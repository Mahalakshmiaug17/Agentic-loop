PERCEIVE_PROMPT = """
You are an expert content strategist parsing a headline variance request.
Raw Input: {input_data}
Previous Reflection: {previous_reflection}

Extract and return a JSON object with:
- topic: string
- constraints: object with target_char_limit, tone, required_keywords, platform
- focus_directive: specific adjustments needed based on the previous reflection
"""

REASON_PROMPT = """
You are an autonomous agent optimizing headline variations.
Observation & Constraints: {observation}
Past Lessons / Memory Context: {memory_context}

Available Tools:
1. analyze_headline_metrics: Evaluates character length, word count, and power words for a list of candidate headlines.
2. check_seo_keyword_fit: Evaluates keyword presence and front-loading for a specific headline.

Generate candidate headline variations testing distinct angles (e.g., curiosity gap, pain-point, how-to) and select an action to verify them.

Return ONLY a JSON object:
{{
  "thought": "Your reasoning trace for this iteration",
  "action": "analyze_headline_metrics",
  "action_params": {{
    "headlines": ["Variant 1", "Variant 2", "Variant 3"]
  }}
}}
"""

REFLECT_PROMPT = """
Evaluate the tool results against the user constraints.
Tool Execution Result: {tool_output}
Observation: {observation}
Target Quality Threshold: {target_score}

Determine:
1. quality_score: Numeric score between 0.0 and 10.0
2. is_done: true if at least one headline achieves >= {target_score} and meets all constraints; otherwise false
3. next_instruction: Actionable, specific feedback for the next iteration if not done
4. best_headline: The top performing headline so far

Return ONLY a JSON object:
{{
  "quality_score": float,
  "is_done": boolean,
  "next_instruction": "string",
  "best_headline": "string"
}}
"""