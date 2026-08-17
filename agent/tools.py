import re
from typing import Dict, Any, List

TOOL_DEFINITIONS = [
    {
        "name": "analyze_headline_metrics",
        "description": "Calculates character length, word count, power word presence, and metric score for headlines.",
        "parameters": {
            "type": "object",
            "properties": {
                "headlines": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of candidate headline strings to evaluate."
                }
            },
            "required": ["headlines"]
        }
    },
    {
        "name": "check_seo_keyword_fit",
        "description": "Checks if required keywords are present and front-loaded in the headline.",
        "parameters": {
            "type": "object",
            "properties": {
                "headline": {"type": "string", "description": "The headline to evaluate."},
                "target_keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords that must be present."
                }
            },
            "required": ["headline", "target_keywords"]
        }
    }
]

POWER_WORDS = {
    "ultimate", "proven", "secret", "hack", "master", "guide",
    "insane", "fast", "simple", "mistakes", "effortless", "critical"
}

def analyze_headline_metrics(headlines: List[str]) -> Dict[str, Any]:
    results = []
    for h in headlines:
        words = re.findall(r"\w+", h.lower())
        char_len = len(h)
        power_count = sum(1 for w in words if w in POWER_WORDS)
        
        # Scoring: Length optimal between 40-65 chars, bonus for power words
        length_score = 10.0 if 40 <= char_len <= 65 else (6.0 if char_len < 40 else 4.0)
        power_score = min(10.0, power_count * 5.0)
        aggregate_score = round((length_score * 0.6) + (power_score * 0.4), 2)
        
        results.append({
            "headline": h,
            "char_count": char_len,
            "word_count": len(words),
            "power_words_found": power_count,
            "metrics_score": aggregate_score
        })
    return {"status": "success", "results": results}

def check_seo_keyword_fit(headline: str, target_keywords: List[str]) -> Dict[str, Any]:
    h_lower = headline.lower()
    matched = [kw for kw in target_keywords if kw.lower() in h_lower]
    front_loaded = any(h_lower.startswith(kw.lower()) for kw in matched)
    
    seo_score = (len(matched) / max(1, len(target_keywords))) * 10.0
    if front_loaded:
        seo_score = min(10.0, seo_score + 2.0)
        
    return {
        "status": "success",
        "headline": headline,
        "matched_keywords": matched,
        "front_loaded": front_loaded,
        "seo_score": round(seo_score, 2)
    }

TOOL_HANDLERS = {
    "analyze_headline_metrics": analyze_headline_metrics,
    "check_seo_keyword_fit": check_seo_keyword_fit
}