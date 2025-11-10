"""
database_manager.py

Lightweight MySQL helpers for persisting chat conversations for logged-in users.
Assumptions about schema:
    - conversations(id INT PK AI, userId VARCHAR(255), createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    - messages(id INT PK AI, conversationId INT, sender ENUM('user','bot') or VARCHAR(10), content TEXT,
                         timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

This module is resilient: returns None/[]/False on DB errors so the app can
still function for anonymous sessions or if DB is temporarily unavailable.
"""

import os
import mysql.connector
from dotenv import load_dotenv

# Ensure environment variables are loaded (Good practice if running this file standalone)
load_dotenv() 

# --- Configuration ---
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "pool_name": "mysql_chat_pool",
    "pool_size": 5 # Adjust size based on expected load (5 is a safe start)
}

# --- 1. Connection Pool Setup ---
try:
    # Use a pool for efficient connection management in a web server environment
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
    print("Database connection pool created successfully.")
except mysql.connector.Error as err:
    print(f"FATAL DB ERROR: Could not create connection pool: {err}")
    connection_pool = None # Ensure it's None if creation fails

# --- 2. Connection Retrieval Helper ---
def get_db_connection():
    """Retrieves a connection from the pool."""
    if connection_pool:
        try:
            return connection_pool.get_connection()
        except mysql.connector.Error as err:
            print(f"Error getting connection from pool: {err}")
            return None
    return None

# --- 3. Core Database Interaction Functions ---

def create_new_conversation(user_id):
    """Creates a new conversation record and returns the new ID."""
    conn = get_db_connection()
    if not conn: return None
    
    cursor = conn.cursor()
    try:
        # NOTE: conversationsWithAI table must exist and userId must be correct type (VARCHAR)
        query = "INSERT INTO conversationsWithAI (userId) VALUES (%s)"
        cursor.execute(query, (user_id,))
        conn.commit()
        # Get the ID of the newly inserted row
        new_id = cursor.lastrowid
        return new_id
    except mysql.connector.Error as err:
        print(f"Error creating conversation: {err}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close() # Return connection to the pool

def get_latest_conversation_for_user(user_id):
    """Returns the most recent conversation id for a user, or None."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT conversationId FROM conversationsWithAI WHERE userId = %s ORDER BY createdAt DESC LIMIT 1",
            (user_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    except mysql.connector.Error as err:
        print(f"Error retrieving latest conversation: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_or_create_conversation(user_id):
    """Gets the latest conversation id for a user, or creates one if none exists."""
    conv_id = get_latest_conversation_for_user(user_id)
    if conv_id:
        return conv_id
    return create_new_conversation(user_id)

def save_message(conversation_id, sender, content):
    """Saves a single message (user or bot) to the messages table."""
    conn = get_db_connection()
    if not conn: return False

    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO messagesWithAI (conversationId, sender, content)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (conversation_id, sender, content))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error saving message: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
        
def get_history(conversation_id, limit=10):
    """Retrieves the message history for AI context."""
    conn = get_db_connection()
    if not conn: return []

    # Use dictionary=True to get results as dictionaries (easier for Python)
    cursor = conn.cursor(dictionary=True) 
    try:
        query = """
        SELECT sender, content 
        FROM messagesWithAI 
        WHERE conversationId = %s
        ORDER BY timestamp DESC
        LIMIT %s
        """
        cursor.execute(query, (conversation_id, limit))
        # Fetch all results and reverse them to be chronological for the AI
        history = cursor.fetchall()
        return history[::-1] 
    except mysql.connector.Error as err:
        print(f"Error retrieving history: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def ensure_conversation_title(conversation_id, candidate_title):
    """Set a title for the conversation if it's currently NULL."""
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        # Only set title if NULL
        cursor.execute(
            "UPDATE conversationsWithAI SET title = COALESCE(title, %s) WHERE conversationId = %s",
            (candidate_title[:100], conversation_id)
        )
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error setting conversation title: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()