import streamlit as st
import yaml
import time
from agent.harness import ExecutionHarness
from agent.memory_manager import MemoryManager
from agent.logger import AgentLogger
from agent.tools import TOOL_HANDLERS
from agent.loop import perceive, reason, act, reflect

st.set_page_config(page_title="Headline Variance Agent", page_icon="⚡", layout="wide")

@st.cache_resource
def init_agent():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    harness = ExecutionHarness(config)
    memory = MemoryManager(
        persist_dir=config["memory"]["persist_directory"],
        collection_name=config["memory"]["collection_name"]
    )
    logger = AgentLogger()
    return config, harness, memory, logger

config, harness, memory, logger = init_agent()

st.title("⚡ Autonomous Headline Optimizer")
st.caption("Agentic cognitive loop: Perceive → Reason → Act → Reflect")

# Input Form
with st.form("headline_form"):
    topic_input = st.text_input(
        "Enter Topic / Initial Title:",
        placeholder="e.g. 7 Simple Tips for Better Sleep"
    )
    constraints_input = st.text_input(
        "Constraints (Length, Tone, Keywords, Platform):",
        placeholder="e.g. Under 60 characters, punchy tone, include power words, Blog Post"
    )
    submitted = st.form_submit_button("Generate & Optimize Headlines")

if submitted and topic_input:
    full_input = f"Topic: {topic_input}. Constraints: {constraints_input}"
    
    max_iterations = config["loop"]["max_iterations"]
    target_score = config["loop"]["target_score"]
    
    current_reflection = {}
    best_overall = None
    all_iterations_data = []

    progress_bar = st.progress(0)
    status_box = st.empty()

    for i in range(1, max_iterations + 1):
        status_box.info(f"Running Iteration {i}/{max_iterations}...")
        
        # 1. Perceive
        t0 = time.time()
        obs = perceive(full_input, current_reflection, harness)
        logger.log_step(i, "perceive", {"input": full_input}, obs, (time.time() - t0) * 1000)
        
        # 2. Reason (Memory read)
        t0 = time.time()
        memories = memory.recall(str(obs.get("topic", "")))
        plan = reason(obs, memories, harness)
        logger.log_step(i, "reason", {"obs": obs}, plan, (time.time() - t0) * 1000)
        
        # 3. Act
        t0 = time.time()
        tool_out = act(plan, TOOL_HANDLERS, harness)
        logger.log_step(i, "act", plan, tool_out, (time.time() - t0) * 1000)
        
        # 4. Reflect (Memory write)
        t0 = time.time()
        reflection = reflect(tool_out, obs, harness, target_score)
        logger.log_step(i, "reflect", tool_out, reflection, (time.time() - t0) * 1000)
        
        memory.save(
            doc_id=f"iter_{i}_{int(time.time())}",
            text=f"Directive: {reflection.get('next_instruction')}",
            metadata={"score": reflection.get("quality_score", 0.0), "best": str(reflection.get("best_headline", ""))}
        )
        
        current_reflection = reflection
        best_overall = reflection.get("best_headline", best_overall)
        
        # Render Iteration Results in real time
        with st.expander(f"Iteration {i} — Score: {reflection.get('quality_score', 0)}/10", expanded=(i == 1)):
            st.markdown(f"**Strategy Focus:** {plan.get('thought', 'N/A')}")
            
            tool_results = tool_out.get("results", [])
            if tool_results:
                cols = st.columns(len(tool_results))
                for idx, item in enumerate(tool_results):
                    with cols[idx]:
                        st.metric(
                            label=f"Variant {idx+1}",
                            value=f"{item.get('metrics_score', 0)}/10",
                            delta=f"{item.get('char_count')} chars"
                        )
                        st.write(f"**\"{item.get('headline')}\"**")
                        st.caption(f"Power words: {item.get('power_words_found')}")
            
            st.info(f"**Agent Feedback for Next Turn:** {reflection.get('next_instruction')}")
            
        progress_bar.progress(i / max_iterations)
        
        if harness.is_stuck(reflection) or reflection.get("is_done", False):
            break

    status_box.empty()
    progress_bar.progress(1.0)
    
    # Final Verdict Card
    st.success("### 🏆 Best Recommended Title")
    st.subheader(f"\"{best_overall}\"")
    st.balloons()