import streamlit as st
import re

def render_header():
    st.set_page_config(
        page_title="Ask Your sql database questions",
        layout="wide"
    )
    
    # Client-Side Heartbeat to prevent "Are you still there?" timeouts
    st.markdown("""
        <script>
        function heartbeat() {
            console.log("Heartbeat");
            fetch(window.location.href);
        }
        setInterval(heartbeat, 60000); // Ping every 60 seconds
        </script>
    """, unsafe_allow_html=True)
    
    st.title("Natural Language → SQL Generator")
    st.write("Ask questions in English and query your MySQL database.")

def render_connection_form():
    """
    Renders the database connection form. 
    Returns the config dict if connected/submitted, or None.
    """
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

    if st.button("Connect"):
        if not all([host, user, password, database]):
            st.error("Please fill all required fields.")
            return None
        
        return {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": int(port)
        }
    return None

def render_query_interface():
    """
    Renders the question input and Generate button.
    Returns (question, clicked)
    """
    question = st.text_area(
        "Ask your question:",
        placeholder="e.g. show all students"
    )
    
    clicked = st.button("Generate & Run")
    return question, clicked

def display_sql_and_results(sql, result, error=None, persona="default"):
    """
    Displays the generated SQL and the query results.
    """
    st.subheader("📄 Generated SQL")
    
    # Explanatory mode handling for display
    if persona == "explanatory":
        st.markdown(sql)
    else:
        st.code(sql, language="sql")

    st.subheader("Result")

    if sql.startswith("INVALID_QUERY"):
        st.error(sql)
        return

    if error:
        st.error(error)
        return

    if isinstance(result, str):
        st.error(result)
    elif result is not None:
         st.dataframe(
            result,
            use_container_width=True,
            height=600
        )
