import os
import pymysql
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load env
load_dotenv()

db_name = os.getenv('DB_NAME', 'lms_db')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', '127.0.0.1')
db_port = int(os.getenv('DB_PORT', '3306'))

print(f"Connecting to MySQL server at {db_host}:{db_port} as {db_user}...")
try:
    conn = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        port=db_port
    )
    cursor = conn.cursor()
    print(f"Creating database '{db_name}' if it does not exist...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    conn.commit()
    cursor.close()
    conn.close()
    print("Database check/creation successful!")
except Exception as e:
    print(f"Error creating database: {e}")
