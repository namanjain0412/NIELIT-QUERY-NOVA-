import os
import streamlit as st
import mysql.connector
import pandas as pd
from dotenv import load_dotenv
from groq import Groq
import re
from PIL import Image
import time
import base64
import spacy

# Load the pre-trained spaCy model
nlp = spacy.load("en_core_web_sm")

# ==========================
#  LOAD ENVIRONMENT VARIABLES
# ==========================
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq API Client
client = Groq(api_key=api_key)

# Database Config from .streamlit/secrets.toml
db_config = {
    "host": st.secrets["mysql"]["host"],
    "user": st.secrets["mysql"]["user"],
    "password": st.secrets["mysql"]["password"],
    "database": st.secrets["mysql"]["database"],
    "port": st.secrets["mysql"]["port"]
}

# Authentication Credentials
VALID_USERNAME = st.secrets["auth"]["username"]
VALID_PASSWORD = st.secrets["auth"]["password"]

# ==========================
#  DATABASE CONNECTION FUNCTION
# ==========================
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        st.error(f"Database Connection Error: {err}")
        return None

# ==========================
#  GET DATABASE SCHEMA
# ==========================
def get_database_schema():
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE()")
    schema = {}
    for table, column in cursor.fetchall():
        if table not in schema:
            schema[table] = []
        schema[table].append(column)
    cursor.close()
    conn.close()
    return schema

# ==========================
#  RAG HELPERS
# ==========================
def create_schema_chunks(schema):
    chunks = []
    for table, columns in schema.items():
        column_str = ", ".join(columns)
        text = f"Table: {table}\nColumns: {column_str}"
        chunks.append({"table": table, "text": text})
    return chunks

def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop]
    return keywords

def retrieve_relevant_chunks(chunks, user_keywords):
    relevant = []
    for chunk in chunks:
        if any(keyword in chunk["text"].lower() for keyword in user_keywords):
            relevant.append(chunk["text"])
    return relevant

# ==========================
#  EXTRACT SQL FROM RESPONSE
# ==========================
def extract_sql_from_response(response_text):
    sql_match = re.search(r"SELECT .*?;", response_text, re.DOTALL | re.IGNORECASE)
    return sql_match.group(0).strip() if sql_match else None

# ==========================
#  GENERATE SQL QUERY FROM USER INPUT (RAG)
# ==========================
def generate_sql_query(user_input, schema):
    restricted_keywords = ["who is", "what is", "where is", "capital of", "define", "tell me about", "prime minister", "president", "country", "world record"]
    if any(keyword in user_input.lower() for keyword in restricted_keywords):
        st.error("❌ Invalid query! This tool only supports database-related questions.")
        return None, 0

    schema_chunks = create_schema_chunks(schema)
    user_keywords = extract_keywords(user_input)
    relevant_schema = retrieve_relevant_chunks(schema_chunks, user_keywords)

    if not relevant_schema:
        st.warning("⚠️ Couldn't find relevant schema. Using full schema.")
        relevant_schema = [chunk["text"] for chunk in schema_chunks]

    prompt = f"""
You are an expert in converting English questions to SQL queries.
Use the following database schema information:

{chr(10).join(relevant_schema)}

Convert the following question into an SQL query.
Only return the SQL query (no explanation):

\"{user_input}\"
"""

    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        generation_time = time.time() - start_time
        sql_query = extract_sql_from_response(response.choices[0].message.content.strip())
        return sql_query, generation_time
    except Exception as e:
        st.error(f"LLM Error: {str(e)}")
        return None, 0

# ==========================
#  ADD BACKGROUND WITH IMAGE OVERLAY
# ==========================
def add_bg_with_overlay(image_file_path):
    with open(image_file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)),
                              url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ==========================
#  STREAMLIT STYLING
# ==========================
st.set_page_config(page_title="Nielit QueryNova", page_icon="✨", layout="wide")

st.markdown(""" 
    <style>
        .stApp {
            font-family: 'Segoe UI', sans-serif;
        }
        .heading {
            text-align: center;
            font-size: 42px;
            font-weight: 700;
            color: #0a3d62;
        }
        .subheading {
            text-align: center;
            font-size: 22px;
            color: #0984e3;
            font-weight: 600;
        }
        .stButton > button {
            background-color: #0984e3;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 16px;
            transition: 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #0652DD;
        }
        .stTextInput > div > div > input {
            font-size: 18px;
            padding: 10px;
        }
        footer { visibility: hidden; }
        .footer-fixed {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f8f9fa;
            padding: 10px;
            text-align: center;
            font-size: 14px;
            color: #555;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================
#  AUTHENTICATION HANDLING
# ==========================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "logout_triggered" not in st.session_state:
    st.session_state["logout_triggered"] = False

def login():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔐 Welcome to Nielit QueryNova")
        st.markdown("<h2 class='subheading'>Your Smart Database Assistant</h2>", unsafe_allow_html=True)
    with col2:
        logo = Image.open("logo.png")
        st.image(logo, width=100)

    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state["authenticated"] = True
            st.session_state["logout_triggered"] = False
        else:
            st.error("Invalid username or password!")

def logout():
    st.session_state["authenticated"] = False
    st.session_state["logout_triggered"] = True

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ==========================
#  MAIN INTERFACE
# ==========================
add_bg_with_overlay("images/bg.png")

col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("<h1 class='heading'>Nielit QueryNova</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='subheading'>Smart Database Assistant</h2>", unsafe_allow_html=True)
with col2:
    logo = Image.open("logo.png")
    st.image(logo, width=80)

# Sidebar
with st.sidebar:
    st.image("logo.png", width=120)
    st.markdown("### ⚙️ Nielit QueryNova")
    st.markdown("Your AI-Powered SQL Assistant")
    st.button("Logout", on_click=logout)

# Get Database Schema
schema = get_database_schema()
if schema:
    st.sidebar.subheader("📂 Database Tables")
    with st.sidebar.expander("📌 Select a Table", expanded=False):
        for table in schema.keys():
            if st.button(f"📄 {table}"):
                st.sidebar.write(f"**Columns in {table}:**")
                st.sidebar.write(", ".join(schema[table]))

# ==========================
#  INPUT + OUTPUT SECTION
# ==========================
st.markdown("### 📝 Ask a Question About Your Database")
user_input = st.text_input("Type your database-related question:")

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if st.button("Generate SQL & Fetch Data"):
    if user_input:
        sql_query, generation_time = generate_sql_query(user_input, schema)
        if sql_query:
            st.session_state.query_history.append((sql_query, generation_time))
            st.success("✅ SQL Query Generated:")
            st.code(sql_query, language="sql")
            st.write(f"⏱ Generated in {generation_time:.2f} seconds")

            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    start_time = time.time()
                    cursor.execute(sql_query)
                    execution_time = time.time() - start_time
                    columns = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()
                    df = pd.DataFrame(results, columns=columns)
                    st.write(f"⏱ Query executed in {execution_time:.2f} seconds")
                    st.dataframe(df)
                except Exception as e:
                    st.error(f"Error executing query: {e}")
                finally:
                    cursor.close()
                    conn.close()
        else:
            st.error("❌ Could not generate a valid SQL query from your input.")

# ==========================
#  FOOTER
# ==========================
st.markdown("""
    <div class='footer-fixed'>
        Developed with ⚙️ by <strong>Naman Jain</strong> <br>
        <span style='font-size: 12px; color: #aaa;'>Version 1.0 • Last updated: May 2025</span><br>
        <p style='font-size: 12px;'>© 2025 Nielit Corporation. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)