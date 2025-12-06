# review_engine.py
import json
from typing import Dict, Any
from openai import OpenAI
import config

# Initialize OpenAI client
client = OpenAI(api_key=config.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are an AI Code Reviewer. You MUST return ONLY a valid JSON object.
STRICT REQUIREMENTS:
- "strengths" MUST be a non-empty list of strings.
- "flaws" MUST be a list of objects (can be empty, but must exist).
- Each flaw MUST contain: issue, line, severity.
- Always include: score, risk_level, strengths, flaws, summary, meta.
- NO markdown, NO commentary, ONLY JSON.

MANDATORY JSON FORMAT:

{
  "score": 0-100,
  "risk_level": "Low" | "Medium" | "High",
  "strengths": ["point 1", "point 2"],
  "flaws": [
    {
      "issue": "some problem",
      "line": 12,
      "severity": "LOW" | "MEDIUM" | "HIGH"
    }
  ],
  "summary": "Short summary.",
  "meta": {
    "name": "",
    "project": ""
  }
}

If there are no flaws, return: "flaws": []
If code is excellent, still give at least 1 strength.
"""

def fix_json(text: str) -> str:
    """Fix and extract valid JSON returned by the LLM."""
    text = text.strip().replace("```json", "").replace("```", "").strip()

    try:
        json.loads(text)
        return text
    except:
        pass

    # Try extracting JSON between first "{" and last "}"
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        extracted = text[start:end]
        json.loads(extracted)
        return extracted
    except:
        raise ValueError("Invalid JSON from LLM:\n" + text)


def review_code(code: str) -> Dict[str, Any]:
    """Send code to GPT-4o-mini and return structured JSON."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Review this code:\n\n{code}"}
            ],
            temperature=0.2,
        )

        raw = response.choices[0].message.content
        fixed_json = fix_json(raw)
        data = json.loads(fixed_json)

        # 🔥 Guarantee mandatory fields exist so PDF never breaks
        data.setdefault("strengths", ["No strengths detected — reviewer fallback"])
        data.setdefault("flaws", [])
        data.setdefault("summary", "No summary provided.")
        data.setdefault("score", 80)
        data.setdefault("risk_level", "Medium")
        data.setdefault("meta", {})

        return data

    except Exception as e:
        return {
            "error": str(e),
            "message": "LLM request failed. Check your API key or network."
        }
