import os
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_sql_query_from_nl(prompt, schema):
    schema_text = "\n".join([f"Table {table}: {', '.join(cols)}" for table, cols in schema.items()])
    
    full_prompt = f"""
    You are a professional SQL Data Analyst. Your job is to convert natural language questions into valid SQL queries.
    
    CRITICAL RULES:
    1. Only generate SELECT statements. 
    2. Do NOT generate INSERT, UPDATE, DELETE, or DROP statements.
    3. Use the schema provided below.
    4. Return ONLY the SQL code. No explanation.

    Schema:
    {schema_text}

    Question: {prompt}
    """

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": full_prompt}],
                "temperature": 0
            }
        )
        content = response.json()["choices"][0]["message"]["content"].strip()
        # Clean markdown formatting if present
        return content.replace("```sql", "").replace("```", "").strip()
    except Exception as e:
        return None