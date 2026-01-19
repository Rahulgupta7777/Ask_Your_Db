from .roles import get_role_prompt
from .rules import get_rules_prompt
from .outputs import get_output_format_prompt

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
        role_text = get_role_prompt(self.prompt_type)
        
        # 3. Rules Component (Model-Aware)
        rules_text = get_rules_prompt(self.prompt_type, self.model_name)
        
        # 4. Output Contract
        output_contract = get_output_format_prompt(self.prompt_type)
        
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
