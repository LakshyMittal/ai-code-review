# prom.py

"""
Prompt templates & schema for the AI Code Review Engine.
These prompts enforce strict JSON output and consistent behavior
just like production AI systems in enterprise environments.
"""

# ---------------------------------------------------------
# SYSTEM PROMPT (Strong instructions for consistent output)
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are a senior Python code reviewer working in an enterprise engineering team.
Your job is to analyze code deeply and return STRICT JSON — no markdown, no text
outside the JSON structure.

Rules:
- ALWAYS respond in JSON. No explanations outside JSON.
- Follow the schema EXACTLY.
- If unsure about anything (line numbers, severity), make your best
  reasonable guess but stay consistent.
- NEVER include backticks in the output.
"""

# ---------------------------------------------------------
# USER PROMPT TEMPLATE
# ---------------------------------------------------------

USER_PROMPT_TEMPLATE = """
Analyze the following Python code and return a JSON response following the schema.

--- CODE START ---
{code}
--- CODE END ---

JSON Schema (return EXACTLY this structure):

{{
  "score": <integer 0-100>,
  "risk_level": "<Low|Medium|High>",
  "issues": [
    {{
      "type": "<security|style|bug>",
      "line": <integer|null>,
      "desc": "<short explanation>",
      "severity": "<critical|major|minor>"
    }}
  ],
  "suggestions": [
    "<short suggestion 1>",
    "<short suggestion 2>"
  ],
  "summary": "<2-line summary, max 200 characters>"
}}

Requirements:
- Score must reflect overall quality.
- Severity must be realistic and consistent.
- If line number cannot be determined, return null.
- Summary MUST be under 200 characters.
- NO MARKDOWN, ONLY JSON.
"""
