# ✨ NIELIT QueryNova – Smart Database Assistant

*A Natural Language to SQL Interface*
**Project Submitted to:** NIELIT East Delhi (Karkardooma)
**Developed by:** Naman Jain

---

## 📌 Project Overview

**NIELIT QueryNova** is a smart assistant that converts natural language queries into SQL and retrieves data directly from a MySQL database.
Built using modern Python tools, this system eliminates the need for manual SQL writing—enabling users, trainers, or staff to interact with their data using simple English.

---

## 🎯 Key Features

* 🔐 Secure Login System
* 📋 Natural Language to SQL Translation (via Groq LLM)
* 📊 Live Database Query Execution
* 🧠 Schema-Aware Querying (RAG approach with spaCy)
* 🖼️ Modern UI with Sidebar Table Explorer
* 💾 Query History Tracking
* ⏱️ Execution and Generation Time Display
* 🎨 Custom Theming and Background Styling

---

## 🧠 How It Works

1. User enters a question in English
2. The system uses **Groq LLM + schema filtering (RAG)** to generate an SQL query
3. The SQL query is executed on a connected MySQL database
4. Results are displayed in a table, along with SQL generation and execution times

---

## 💬 Sample Questions You Can Ask

* Which students were trained by **Harshita Bhardwaj**?
* List the names and mobile numbers of students trained by **Naman Jain**
* List all trainers with **course codes** and also show their **course duration**

---

## 🏗️ Tech Stack

| Layer      | Technology                         |
| ---------- | ---------------------------------- |
| Language   | Python 3                           |
| Framework  | Streamlit                          |
| LLM        | Groq (LLaMA 3 70B)                 |
| Database   | MySQL                              |
| NLP Filter | spaCy (RAG-style schema selection) |
| Others     | dotenv, PIL, base64, pandas, re    |

---

## ⚙️ Installation Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/nielit-querynova.git
cd nielit-querynova
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Streamlit Secrets

Create a file at: `.streamlit/secrets.toml`

```toml
[auth]
username = "admin"
password = "admin123"

[mysql]
host = "localhost"
user = "root"
password = "your_db_password"
database = "nielit_db"
port = 3306

[api]
groq_api_key = "your_groq_api_key"
```

### 4. Run the App

```bash
streamlit run app.py
```

---

## 🗂️ Project Structure

```
nielit-querynova/
│
├── app.py                   # Main Application Logic
├── requirements.txt         # Python Dependencies
├── images/
│   └── bg.png               # Background Image
├── logo.png                 # App Logo
├── .streamlit/
│   └── secrets.toml         # Login + DB + API credentials
└── README.md                # Project Documentation
```

---

## 🔒 Authentication

Login credentials are securely managed using **Streamlit's `secrets.toml`** mechanism.
No database or admin panel is exposed publicly.

---

## 👨‍💻 Developer

**👤 Naman Jain**
Final Year Project – NIELIT East Delhi, Karkardooma
📧 Email: [namanjain042002@gmail.com](mailto:namanjain042002@gmail.com)

---

## 📜 License & Usage

This project is intended for **educational and institutional use** at NIELIT.
For any commercial use or external deployment, permission from the developer is required.

---
