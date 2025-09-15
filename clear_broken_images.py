#!/usr/bin/env python3
"""
Script to clear broken image references from database
All existing images are stored as local paths but files were deleted by Heroku's ephemeral filesystem
This script will clear the image references so placeholders show instead of 404 errors
"""

import os
import sys
import json
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

def clear_broken_images():
    """Clear broken image references from database"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not found")
        return False
    
    # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        # Create database connection
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Clear images from vehicles table
                print("Clearing broken image references from vehicles...")
                result = conn.execute(text("""
                    UPDATE vehicle 
                    SET images = NULL 
                    WHERE images IS NOT NULL 
                    AND images != ''
                    AND images NOT LIKE '%http%'
                """))
                vehicles_updated = result.rowcount
                print(f"Updated {vehicles_updated} vehicle records")
                
                # Clear images from client_request table
                print("Clearing broken image references from client requests...")
                result = conn.execute(text("""
                    UPDATE client_request 
                    SET images = NULL 
                    WHERE images IS NOT NULL 
                    AND images != ''
                    AND images NOT LIKE '%http%'
                """))
                requests_updated = result.rowcount
                print(f"Updated {requests_updated} client request records")
                
                # Clear individual image columns from vehicles (if they exist)
                for i in range(1, 11):
                    try:
                        result = conn.execute(text(f"""
                            UPDATE vehicle 
                            SET image_{i} = NULL 
                            WHERE image_{i} IS NOT NULL 
                            AND image_{i} != ''
                            AND image_{i} NOT LIKE '%http%'
                        """))
                        if result.rowcount > 0:
                            print(f"Cleared image_{i} from {result.rowcount} vehicles")
                    except Exception as e:
                        # Column might not exist, continue
                        pass
                
                # Commit transaction
                trans.commit()
                print(f"\n✅ SUCCESS: Cleared broken image references")
                print(f"   - {vehicles_updated} vehicles updated")
                print(f"   - {requests_updated} client requests updated")
                print("   - All records will now show placeholder images")
                print("   - New uploads will use Cloudinary and persist permanently")
                
                return True
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"ERROR during database update: {e}")
                return False
                
    except Exception as e:
        print(f"ERROR connecting to database: {e}")
        return False

if __name__ == '__main__':
    print("🔧 Clearing broken image references from database...")
    print("This will fix the 404 image errors by removing references to deleted local files")
    print()
    
    success = clear_broken_images()
    
    if success:
        print("\n🚀 Database updated successfully!")
        print("Your website should now show placeholder images instead of broken links.")
        print("New image uploads will be saved permanently to Cloudinary.")
    else:
        print("\n❌ Failed to update database. Check the error messages above.")
    
    sys.exit(0 if success else 1)
