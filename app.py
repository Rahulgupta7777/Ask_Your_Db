import streamlit as st
from sql_generator import SQLQueryGenerator
from db_executor import DatabaseExecutor
from prompt_config import build_system_prompt
import mysql.connector
from mysql.connector import Error
import socket
import ipaddress


st.set_page_config(
    page_title="Ask Your sql database questions",
    layout="wide"
)

st.title("Natural Language → SQL Generator")
st.write("Ask questions in English and query your MySQL database.")



host = st.text_input(
    label="Please provide your database host",
    placeholder="Enter database host"
)

user = st.text_input(
    label="Please provide your database user",
    placeholder="Enter database user"
)

password = st.text_input(
    label="Please provide your database password",
    type="password",
    placeholder="Enter password"
)

database = st.text_input(
    label="Please provide your database name",
    placeholder="Enter database name"
)

port = st.number_input(
    label="Please provide your database port",
    value=3306,
    step=1
)



def is_local_or_private(host_addr):
    """
    Checks if a hostname or IP is loopback or private.
    Returns (True/False, "Reason")
    """
    try:
        ip_str = socket.gethostbyname(host_addr)
        ip = ipaddress.ip_address(ip_str)

        if ip.is_loopback:
            return True, f"'{host_addr}' resolves to loopback ({ip_str})."
        if ip.is_private:
            return True, f"'{host_addr}' resolves to private IP ({ip_str})."
        
        return False, None
    except Exception:
        return False, None

if st.button("Connect"):
    if not all([host, user, password, database]):
        st.error("Please fill all required fields.")
    else:
        is_private, reason = is_local_or_private(host)
        if is_private:
            st.warning(
                f"⚠️ Cloud Warning: You are using a local/private host ({reason}).\n\n"
            )
        
        st.session_state.db_config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": int(port)
        }
        st.success("Database configuration saved.")



# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ AI Configuration")
    
    model_name = st.selectbox(
        "Select Model",
        options=["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0,
        help="Select the OpenAI model to use for SQL generation."
    )
    
    persona = st.selectbox(
        "Select Persona",
        options=["default", "concise", "explanatory"],
        format_func=lambda x: x.capitalize(),
        index=0,
        help="Choose the AI's behavior: Tech Lead (Default), Strict SQL, or Explanatory."
    )
    
    st.divider()

if "db_config" in st.session_state:
    sql_gen = SQLQueryGenerator()
    db = DatabaseExecutor(st.session_state.db_config)

    try:
        schema = db.get_schema()
        # Pass the selected persona to build_system_prompt
        system_prompt = build_system_prompt(schema, prompt_type=persona)

        with st.sidebar:
            st.header("Database Schema")
            for table, cols in schema.items():
                with st.expander(table):
                    for c in cols:
                        st.text(c)
            st.success("Connected successfully!")

    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        # Allow retry by clearing config if connection drifts
        if st.button("Reset Connection"):
            del st.session_state.db_config
            st.rerun()


question = st.text_area(
    "Ask your question:",
    placeholder="e.g. show all students"
)


if st.button("Generate & Run"):
    if "db_config" not in st.session_state:
        st.error("Please connect to the database first.")

    elif not question.strip():
        st.warning("Please enter a question.")

    else:
        with st.spinner(f"Generating SQL using {model_name}..."):
            # Pass model_name to generate_sql
            sql = sql_gen.generate_sql(question, system_prompt, model_name)

        st.subheader("📄 Generated SQL")
        if persona == "explanatory":
             st.markdown(sql) # Render markdown for explanatory mode
        else:
             st.code(sql, language="sql")

        st.subheader("Result")


        if sql.startswith("INVALID_QUERY"):
            st.error(sql)

        elif persona != "explanatory": # In explanatory mode, we might not want to execute automatically if it's just text, or we extract the SQL. 
             # For simplicity in this iteration, if explanatory mode returns a block, we might fail execution:
             # The instructions said "First, provide the SQL query in a markdown block". 
             # Parsing that out cleanly is tricky without regex. 
             # For now, let's only execute if it looks like raw SQL or if we add a parser.
             # Given the "explanatory" prompt format, it returns markdown.
             # The existing code expects RAW SQL.
             # If persona is explanatory, we might skip auto-execution or try to find the code block.
             
            with st.spinner("Executing query..."):
                # Basic safety check: if it's a markdown block, try to extract sql
                if "```sql" in sql:
                     import re
                     match = re.search(r"```sql\n(.*?)\n```", sql, re.DOTALL)
                     if match:
                         clean_sql = match.group(1)
                         result = db.execute_query(clean_sql)
                         show_result(result)
                     else:
                         st.info("Query generated in explanatory mode. Please review the explanation above.")
                else:
                    # Attempt execution if it looks like a query (and not just text)
                    if sql.strip().upper().startswith(("SELECT", "WITH", "SHOW", "DESCRIBE")):
                        result = db.execute_query(sql)
                        show_result(result)
                    else:
                         st.info("Output is not a raw SQL query (Explanatory Mode).")

def show_result(result):
    if isinstance(result, str):
        st.error(result)
    else:
        st.dataframe(
            result,
            use_container_width=True,
            height=600
        )
