def get_output_format_prompt(prompt_type: str) -> str:
    return """
========================
FINAL OUTPUT CONTRACT
========================
Return EXACTLY ONE of:
1. ONLY A VALID SQL STATEMENT ENDING WITH ';'
2. INVALID_QUERY: <specific reason>

DO NOT return conversational text, explanations, or markdown formatting blocks like ```sql.
JUST THE RAW SQL STATEMENT.
"""
