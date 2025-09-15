#!/usr/bin/env python3
"""
Direct database migration using psycopg2
"""

import psycopg2
import os

def migrate_database():
    """Add seller_keyword column directly using psycopg2"""
    try:
        # Get database URL from environment
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("DATABASE_URL not found in environment")
            return
            
        # Fix URL format for psycopg2
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        print(f"Connecting to database...")
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Check if column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='vehicle' AND column_name='seller_keyword';
        """)
        
        if cur.fetchone():
            print("Column seller_keyword already exists")
            return
        
        # Add the column
        cur.execute("ALTER TABLE vehicle ADD COLUMN seller_keyword VARCHAR(255);")
        conn.commit()
        
        print("Column seller_keyword added successfully")
        
        # Close connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    migrate_database()
