#!/usr/bin/env python3
"""
Test seller keyword functionality by creating sample data
"""
import os
os.environ.setdefault("SKIP_ROUTES", "1")

from app import app, db
from models import Vehicle, ClientRequest
import json

def test_seller_keyword():
    with app.app_context():
        try:
            # Create a test vehicle with seller_keyword directly
            test_vehicle = Vehicle(
                title="Test Auto AUTOSDIEGO",
                brand="Toyota",
                model="Corolla",
                year=2020,
                price=15000000,
                currency="ARS",
                kilometers=50000,
                fuel_type="Nafta",
                transmission="Manual",
                location="Tupungato",
                description="Auto de prueba para sistema de palabras clave",
                whatsapp_number="2622123456",
                call_number="2622123456",
                contact_type="whatsapp",
                images=json.dumps(["placeholder-car.png"]),
                seller_keyword="AUTOSDIEGO",
                is_plus=False
            )
            
            db.session.add(test_vehicle)
            db.session.commit()
            
            print(f"✅ Test vehicle created with ID: {test_vehicle.id}")
            print(f"   Title: {test_vehicle.title}")
            print(f"   Seller keyword: {test_vehicle.seller_keyword}")
            
            # Verify it can be found by keyword
            vehicles_with_keyword = Vehicle.query.filter_by(seller_keyword="AUTOSDIEGO").all()
            print(f"✅ Found {len(vehicles_with_keyword)} vehicles with keyword 'AUTOSDIEGO'")
            
            return test_vehicle.id
            
        except Exception as e:
            print(f"❌ Error creating test vehicle: {e}")
            return None

if __name__ == "__main__":
    test_seller_keyword()
