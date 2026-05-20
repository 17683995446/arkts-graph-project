
import httpx
from typing import Dict, Any, List
import json
import os

SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")
SILICONFLOW_BASE_URL = os.environ.get("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

class LLMQueryHandler:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def natural_language_to_sql(self, question: str) -> str:
        prompt = """You are a SQLite expert. Convert the user's natural language question into a valid SQLite query.

The database has these tables:
1. files (id, path, hash, created_at, updated_at)
2. classes (id, name, file_id, flags) - flags=1 means it's a component
3. methods (id, name, class_id)
4. calls (caller_id, callee_id) - method calls
5. components (parent_id, child_id) - component nesting

Important:
- Use JOINs when needed
- Return ONLY the SQL query, no explanations
- Keep it simple

Question: {}
""".format(question)
        
        try:
            response = await self.client.post(
                f"{SILICONFLOW_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "Qwen/Qwen2.5-7B-Instruct",
                    "messages": [
                        {"role": "system", "content": "You are a SQL query generator."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                sql = result["choices"][0]["message"]["content"].strip()
                sql = sql.replace("```sql", "").replace("```", "").strip()
                return sql
            else:
                return "SELECT * FROM files LIMIT 10"
        except Exception as e:
            print(f"LLM Error: {e}")
            return "SELECT * FROM files LIMIT 10"
    
    async def close(self):
        await self.client.aclose()
