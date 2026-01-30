import pymysql
import pandas as pd

class DatabaseExecutor:
    def __init__(self, config: dict):
        self.config = config

    def execute_query(self, sql: str):
        result = None 
        try:
            # PyMySQL connection
            # PyMySQL connection
            connect_args = {
                "host": self.config["host"],
                "user": self.config["user"],
                "password": self.config["password"],
                "database": self.config["database"],
                "port": int(self.config["port"]),
                "cursorclass": pymysql.cursors.DictCursor,
                "connect_timeout": 5
            }

            # Check for SSL requirement
            if self.config.get("ssl_enabled", False):
                import ssl
                # Create a context that generally allows connection (unverified for broad compatibility in this demo)
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                connect_args["ssl"] = ctx

            conn = pymysql.connect(**connect_args)
            cursor = conn.cursor()
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
        connect_args = {
            "host": self.config["host"],
            "user": self.config["user"],
            "password": self.config["password"],
            "database": self.config["database"],
            "port": int(self.config["port"]),
            "connect_timeout": 5
        }

        if self.config.get("ssl_enabled", False):
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ctx

        conn = pymysql.connect(**connect_args)
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
