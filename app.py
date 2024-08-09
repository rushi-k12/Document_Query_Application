import streamlit as st
import sqlite3
import os
import hashlib
from datetime import datetime
import pandas as pd
from cryptography.fernet import Fernet
from PyPDF2 import PdfReader
from docx import Document
import base64

# Database Connection
conn = sqlite3.connect('app.db', check_same_thread=False)
c = conn.cursor()

# Encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

# Initialize DB
def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, user_id INTEGER, filename TEXT, content TEXT, date_added TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS queries (id INTEGER PRIMARY KEY, user_id INTEGER, query TEXT, response TEXT, date TEXT)''')
    conn.commit()

# User Authentication
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login(username, password):
    hashed_password = hash_password(password)
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    return c.fetchone()

def register(username, password):
    hashed_password = hash_password(password)
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()

# Document Uploading and Querying
def save_document(user_id, filename, content):
    encrypted_content = cipher.encrypt(content.encode())
    c.execute('INSERT INTO documents (user_id, filename, content, date_added) VALUES (?, ?, ?, ?)', 
              (user_id, filename, encrypted_content, str(datetime.now())))
    conn.commit()

def search_document(user_id, query):
    c.execute('SELECT filename, content FROM documents WHERE user_id = ?', (user_id,))
    results = []
    for filename, content in c.fetchall():
        decrypted_content = cipher.decrypt(content).decode()
        if query.lower() in decrypted_content.lower():
            results.append((filename, decrypted_content))
    return results

# UI Design
def main():
    st.title("Document Query Application")

    menu = ["Login", "Register", "Upload Document", "Query Document", "History", "Download Chat History"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            user = login(username, password)
            if user:
                st.session_state['user_id'] = user[0]
                st.success("Logged in as {}".format(username))
            else:
                st.warning("Incorrect username/password")

    elif choice == "Register":
        st.subheader("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Register"):
            register(username, password)
            st.success("You have successfully registered")

    elif choice == "Upload Document":
        st.subheader("Upload Document")
        if 'user_id' not in st.session_state:
            st.warning("Please login first")
        else:
            file = st.file_uploader("Upload File", type=["pdf", "docx", "txt"])
            if file is not None:
                content = ''
                if file.type == "application/pdf":
                    reader = PdfReader(file)
                    content = ''.join([page.extract_text() for page in reader.pages])
                elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(file)
                    content = ''.join([para.text for para in doc.paragraphs])
                elif file.type == "text/plain":
                    content = file.read().decode('utf-8')
                
                if content:
                    save_document(st.session_state['user_id'], file.name, content)
                    st.success("Document uploaded successfully")

    elif choice == "Query Document":
        st.subheader("Query Document")
        if 'user_id' not in st.session_state:
            st.warning("Please login first")
        else:
            query = st.text_input("Enter your query")
            if st.button("Search"):
                results = search_document(st.session_state['user_id'], query)
                if results:
                    for filename, content in results:
                        st.write(f"**{filename}**")
                        st.write(content)
                else:
                    st.write("No relevant documents found")

    elif choice == "History":
        st.subheader("Query History")
        if 'user_id' not in st.session_state:
            st.warning("Please login first")
        else:
            c.execute('SELECT query, response, date FROM queries WHERE user_id = ?', (st.session_state['user_id'],))
            history = c.fetchall()
            for query, response, date in history:
                st.write(f"**Query**: {query} | **Response**: {response} | **Date**: {date}")

    elif choice == "Download Chat History":
        st.subheader("Download Chat History")
        if 'user_id' not in st.session_state:
            st.warning("Please login first")
        else:
            c.execute('SELECT query, response, date FROM queries WHERE user_id = ?', (st.session_state['user_id'],))
            history = c.fetchall()
            history_text = "\n".join([f"Query: {query}\nResponse: {response}\nDate: {date}\n" for query, response, date in history])
            b64 = base64.b64encode(history_text.encode()).decode()
            href = f'<a href="data:file/text;base64,{b64}" download="chat_history.txt">Download Chat History</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == '__main__':
    init_db()
    main()
