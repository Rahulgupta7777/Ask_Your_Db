import streamlit as st
from sql_generator import SQLQueryGenerator
from db_executor import DatabaseExecutor
from prompt_config import build_system_prompt
import mysql.connector
from mysql.connector import Error
import socket
import ipaddress

st.set_page_config(
    page_title="NL → SQL Generator",
    layout="wide"
)

st.title("Natural Language → SQL Generator")
st.write("Ask questions in English and query your MySQL database.")



host = st.text_input(
    label="Please provide your database host",
    placeholder="localhost"
)

user = st.text_input(
    label="Please provide your database user",
    placeholder="root"
)

password = st.text_input(
    label="Please provide your database password",
    type="password",
    placeholder="Enter password"
)

database = st.text_input(
    label="Please provide your database name",
    placeholder="universit"
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


if "db_config" in st.session_state:
    sql_gen = SQLQueryGenerator()
    db = DatabaseExecutor(st.session_state.db_config)

    try:
        schema = db.get_schema()
        system_prompt = build_system_prompt(schema)

        with st.sidebar:
            st.header("Database Schema")
            for table, cols in schema.items():
                with st.expander(table):
                    for c in cols:
                        st.text(c)
            st.success("Connected successfully!")

    except Exception as e:
        st.error(f"Failed to connect to database: {e}")


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
        with st.spinner("Generating SQL..."):
            sql = sql_gen.generate_sql(question, system_prompt)

        st.subheader("📄 Generated SQL")
        st.code(sql, language="sql")

        st.subheader("Result")


        if sql.startswith("INVALID_QUERY"):
            st.error(sql)

        else:
            with st.spinner("Executing query..."):
                result = db.execute_query(sql)

            if isinstance(result, str):
                st.error(result)
            else:
                st.dataframe(
                    result,
                    use_container_width=True,
                    height=5000
                )
