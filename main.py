import yaml
from agent.harness import ExecutionHarness
from agent.memory_manager import MemoryManager
from agent.logger import AgentLogger
from agent.loop import run_agentic_loop

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()
    
    harness = ExecutionHarness(config)
    memory = MemoryManager(
        persist_dir=config["memory"]["persist_directory"],
        collection_name=config["memory"]["collection_name"]
    )
    logger = AgentLogger()
    
    test_input = (
        "Topic: How to Build an AI Agent in Python from Scratch. "
        "Constraints: Must stay strictly between 45 and 65 characters, tone must be authoritative and actionable, "
        "must include at least one power word (e.g., master, proven, ultimate, guide), platform: Medium / Tech Blog."
    )
    
    print("Executing Agentic Headline Variance Loop...")
    result = run_agentic_loop(test_input, config, harness, memory, logger)
    print("\nFinal Result Summary:", result)