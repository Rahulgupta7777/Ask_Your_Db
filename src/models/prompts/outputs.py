def get_output_format_prompt(prompt_type: str) -> str:
    if prompt_type == "concise":
        return """
RETURN ONLY THE RAW SQL. NO MARKDOWN. NO EXPLANATIONS.
If the query is invalid, return: INVALID_QUERY: <reason>
"""
    elif prompt_type == "explanatory":
        return """
FORMATTING:
1. First, provide the SQL query in a markdown block.
2. Then, provide a bulleted explanation of the logic, joins, and filters used.
3. If there are performance considerations (e.g. missing indexes), mention them.

If the query is invalid, explain politely why and suggest alternatives.
"""
    else: # default
        return """
========================
FINAL OUTPUT CONTRACT
========================
Return EXACTLY ONE of:
1. A single valid SQL statement ending with ';'
2. INVALID_QUERY: <specific reason>

DO NOT return comments, explanations, or markdown.
"""
