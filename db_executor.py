import mysql.connector
import pandas as pd

class DatabaseExecutor:
    def __init__(self, config: dict):
        self.config = config

    def execute_query(self, sql: str):
        result = None 
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql)

            # If it's a SELECT query
            if sql.strip().lower().startswith("select"):
                rows = cursor.fetchall()
                result = pd.DataFrame(rows)
            else:
                # UPDATE / INSERT / DELETE
                conn.commit()
                result = f"Query executed successfully. Rows affected: {cursor.rowcount}"
            
            cursor.close()
            conn.close()
            return result
            
        except Exception as e:
            return f"SQL Error: {e}"

    def get_schema(self):
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME;
        """, (self.config["database"],))

        schema = {}
        for table, column, dtype in cursor.fetchall():
            schema.setdefault(table, []).append(f"{column} ({dtype})")

        cursor.close()
        conn.close()
        return schema
