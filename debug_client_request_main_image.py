#!/usr/bin/env python3
"""
Debug script to test main image selection in client request form
Run this on Heroku to check if main_image_index is being saved correctly
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, ClientRequest

def debug_client_request_main_image():
    """Debug client request main image selection"""
    with app.app_context():
        print("=== CLIENT REQUEST MAIN IMAGE DEBUG ===")
        print(f"Timestamp: {datetime.now()}")
        print()
        
        # Get recent client requests
        recent_requests = ClientRequest.query.order_by(ClientRequest.id.desc()).limit(5).all()
        
        if not recent_requests:
            print("❌ No client requests found in database")
            return
        
        print(f"📊 Found {len(recent_requests)} recent client requests")
        print()
        
        for request in recent_requests:
            print(f"🔍 CLIENT REQUEST ID: {request.id}")
            print(f"   Title: {request.title}")
            print(f"   Full Name: {request.full_name}")
            print(f"   Publication Type: {request.publication_type}")
            
            # Check images
            images = request.get_images_list()
            print(f"   Images count: {len(images)}")
            
            if images:
                print(f"   main_image_index: {request.main_image_index}")
                print(f"   Images list:")
                for idx, img in enumerate(images):
                    is_main = "⭐ MAIN" if idx == request.main_image_index else ""
                    print(f"     [{idx}] {img[:60]}... {is_main}")
                
                # Test get_main_image method
                main_image = request.get_main_image()
                print(f"   get_main_image() returns: {main_image[:60]}...")
                
                # Check if main image matches expected index
                expected_main = images[request.main_image_index] if request.main_image_index < len(images) else images[0]
                if main_image == expected_main:
                    print("   ✅ get_main_image() returns correct image")
                else:
                    print("   ❌ get_main_image() returns WRONG image")
                    print(f"      Expected: {expected_main[:60]}...")
                    print(f"      Got: {main_image[:60]}...")
            else:
                print("   ❌ No images found")
            
            print("-" * 80)

if __name__ == "__main__":
    debug_client_request_main_image()
