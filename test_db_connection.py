#!/usr/bin/env python3
"""
Script to test database connectivity for the Flask marketplace app
"""
import os
import sys
import psycopg2
from urllib.parse import urlparse

def test_database_connection():
    """Test connection to the configured database"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        return False
    
    print(f"🔍 Testing connection to: {database_url}")
    
    try:
        # Parse the database URL
        parsed = urlparse(database_url)
        
        print(f"📍 Host: {parsed.hostname}")
        print(f"📍 Port: {parsed.port}")
        print(f"📍 Database: {parsed.path[1:]}")  # Remove leading slash
        print(f"📍 Username: {parsed.username}")
        
        # Test connection
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connection successful!")
        print(f"📊 PostgreSQL version: {version[0]}")
        
        # Test table creation (without committing)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                test_data VARCHAR(50)
            );
        """)
        print("✅ Table creation test successful!")
        
        # Rollback to avoid creating the test table
        conn.rollback()
        
        cursor.close()
        conn.close()
        
        print("🎉 Database connectivity test PASSED!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {str(e)}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if "network is unreachable" in error_str:
            print("\n🔧 TROUBLESHOOTING:")
            print("   - Check if Supabase database is active")
            print("   - Verify network connectivity from Heroku to Supabase")
            print("   - Check Supabase firewall/security settings")
            print("   - Consider using Heroku PostgreSQL as alternative")
        elif "authentication failed" in error_str:
            print("\n🔧 TROUBLESHOOTING:")
            print("   - Verify database username and password")
            print("   - Check if database user has proper permissions")
        elif "does not exist" in error_str:
            print("\n🔧 TROUBLESHOOTING:")
            print("   - Verify database name is correct")
            print("   - Check if database was created in Supabase")
            
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def suggest_heroku_postgres():
    """Suggest using Heroku PostgreSQL as alternative"""
    print("\n" + "="*50)
    print("🔄 ALTERNATIVE SOLUTION: Heroku PostgreSQL")
    print("="*50)
    print("If Supabase connectivity continues to fail, consider using Heroku's native PostgreSQL:")
    print()
    print("1. Add Heroku PostgreSQL addon:")
    print("   heroku addons:create heroku-postgresql:mini --app compraventavalledeuco")
    print()
    print("2. The DATABASE_URL will be automatically set by Heroku")
    print()
    print("3. Initialize database:")
    print("   heroku run python app.py init-db --app compraventavalledeuco")
    print()
    print("4. This will provide better network reliability and integration")

if __name__ == "__main__":
    print("🚀 Database Connectivity Test")
    print("="*30)
    
    success = test_database_connection()
    
    if not success:
        suggest_heroku_postgres()
    
    sys.exit(0 if success else 1)
