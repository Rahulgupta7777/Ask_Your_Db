import streamlit as st
import re
from src.models.sql_generator import SQLQueryGenerator
from src.models.db_executor import DatabaseExecutor
from src.models.prompt_config import SystemPromptBuilder
from src.models.utils import is_local_or_private
from src.views import home_view, sidebar_view

def run():
    # 1. Render Header
    home_view.render_header()
    
    # 2. Render Sidebar & Get AI Config
    model_name, persona = sidebar_view.render_ai_config()
    
    # 3. Handle Connection State
    if "db_config" not in st.session_state:
        # Show connection form if not connected
        config = home_view.render_connection_form()
        if config:
            # Check for private IP warning
            is_private, reason = is_local_or_private(config["host"])
            if is_private:
                st.warning(f"⚠️ Cloud Warning: You are using a local/private host ({reason}).")
            
            st.session_state.db_config = config
            st.success("Database configuration saved.")
            st.rerun() # Rerun to show the main interface
    else:
        # Connected State
        _handle_connected_state(model_name, persona)

def _handle_connected_state(model_name, persona):
    db_config = st.session_state.db_config
    
    # Initialize Models
    sql_gen = SQLQueryGenerator()
    db = DatabaseExecutor(db_config)
    
    # Render Schema in Sidebar
    try:
        schema = db.get_schema()
        sidebar_view.render_schema_viewer(schema)
        # Pre-build prompt
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

    # Render Main Query Interface
    question, clicked = home_view.render_query_interface()
    
    if clicked:
        if not question.strip():
            st.warning("Please enter a question.")
            return

        with st.spinner(f"Generating SQL using {model_name}..."):
            sql = sql_gen.generate_sql(question, system_prompt, model_name)
        
        # Execute Logic
        result = None
        error = None
        
        # logic for handling explanatory mode execution
        final_sql_for_exec = sql
        should_execute = True

        if persona == "explanatory":
            if "```sql" in sql:
                 match = re.search(r"```sql\n(.*?)\n```", sql, re.DOTALL)
                 if match:
                     final_sql_for_exec = match.group(1)
                 else:
                     should_execute = False
            else:
                 should_execute = False # Just text explanation

        if sql.startswith("INVALID_QUERY"):
            should_execute = False
        
        if should_execute:
             with st.spinner("Executing query..."):
                # Clean up sql just in case it has markdown ticks and wasnt caught by explanatory regex
                if "```" in final_sql_for_exec:
                     final_sql_for_exec = final_sql_for_exec.replace("```sql", "").replace("```", "").strip()
                
                # Check for read-only safety again (redundant but safe)
                if not final_sql_for_exec.strip().upper().startswith(("SELECT", "WITH", "SHOW", "DESCRIBE")):
                     error = "Query execution skipped for safety (Non-SELECT statement)."
                else:
                     result = db.execute_query(final_sql_for_exec)
        else:
             if not sql.startswith("INVALID_QUERY") and persona == "explanatory":
                 # Just an info message, not an error
                 st.info("Query generated in explanatory mode. Please review the explanation above.")

        # Display results via View
        home_view.display_sql_and_results(sql, result, error, persona)
