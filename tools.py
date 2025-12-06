# tools.py

"""
Enterprise-grade LLM tool wrapper for the AI Code Review Engine.
This file:
- Normalizes inputs
- Loads prompts
- Calls the LLM (OpenAI GPT-4.1)
- Ensures STRICT JSON output
- Validates & sanitizes response
"""

import json
import logging
from typing import Dict, Any

from pydantic import BaseModel, ValidationError
from openai import OpenAI

import config
from prom import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# ---------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# ---------------------------------------------------------
# Pydantic Input Schema
# ---------------------------------------------------------

class CodeReviewInput(BaseModel):
    code: str


# ---------------------------------------------------------
# LLM Client Initialization
# ---------------------------------------------------------

client = OpenAI(
    api_key=config.OPENAI_API_KEY,
)


# ---------------------------------------------------------
# Utility: Normalize tool inputs (enterprise pattern)
# ---------------------------------------------------------

def _normalize_inputs(input_data: Any) -> Dict[str, Any]:
    """
    Mimics the structure used in enterprise projects:
    - Accepts str or dict
    - Converts to dict
    - Sanitizes
    """
    if isinstance(input_data, str):
        return {"code": input_data}
    if isinstance(input_data, dict):
        return input_data
    raise ValueError("Invalid input format for CodeReviewTool")


# ---------------------------------------------------------
# Core Tool
# ---------------------------------------------------------

class CodeReviewTool:
    """
    A simplified enterprise-style tool used to:
    - Accept code
    - Send to LLM with prompts
    - Return validated JSON
    """

    name = "code_review_tool"
    description = "Analyzes Python code and returns a structured JSON review."

    @staticmethod
    def run(input_data: Any) -> Dict[str, Any]:
        """
        Entry point (sync). Normalizes input, calls LLM, parses JSON safely.
        """

        # Normalize
        normalized = _normalize_inputs(input_data)

        try:
            validated = CodeReviewInput(**normalized)
        except ValidationError as e:
            return {"error": f"Invalid input: {e}"}

        code = validated.code

        # Build user prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(code=code)

        try:
            # LLM Call
            log.info("Calling GPT-4.1 for code review...")
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
            )

            llm_output = response.choices[0].message.content.strip()

            # Parse JSON safely
            try:
                parsed_json = json.loads(llm_output)
                return parsed_json
            except json.JSONDecodeError:
                log.error("LLM returned invalid JSON")
                return {"error": "LLM returned invalid JSON", "raw_output": llm_output}

        except Exception as e:
            log.error(f"LLM invocation error: {e}")
            return {"error": str(e)}
