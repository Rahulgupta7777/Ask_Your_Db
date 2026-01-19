import streamlit as st

def render_ai_config():
    """
    Renders the AI configuration sidebar and returns the selected model and persona.
    """
    with st.sidebar:
        st.title("⚙️ AI Configuration")
        
        complexity = st.radio(
            "Complexity Level",
            options=["Basic (Fast)", "Advanced (Smart)"],
            index=1,
            help="Basic: Fast execution. Advanced: More intelligent reasoning."
        )

        st.divider()

        if complexity == "Basic (Fast)":
            model_name = "gpt-3.5-turbo"
            persona = "concise"
        
        else: # Advanced (Smart)
            model_name = "gpt-4o"
            persona = "default"
        
        return model_name, persona

def render_schema_viewer(schema):
    """
    Renders the schema viewer in the sidebar.
    """
    with st.sidebar:
        st.header("Database Schema")
        for table, cols in schema.items():
            with st.expander(table):
                for c in cols:
                    st.text(c)
        st.success("Connected successfully!")
