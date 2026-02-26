import pandas as pd
from sqlalchemy import create_engine, inspect, text

class DatabaseExecutor:
    def __init__(self, config: dict = None, db_url: str = None):
        self.config = config
        self.db_url = db_url
        self.engine = None
        
        url = self.db_url
        connect_args = {}
        
        if not url and self.config:
            # handle legacy config
            host = self.config.get("host")
            user = self.config.get("user")
            password = self.config.get("password")
            database = self.config.get("database")
            port = self.config.get("port", 3306)
            url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
            
            if self.config.get("ssl_enabled", False):
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                connect_args["ssl"] = ctx

        if url:
            if url.startswith("mysql://"):
                url = url.replace("mysql://", "mysql+pymysql://", 1)
            elif url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            
            from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
            parsed = urlparse(url)
            qs = parse_qsl(parsed.query)
            
            new_qs = []
            ssl_requested = False
            for k, v in qs:
                k_lower = k.lower()
                if k_lower in ['ssl-mode', 'ssl_mode', 'sslmode', 'ssl']:
                    if v.upper() in ['REQUIRED', 'REQUIRE', 'VERIFY_CA', 'VERIFY_IDENTITY', 'TRUE', '1']:
                        ssl_requested = True
                elif k_lower in ['pgbouncer', 'connection_limit', 'pool_timeout']:
                    pass # ignore these pooler specific kwargs for sqlalchemy
                else:
                    new_qs.append((k, v))
            
            parsed = parsed._replace(query=urlencode(new_qs))
            url = urlunparse(parsed)
            
            if ssl_requested:
                if url.startswith("postgresql"):
                    connect_args["sslmode"] = "require"
                else:
                    import ssl
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    connect_args["ssl"] = ctx
            
            self.engine = create_engine(url, connect_args=connect_args, pool_recycle=3600)

    def execute_query(self, sql: str):
        if not self.engine:
            return "Error: No database connection configured for execution."
            
        try:
            with self.engine.connect() as conn:
                sql_lower = sql.strip().lower()
                if sql_lower.startswith(("select", "with", "show", "describe")):
                    result = pd.read_sql(text(sql), conn)
                    return result
                else:
                    result_proxy = conn.execute(text(sql))
                    conn.commit()
                    return f"Query executed successfully. Rows affected: {result_proxy.rowcount}"
        except Exception as e:
            return f"SQL Error: {e}"

    def get_schema(self):
        """Fetches schema from live DB and returns it as a dictionary."""
        if not self.engine:
            raise Exception("No schema available (Not connected).")

        inspector = inspect(self.engine)
        schema = {}
        for table_name in inspector.get_table_names():
            columns = [f"{col['name']} ({col['type']})" for col in inspector.get_columns(table_name)]
            schema[table_name] = columns
        
        return schema