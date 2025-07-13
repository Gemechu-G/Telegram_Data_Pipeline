# test_env.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access some variables
telegram_api_id = os.getenv("TELEGRAM_API_ID")
db_user = os.getenv("POSTGRES_USER")
db_host = os.getenv("POSTGRES_HOST")
db_password = os.getenv("POSTGRES_PASSWORD") # Good to check a secret too

print(f"Telegram API ID: {telegram_api_id}")
print(f"DB User: {db_user}")
print(f"DB Host: {db_host}")
print(f"DB Password (first 3 chars): {db_password[:3]}...") # Don't print full password

if telegram_api_id and db_user and db_host and db_password:
    print("Environment variables loaded successfully!")
else:
    print("Error: One or more environment variables not loaded or empty.")
    print("Check your .env file and ensure it's in the project root with correct values.")