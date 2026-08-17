import json
import time
from typing import Dict, Any, List
from agent.prompts import PERCEIVE_PROMPT, REASON_PROMPT, REFLECT_PROMPT
from agent.tools import TOOL_HANDLERS
from agent.harness import ExecutionHarness
from agent.memory_manager import MemoryManager
from agent.logger import AgentLogger

def perceive(input_data: str, previous_reflection: dict, harness: ExecutionHarness) -> dict:
    prompt = PERCEIVE_PROMPT.format(
        input_data=input_data,
        previous_reflection=json.dumps(previous_reflection) if previous_reflection else "{}"
    )
    return harness.call_llm_with_retry(prompt)

def reason(observation: dict, memory: List[dict], harness: ExecutionHarness) -> dict:
    prompt = REASON_PROMPT.format(
        observation=json.dumps(observation),
        memory_context=json.dumps(memory)
    )
    return harness.call_llm_with_retry(prompt)

def act(plan: dict, tools: dict, harness: ExecutionHarness) -> dict:
    action_name = plan.get("action")
    params = plan.get("action_params", {})
    if action_name in tools:
        return harness.execute_tool_safely(tools[action_name], params)
    return {"status": "error", "message": f"Tool {action_name} not found"}

def reflect(result: dict, observation: dict, harness: ExecutionHarness, target_score: float) -> dict:
    prompt = REFLECT_PROMPT.format(
        tool_output=json.dumps(result),
        observation=json.dumps(observation),
        target_score=target_score
    )
    return harness.call_llm_with_retry(prompt)

def run_agentic_loop(
    initial_input: str,
    config: dict,
    harness: ExecutionHarness,
    memory: MemoryManager,
    logger: AgentLogger
) -> dict:
    max_iterations = config["loop"]["max_iterations"]
    target_score = config["loop"]["target_score"]
    
    current_reflection = {}
    best_overall = None
    all_generated_variants = []
    
    for i in range(1, max_iterations + 1):
        print(f"\n==================== Iteration {i}/{max_iterations} ====================")
        
        # 1. PERCEIVE
        t0 = time.time()
        observation = perceive(initial_input, current_reflection, harness)
        logger.log_step(i, "perceive", {"input": initial_input}, observation, (time.time() - t0) * 1000)
        
        # 2. REASON (Memory read context)
        t0 = time.time()
        past_memories = memory.recall(str(observation.get("topic", "")))
        plan = reason(observation, past_memories, harness)
        logger.log_step(i, "reason", {"observation": observation, "memory_count": len(past_memories)}, plan, (time.time() - t0) * 1000)
        
        # 3. ACT (Execute Tool Handler)
        t0 = time.time()
        tool_output = act(plan, TOOL_HANDLERS, harness)
        logger.log_step(i, "act", plan, tool_output, (time.time() - t0) * 1000)
        
        # Print generated headline candidates and individual metrics
        print("\n Candidate Variants Evaluated:")
        tool_results = tool_output.get("results", [])
        if tool_results:
            for item in tool_results:
                headline_text = item.get("headline", "")
                metrics_score = item.get("metrics_score", 0.0)
                char_count = item.get("char_count", 0)
                power_count = item.get("power_words_found", 0)
                all_generated_variants.append(headline_text)
                print(f"  * [{metrics_score}/10] \"{headline_text}\" ({char_count} chars, {power_count} power words)")
        else:
            print("  * No candidates evaluated by tool.")

        # 4. REFLECT (Self-Evaluation and Directive Formulation)
        t0 = time.time()
        reflection = reflect(tool_output, observation, harness, target_score)
        logger.log_step(i, "reflect", tool_output, reflection, (time.time() - t0) * 1000)
        
        # Persist feedback to Memory Layer
        memory.save(
            doc_id=f"iter_{i}_{int(time.time())}",
            text=f"Directive: {reflection.get('next_instruction')}",
            metadata={
                "score": reflection.get("quality_score", 0.0),
                "best": str(reflection.get("best_headline", ""))
            }
        )
        
        current_reflection = reflection
        best_overall = reflection.get("best_headline", best_overall)
        print(f"\n Reflection Quality Score: {reflection.get('quality_score')}/10")
        print(f" Best Pick: '{best_overall}'")
        print(f" Next Directive: {reflection.get('next_instruction')}")
        
        # Guardrail: Stuck check
        if harness.is_stuck(reflection):
            print("\n[HARNESS] Loop detected STUCK condition. Breaking.")
            return {
                "status": "STUCK",
                "best_result": best_overall,
                "all_variants": all_generated_variants,
                "iterations": i
            }
            
        # Guardrail: Target threshold satisfied
        if reflection.get("is_done", False):
            print(f"\n[SUCCESS] Target quality reached at Iteration {i}!")
            return {
                "status": "SUCCESS",
                "best_result": best_overall,
                "all_variants": all_generated_variants,
                "iterations": i
            }
            
    print("\n[PARTIAL] Max iterations reached without satisfying target threshold.")
    return {
        "status": "PARTIAL",
        "best_result": best_overall,
        "all_variants": all_generated_variants,
        "iterations": max_iterations
    }