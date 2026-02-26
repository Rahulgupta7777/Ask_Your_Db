import streamlit as st
import re
from src.models.sql_generator import SQLQueryGenerator
from src.models.db_executor import DatabaseExecutor
from src.models.utils import is_local_or_private
from src.views import home_view, sidebar_view

def run():
    home_view.render_header()
    model_name, persona = sidebar_view.render_ai_config()
    
    app_mode = st.radio("Select Input Source:", ["Live Database", "Manual Schema (Copy-Paste)"])

    if app_mode == "Manual Schema (Copy-Paste)":
        _handle_manual_mode(model_name, persona)
    else:
        if "db_config" not in st.session_state:
            config = home_view.render_connection_form()
            if config:
                st.session_state.db_config = config
                st.rerun()
        else:
            _handle_connected_state(model_name, persona)

def _handle_manual_mode(model_name, persona):
    schema_text = st.text_area("Paste your Table Schema", height=300)
    question, clicked = home_view.render_query_interface()

    if clicked and schema_text:
        sql_gen = SQLQueryGenerator()
        system_prompt = f"You are a Senior Data Analyst at Google. Use this schema context: {schema_text}. Persona: {persona}\\nOutput strictly raw SQL without markdown or conversational text."
        
        with st.spinner("Generating SQL..."):
            sql = sql_gen.generate_sql(question, system_prompt, model_name)
            home_view.display_sql_and_results(sql, None, None, persona)
            
def _handle_connected_state(model_name, persona):
    db_config = st.session_state.db_config
    
    sql_gen = SQLQueryGenerator()
    db = DatabaseExecutor(config=db_config, db_url=db_config.get("db_url", None))
    
    try:
        schema = db.get_schema()
        sidebar_view.render_schema_viewer(schema)
        
        if isinstance(schema, str) and "please seed some data" in schema.lower():
             system_prompt = ""
        else:
             from src.models.prompts.builder import SystemPromptBuilder
             system_prompt = SystemPromptBuilder(
                 schema=schema, 
                 prompt_type=persona, 
                 model_name=model_name
             ).build()
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        if st.button("Reset Connection"):
            del st.session_state.db_config
            st.rerun()
        return

    question, clicked = home_view.render_query_interface()
    
    if clicked:
        if not question.strip():
            st.warning("Please enter a question.")
            return

        with st.spinner(f"Generating SQL using {model_name}..."):
            sql = sql_gen.generate_sql(question, system_prompt, model_name)
        
        result = None
        error = None
        should_execute = True

        if sql.startswith("INVALID_QUERY"):
            should_execute = False
        
        if should_execute and system_prompt != "":
             with st.spinner("Executing query..."):
                final_sql_for_exec = sql.replace("```sql", "").replace("```", "").strip()
                result = db.execute_query(final_sql_for_exec)
        elif system_prompt == "":
             result = "Please seed some data"
             error = "The database schema is empty."

        home_view.display_sql_and_results(sql, result, error, persona)
