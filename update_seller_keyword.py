#!/usr/bin/env python3
"""
Script to update seller_keyword for vehicle ID 8 from 'Diego Portaz' to 'diegoautos'
This script can be run in production to fix the seller keyword.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def update_seller_keyword():
    try:
        from app import app, db
        from models import Vehicle
        
        with app.app_context():
            # Find vehicle with ID 8
            vehicle = Vehicle.query.get(8)
            if vehicle:
                print(f'Vehicle ID: {vehicle.id}')
                print(f'Title: {vehicle.title}')
                print(f'Current seller_keyword: "{vehicle.seller_keyword}"')
                
                # Update seller_keyword to 'diegoautos'
                vehicle.seller_keyword = 'diegoautos'
                db.session.commit()
                
                print(f'✅ Updated seller_keyword to: "{vehicle.seller_keyword}"')
                return True
            else:
                print('❌ Vehicle with ID 8 not found')
                return False
                
    except Exception as e:
        print(f'❌ Error updating seller keyword: {e}')
        return False

if __name__ == "__main__":
    print("Updating seller keyword for vehicle ID 8...")
    success = update_seller_keyword()
    if success:
        print("✅ Update completed successfully!")
    else:
        print("❌ Update failed!")
