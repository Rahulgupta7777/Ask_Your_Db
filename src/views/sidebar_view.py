import streamlit as st

def render_ai_config():
    """
    Renders the AI configuration sidebar and returns the selected model and persona.
    """
    with st.sidebar:
        st.title("⚙️ AI Configuration")
        
        complexity = st.radio(
            "Complexity Level",
            options=["Basic (Fast)", "Advanced (Smart)", "Custom"],
            index=1,
            help="Basic: GPT-3.5 + Strict SQL. Advanced: GPT-4o + Tech Lead. Custom: Choose manually."
        )

        st.divider()

        if complexity == "Basic (Fast)":
            model_name = "gpt-3.5-turbo"
            persona = "concise"
            st.caption("🚀 **Config**: GPT-3.5-Turbo | Strict JSON SQL")
        
        elif complexity == "Advanced (Smart)":
            model_name = "gpt-4o"
            persona = "default"
            st.caption("🧠 **Config**: GPT-4o | Tech Lead (10 yrs exp)")
        
        else: # Custom
            model_name = st.selectbox(
                "Select Model",
                options=["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                index=0
            )
            
            persona = st.selectbox(
                "Select Persona",
                options=["default", "concise", "explanatory"],
                format_func=lambda x: x.capitalize(),
                index=0
            )
        
        st.divider()
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
