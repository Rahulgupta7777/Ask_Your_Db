import streamlit as st

def render_ai_config():
    """
    Renders the configuration sidebar and returns the fixed model and persona.
    """
    with st.sidebar:
        st.title("Showing")
        st.info("write SQL queries for me")
        
        model_name = "gpt-4o"
        persona = "elite_analyst"
        
        return model_name, persona

def render_schema_viewer(schema):
    """
    Renders the schema viewer in the sidebar.
    """
    with st.sidebar:
        st.header("Database Schema")
        if isinstance(schema, str):
            if "please seed some data" in schema.lower():
                st.warning("Please seed some data. The database is empty.")
            else:
                st.error(schema)
        else:
            for table, cols in schema.items():
                with st.expander(table):
                    for c in cols:
                        st.text(c)
            st.success("Connected successfully!")
