from flask import Flask, render_template, request, jsonify
import requests
import re
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Your MySQL username
    'password': 'ani12345',  # Your MySQL password
    'database': 'anik'  # Your database name
}

# LM Studio API configuration
LM_STUDIO_API_URL = "http://localhost:1234/v1/completions"
MODEL_NAME = "hermes-3-llama-3.2-3b"

def clean_sql_query(sql_query):
    """Clean and format the SQL query"""
    return re.sub(r"```sql|```", "", sql_query).strip().rstrip(";")

def generate_sql_query(user_input):
    """Generate SQL query from natural language input"""
    prompt = f"""Convert this to MySQL SQL: {user_input}
    Include only the SQL query without explanations.
    SQL Query:"""
    
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.3
    }

    try:
        response = requests.post(LM_STUDIO_API_URL, json=data, timeout=10)
        response.raise_for_status()
        response_json = response.json()
        
        if "choices" in response_json and response_json["choices"]:
            return clean_sql_query(response_json["choices"][0]["text"].strip())
        
        return None
    except Exception as e:
        return f"API Error: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    sql_query = ""
    user_input = ""
    
    if request.method == 'POST':
        user_input = request.form['user_input']
        sql_query = generate_sql_query(user_input)
    
    return render_template('index.html', user_input=user_input, sql_query=sql_query, inline_css="""
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        h2 {
            color: #333;
        }
        form {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.1);
            display: inline-block;
        }
        input {
            padding: 10px;
            margin: 10px 0;
            width: 300px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            padding: 10px 15px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background: #218838;
        }
        pre {
            background: #fff;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.1);
            display: inline-block;
            text-align: left;
        }
    """)

if __name__ == '__main__':
    app.run(debug=True)
