import streamlit as st
import pandas as pd
from utils.db_utils import get_engine, get_schema_preview, run_query
from utils.llm_utils import get_sql_query_from_nl
from sqlalchemy import inspect

# Streamlit page setup
st.set_page_config(page_title="SQL Data Navigator", layout="wide")
st.title("🤖 Enhanced SQL Chatbot (MySQL and POSTGRES Edition)")
st.caption("Chat with your MySQL database using Groq + LangChain")

# 🛠 Database connection sidebar
st.sidebar.header("⚙️ Connection")
db_type = st.sidebar.selectbox("Database Type", ["mysql", "postgres", "sqlite"])

if db_type == "sqlite":
    database = st.sidebar.text_input("Database File", value="local.db")
    user = password = host = port = None
else:
    host = st.sidebar.text_input("Host", value="localhost")
    database = st.sidebar.text_input("Database Name", value="test_db")
    user = st.sidebar.text_input("User")
    password = st.sidebar.text_input("Password", type="password")
    port = st.sidebar.number_input("Port", value=3306 if db_type == "mysql" else 5432)

if st.sidebar.button("Connect"):
    try:
        engine = get_engine(db_type, user, password, host, database, port)
        # Test connection
        with engine.connect() as conn:
            pass
        st.session_state.engine = engine
        st.session_state.schema = get_schema_preview(engine)
        st.session_state.chat_history = []
        st.sidebar.success("✅ Connected!")
    except Exception as e:
        st.sidebar.error(f"Connection failed: {e}")

# 🗂 Schema explorer
if "engine" in st.session_state:
    st.sidebar.header("🗂 Database Tables")
    inspector = inspect(st.session_state.engine)
    for table in inspector.get_table_names():
        with st.sidebar.expander(f"📋 {table}"):
            cols = inspector.get_columns(table)
            st.markdown("\n".join([f"- {c['name']} ({c['type']})" for c in cols]))

# 💬 Chat interface
if "engine" in st.session_state:
    # Display chat history
    for msg in st.session_state.get("chat_history", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "df" in msg:
                st.dataframe(msg["df"])

    if prompt := st.chat_input("How many users signed up last month?"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("🧠 Analyzing database..."):
            sql = get_sql_query_from_nl(prompt, st.session_state.schema)
            
        if sql:
            with st.chat_message("assistant"):
                st.code(sql, language="sql")
                result = run_query(st.session_state.engine, sql)
                
                if isinstance(result, pd.DataFrame):
                    if result.empty:
                        st.warning("No data found for this query.")
                    else:
                        st.dataframe(result)
                        # Add to history
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "content": f"Query results:",
                            "df": result
                        })
                else:
                    st.error(result)
else:
    st.info("Please connect to a database in the sidebar to start chatting.")