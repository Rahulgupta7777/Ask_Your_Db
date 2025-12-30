from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SQLQueryGenerator:
    def generate_sql(self, question: str, system_prompt: str) -> str:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0
        )

        sql = response.choices[0].message.content.strip()

        if "```" in sql:
            sql = sql.replace("```sql", "").replace("```", "").strip()

        return sql
