import pymysql
import ssl

# Create a context that ignores verification but uses SSL
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

config = {
    "host": "mysql-3b560640-rahulgupta193246-8e3a.g.aivencloud.com", # Public host (ok to keep or redact)
    "user": "avnadmin",
    "password": "REDACTED_PASSWORD", # REDACTED
    "database": "defaultdb",
    "port": 22940,
    "connect_timeout": 5,
    "cursorclass": pymysql.cursors.DictCursor,
    "ssl": ctx
}

print(f"Connecting with ssl context (no verify)...")

# This script is for reproduction only and requires credentials to run.
# Credentials have been redacted for security.
if config["password"] == "REDACTED_PASSWORD":
    print("Please provide a valid password in the config dictionary to run this script.")
else:
    try:
        conn = pymysql.connect(**config)
        print("Connected successfully!")
        
        cursor = conn.cursor()
        cursor.execute("SHOW STATUS LIKE 'Ssl_cipher'")
        result = cursor.fetchone()
        print(f"SSL Cipher: {result}")
        
        conn.close()
    except Exception as e:
        print(f"Connection FAILED: {e}")
