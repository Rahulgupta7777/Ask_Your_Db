import streamlit as st
from urllib.parse import urlparse, parse_qs


def render_header():
    st.set_page_config(
        page_title="Ask Your SQL Database",
        layout="wide",
        page_icon="🤖",
    )

    # Client-Side Heartbeat to prevent "Are you still there?" timeouts
    # Plus custom styling
    st.markdown(
        """
        <style>
        /* Modern Glassmorphism Aesthetic */
        .stButton>button {
            background-color: #00d2ff;
            background-image: linear-gradient(to right, #00d2ff 0%, #3a7bd5 51%, #00d2ff 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 16px;
            transition: all 0.3s ease 0s;
        }
        .stButton>button:hover {
            background-position: right center;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4);
        }
        h1, h2, h3 {
            background: -webkit-linear-gradient(#fff, #a1c4fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        </style>
        <script>
        function heartbeat() {
            console.log("Heartbeat");
            fetch(window.location.href);
        }
        setInterval(heartbeat, 60000); // Ping every 60 seconds
        </script>
        """,
        unsafe_allow_html=True,
    )

    st.title("Natural Language → SQL Generator")
    st.write("Generate complex SQL queries and analyze your data seamlessly using natural language.")


def render_connection_form():
    """
    Renders the database connection form.
    Returns the config dict if connected/submitted, or None.
    """
    st.subheader("Database Connection")

    db_url = st.text_input(
        label="Database URL (Recommended)",
        placeholder="mysql://user:pass@host:port/db OR postgresql://user:pass@host:port/db",
        help="Paste a standard database connection string (Supabase, Aiven, AWS, etc.).",
    )

    # Defaults (used for manual fields, possibly auto-filled from URL)
    d_host, d_user, d_pass, d_db, d_port = "", "", "", "", 3306
    d_ssl = False

    st.markdown("--- OR ---")

    if db_url:
        try:
            parse_url = db_url if "://" in db_url else f"mysql://{db_url}"
            parsed = urlparse(parse_url)

            if parsed.hostname:
                d_host = parsed.hostname
            if parsed.username:
                d_user = parsed.username
            if parsed.password:
                d_pass = parsed.password
            if parsed.path:
                d_db = parsed.path.lstrip("/")
            if parsed.port:
                d_port = parsed.port

            # Parse query params for ssl-mode, ssl flags
            if parsed.query:
                qs = parse_qs(parsed.query)

                if "ssl-mode" in qs:
                    mode = qs["ssl-mode"][0].upper()
                    if mode in ["REQUIRED", "VERIFY_CA", "VERIFY_IDENTITY"]:
                        d_ssl = True

                if "ssl" in qs:
                    d_ssl = True

        except Exception:
            st.warning("Could not auto-parse the provided URL. Please fill fields manually.")

    host = st.text_input(
        label="Host",
        value=d_host,
        placeholder="e.g. localhost",
    )
    user = st.text_input(
        label="User",
        value=d_user,
        placeholder="e.g. root",
    )
    password = st.text_input(
        label="Password",
        type="password",
        value=d_pass,
        placeholder="Enter password",
    )
    database = st.text_input(
        label="Database Name",
        value=d_db,
        placeholder="e.g. my_database",
    )
    port = st.number_input(
        label="Port",
        value=int(d_port),
        step=1,
    )
    ssl_enabled = st.checkbox(
        label="Enable SSL (Required for some cloud providers like Aiven, Azure)",
        value=d_ssl,
        help="Check this if your database requires an SSL connection (e.g. ssl-mode=REQUIRED).",
    )

    if st.button("Connect ✨"):
        if db_url:
            return {"db_url": db_url}

        if all([host, user, password, database]):
            return {
                "host": host,
                "user": user,
                "password": password,
                "database": database,
                "port": int(port),
                "ssl_enabled": ssl_enabled,
                "db_url": None,
            }

        st.error("Please provide a Database URL or fill all manual fields.")
        return None

    return None


def render_query_interface():
    """
    Renders the question input and Generate button.
    Returns (question, clicked)
    """
    question = st.text_area(
        "Ask your question:",
        placeholder="e.g. Write a complex query to calculate the month-over-month growth of active users...",
    )

    clicked = st.button("Generate & Run ✨")
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

    if isinstance(sql, str) and sql.startswith("INVALID_QUERY"):
        st.error(sql)
        return

    if error:
        st.error(error)
        return

    if isinstance(result, str):
        st.error(result)
        if "please seed some data" in result.lower():
            st.warning("The database schema is empty. Please seed some data.")
        else:
            st.info(result)
        return

    if result is not None:
        st.dataframe(result, use_container_width=True, height=600)