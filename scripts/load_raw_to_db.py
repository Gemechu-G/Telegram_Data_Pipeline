import os
import json
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import logging
from datetime import datetime

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Load Environment Variables ---
load_dotenv()

DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')

RAW_MESSAGES_PATH = os.path.join(os.getcwd(), 'data', 'raw', 'telegram_messages')

def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise

def create_raw_messages_table(cursor):
    """Creates the raw_telegram_messages table if it doesn't exist."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS raw_telegram_messages (
        id SERIAL PRIMARY KEY,
        message_data JSONB,
        loaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        file_path TEXT UNIQUE
    );
    """
    cursor.execute(create_table_query)
    logger.info("Table 'raw_telegram_messages' ensured to exist.")

def load_json_to_db():
    """
    Reads JSON files from the raw data directory and loads them into PostgreSQL.
    Handles nested directories and avoids reprocessing already loaded files.
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False # Use transactions for better integrity
        cursor = conn.cursor()

        create_raw_messages_table(cursor)

        loaded_files = set()
        # Check for already loaded files
        cursor.execute("SELECT file_path FROM raw_telegram_messages;")
        for row in cursor.fetchall():
            loaded_files.add(row[0])

        files_to_load = []
        for root, _, files in os.walk(RAW_MESSAGES_PATH):
            for file_name in files:
                if file_name.endswith('.json'):
                    file_path = os.path.join(root, file_name)
                    if file_path not in loaded_files:
                        files_to_load.append(file_path)

        if not files_to_load:
            logger.info("No new JSON files to load into the database.")
            return

        insert_count = 0
        for file_path in files_to_load:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    messages = json.load(f)

                # Ensure messages is a list. If a file contains a single message, json.load might return a dict.
                if not isinstance(messages, list):
                    messages = [messages]

                # Prepare data for batch insertion
                data_to_insert = []
                for message in messages:
                    # Add a unique identifier for the specific message within the JSON array,
                    # this assumes 'id' field exists in each message object
                    unique_id = f"{file_path}_{message.get('id', 'no_id')}"
                    data_to_insert.append((json.dumps(message), datetime.now(), file_path))

                # Using executemany for efficiency
                insert_query = sql.SQL("""
                    INSERT INTO raw_telegram_messages (message_data, loaded_at, file_path)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (file_path) DO NOTHING; -- Prevents re-inserting if file_path is already there
                """)
                cursor.executemany(insert_query, data_to_insert)
                insert_count += len(data_to_insert)
                logger.info(f"Loaded {len(data_to_insert)} messages from {file_path}")
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from {file_path}: {e}")
            except Exception as e:
                logger.error(f"Error loading file {file_path} to DB: {e}", exc_info=True)

        conn.commit()
        logger.info(f"Successfully loaded {insert_count} new messages into raw_telegram_messages table.")

    except Exception as e:
        if conn:
            conn.rollback() # Rollback on error
        logger.critical(f"Fatal error during database loading: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")

if __name__ == '__main__':
    load_json_to_db()