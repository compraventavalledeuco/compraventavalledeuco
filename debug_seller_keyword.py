#!/usr/bin/env python3
"""
Debug script to check seller keyword functionality
"""
import os
os.environ.setdefault("SKIP_ROUTES", "1")

from app import app, db
from models import Vehicle, ClientRequest

def debug_seller_keyword():
    with app.app_context():
        print("=== DEBUGGING SELLER KEYWORD SYSTEM ===")
        
        # Check Vehicle table columns
        print("\n1. Vehicle table columns:")
        vehicle_columns = [c.name for c in Vehicle.__table__.columns]
        print(vehicle_columns)
        has_seller_keyword = 'seller_keyword' in vehicle_columns
        print(f"Has seller_keyword column: {has_seller_keyword}")
        
        # Check ClientRequest table columns
        print("\n2. ClientRequest table columns:")
        client_request_columns = [c.name for c in ClientRequest.__table__.columns]
        print(client_request_columns)
        has_client_seller_keyword = 'seller_keyword' in client_request_columns
        print(f"Has seller_keyword column: {has_client_seller_keyword}")
        
        # Check existing vehicles with seller_keyword
        print("\n3. Vehicles with seller_keyword:")
        if has_seller_keyword:
            vehicles_with_keyword = Vehicle.query.filter(Vehicle.seller_keyword.isnot(None)).all()
            print(f"Found {len(vehicles_with_keyword)} vehicles with seller_keyword")
            for v in vehicles_with_keyword[:5]:  # Show first 5
                print(f"  - ID: {v.id}, Title: {v.title}, Keyword: {v.seller_keyword}")
        else:
            print("  seller_keyword column missing in Vehicle table")
        
        # Check existing client requests with seller_keyword
        print("\n4. Client requests with seller_keyword:")
        if has_client_seller_keyword:
            requests_with_keyword = ClientRequest.query.filter(ClientRequest.seller_keyword.isnot(None)).all()
            print(f"Found {len(requests_with_keyword)} client requests with seller_keyword")
            for r in requests_with_keyword[:5]:  # Show first 5
                print(f"  - ID: {r.id}, Name: {r.name}, Keyword: {r.seller_keyword}")
        else:
            print("  seller_keyword column missing in ClientRequest table")
        
        # Check total counts
        print("\n5. Total counts:")
        total_vehicles = Vehicle.query.count()
        total_requests = ClientRequest.query.count()
        print(f"Total vehicles: {total_vehicles}")
        print(f"Total client requests: {total_requests}")

if __name__ == "__main__":
    debug_seller_keyword()
