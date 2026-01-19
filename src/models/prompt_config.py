class SystemPromptBuilder:
    """
    Builder class for constructing the system prompt dynamically based on 
    schema, persona, and model context.
    """
    
    def __init__(self, schema: dict, prompt_type: str = "default", model_name: str = "gpt-4o"):
        self.schema = schema
        self.prompt_type = prompt_type
        self.model_name = model_name

    def build(self) -> str:
        """
        Constructs and returns the full system prompt string.
        """
        # 1. Schema Component
        schema_text = self._build_schema_section()
        
        # 2. Role Component
        role_text = self._get_role()
        
        # 3. Rules Component (Model-Aware)
        rules_text = self._get_rules()
        
        # 4. Output Contract
        output_contract = self._get_output_format()
        
        # Assembly
        full_prompt = f"""
{role_text}

{schema_text}

{rules_text}

{output_contract}
"""
        return full_prompt.strip()

    def _build_schema_section(self) -> str:
        ddl_text = ""
        for table, columns in self.schema.items():
            ddl_text += f"CREATE TABLE {table} (\n"
            for col in columns:
                ddl_text += f"  {col},\n"
            ddl_text = ddl_text.rstrip(",\n") + "\n);\n\n"

        return f"""
========================
DATABASE SCHEMA (SOURCE OF TRUTH)
========================
The schema below is the ONLY source of truth.
You MUST NOT assume anything beyond it.

{ddl_text}
"""

    def _get_role(self) -> str:
        if self.prompt_type == "concise":
            return """
You are a strict SQL compiler. You receive natural language and output ONLY SQL.
You have zero tolerance for ambiguity.
"""
        elif self.prompt_type == "explanatory":
            return """
You are a helpful Senior Database Engineer and Educator.
Your goal is to not only generate the correct SQL but also EXPLAIN your thought process
and how the query works, so the user can learn.
"""
        else: # default / tech_lead
            return """
You are the Chief Data Officer (CDO) at Google, based in Mountain View, California, 
with over 10 years of world-class experience in distributed systems, SQL optimization, 
and database architecture.

Your role is to translate natural language requests—no matter how informal, vague, 
or grammatically incorrect—into **safe, accurate, optimized, ANSI-compliant SQL**.
"""

    def _get_rules(self) -> str:
        base_rules = """
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
"""

        strict_query_rules = """
========================
STRICT QUERY CONSTRUCTION RULES
========================
1. NEVER use SELECT *
2. Always list columns explicitly
3. Use explicit JOIN syntax only
4. NEVER use UNION unless explicitly requested
5. Prefer LIMIT for top/first requests
"""

        # Model-Specific Optimizations
        model_notes = ""
        if "gpt-3.5" in self.model_name:
            model_notes = """
========================
MODEL SPECIFIC ATTENTION
========================
- You are running on a lighter model. PAY EXTRA ATTENTION to JOIN conditions.
- Do not hallucinate columns. Double check the schema above.
"""

        if self.prompt_type == "concise":
            return f"{base_rules}\n\n{model_notes}"
        
        return f"{base_rules}\n\n{strict_query_rules}\n\n{model_notes}"

    def _get_output_format(self) -> str:
        if self.prompt_type == "concise":
            return """
RETURN ONLY THE RAW SQL. NO MARKDOWN. NO EXPLANATIONS.
If the query is invalid, return: INVALID_QUERY: <reason>
"""
        elif self.prompt_type == "explanatory":
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

