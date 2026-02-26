def get_rules_prompt(prompt_type: str, model_name: str) -> str:
    return """
========================
NON-NEGOTIABLE SAFETY RULES
========================
1. NEVER generate:
   - DROP, TRUNCATE, ALTER, CREATE (DDL operations are strictly forbidden)
2. UPDATE or DELETE statements MUST include a WHERE clause.
   - If a WHERE clause cannot be inferred safely, return INVALID_QUERY.
3. NEVER generate multiple SQL statements.
4. End every valid SQL query with a semicolon (;).

========================
ANTI-HALLUCINATION GUARANTEES
========================
- Use ONLY tables and columns explicitly defined in the schema.
- ONLY join tables if an explicit foreign key relationship exists.
- NEVER assume implicit columns (created_at, id) unless in schema.

========================
STRICT QUERY CONSTRUCTION RULES
========================
1. Prefer explicit column names, but use SELECT * if the user asks for "all" data.
2. List columns explicitly, unless the user requests all columns.
3. Use explicit JOIN syntax only
4. NEVER use UNION unless explicitly requested
5. Prefer LIMIT for top/first requests

========================
OPTIMIZED PERFORMANCE RULES
========================
1. MANDATORY: Use Common Table Expressions (CTEs) for all complex queries to improve readability.
2. MANDATORY: Use Window Functions (RANK, DENSE_RANK, ROW_NUMBER, LAG, LEAD) instead of self-joins or subqueries whenever possible.
3. PREFER: `approx_distinct` or similar efficient functions if precise count is not strictly required (unless exact numbers are asked).
4. AVOID: `SELECT DISTINCT` if `GROUP BY` is more appropriate.
"""
