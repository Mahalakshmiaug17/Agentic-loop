import os
import re
import time
import json
import random
from pathlib import Path
from typing import Callable, Any, Dict
from openai import OpenAI
from dotenv import load_dotenv

# Search for .env explicitly from the project root and current working directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

class ExecutionHarness:
    def __init__(self, config: dict):
        self.config = config
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            print("\n" + "=" * 70)
            print("[HARNESS ERROR] OPENROUTER_API_KEY not found in environment or .env file.")
            print(f"Looked at path: {env_path}")
            print("Please set your API key in the .env file or run:")
            print('$env:OPENROUTER_API_KEY="sk-or-v1-YOUR_KEY"')
            print("=" * 70 + "\n")
            raise ValueError("OPENROUTER_API_KEY environment variable missing.")

        self.client = OpenAI(
            base_url=config["llm"].get("base_url", "https://openrouter.ai/api/v1"),
            api_key=api_key.strip()
        )
        self.total_tokens_used = 0
        self.reflection_history = []

    def _clean_json_response(self, text: str) -> str:
        text = text.strip()
        match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text

    def call_llm_with_retry(
        self,
        prompt: str,
        system_prompt: str = "You are a specialized JSON-only assistant. Always respond with pure valid JSON."
    ) -> Dict[str, Any]:
        max_retries = self.config["harness"].get("max_retries", 3)
        delay = self.config["harness"].get("initial_delay", 1.0)
        backoff = self.config["harness"].get("backoff_factor", 2.0)
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config["llm"]["model"],
                    temperature=self.config["llm"]["temperature"],
                    response_format={"type": "json_object"},
                    extra_headers={
                        "HTTP-Referer": "https://github.com/agentic-loop",
                        "X-Title": "Agentic Headline Optimizer"
                    },
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    timeout=self.config["llm"].get("timeout", 25)
                )
                
                if response.usage:
                    self.total_tokens_used += response.usage.total_tokens
                    if self.total_tokens_used > self.config["loop"].get("token_budget", 50000):
                        print(f"[HARNESS WARN] Token budget exceeded: {self.total_tokens_used}")

                raw_content = response.choices[0].message.content or "{}"
                cleaned = self._clean_json_response(raw_content)
                return json.loads(cleaned)

            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"[HARNESS] Fallback triggered on attempt {max_retries}: {str(e)}")
                    return {"error": "LLM_CALL_FAILED", "raw_exception": str(e)}
                
                jitter = random.uniform(0.1, 0.5) if self.config["harness"].get("jitter", True) else 0
                sleep_time = (delay * (backoff ** attempt)) + jitter
                print(f"[HARNESS] Retrying in {round(sleep_time, 2)}s due to error: {str(e)}")
                time.sleep(sleep_time)

    def execute_tool_safely(self, tool_func: Callable, params: dict) -> dict:
        try:
            return tool_func(**params)
        except Exception as e:
            return {"status": "error", "error_message": f"Tool execution failed: {str(e)}"}

    def is_stuck(self, reflection: dict) -> bool:
        instruction = reflection.get("next_instruction", "")
        if not isinstance(instruction, str) or not instruction.strip():
            return False
        
        instruction_clean = instruction.strip().lower()
        self.reflection_history.append(instruction_clean)
        
        if len(self.reflection_history) >= 2:
            if self.reflection_history[-1] == self.reflection_history[-2]:
                return True
        return False