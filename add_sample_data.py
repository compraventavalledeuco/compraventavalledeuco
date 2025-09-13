#!/usr/bin/env python3
"""
Script para agregar datos de muestra al marketplace Valle de Uco
"""

from app import app, db
from models import Vehicle, Admin
from datetime import datetime
import os

def add_sample_vehicles():
    """Agrega vehículos de muestra a la base de datos"""
    
    sample_vehicles = [
        {
            'title': 'Toyota Corolla 2020 - Excelente Estado',
            'brand': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'price': 8500000,
            'currency': 'ARS',
            'description': 'Toyota Corolla 2020 en excelente estado. Único dueño, service oficial completo. Motor 1.8 CVT, muy económico.',
            'fuel_type': 'Nafta',
            'transmission': 'Automática',
            'kilometers': 45000,
            'whatsapp_number': '2622581554',
            'call_number': '2622581554',
            'contact_type': 'whatsapp',
            'is_plus': True,
            'is_active': True,
            'location': 'Tupungato'
        },
        {
            'title': 'Ford Focus 2018 - Titanium',
            'brand': 'Ford',
            'model': 'Focus',
            'year': 2018,
            'price': 6200000,
            'currency': 'ARS',
            'description': 'Ford Focus Titanium 2018. Full equipo, cuero, climatizador automático, excelente estado general.',
            'fuel_type': 'Nafta',
            'transmission': 'Manual',
            'kilometers': 78000,
            'whatsapp_number': '2622581554',
            'call_number': '2622581554',
            'contact_type': 'whatsapp',
            'is_plus': False,
            'is_active': True,
            'location': 'Tunuyán'
        },
        {
            'title': 'Chevrolet Onix 2021 - Como Nuevo',
            'brand': 'Chevrolet',
            'model': 'Onix',
            'year': 2021,
            'price': 7800000,
            'currency': 'ARS',
            'description': 'Chevrolet Onix 2021 prácticamente nuevo. Pocos kilómetros, garantía vigente.',
            'fuel_type': 'Nafta',
            'transmission': 'Manual',
            'kilometers': 15000,
            'whatsapp_number': '2622581554',
            'call_number': '2622581554',
            'contact_type': 'phone',
            'is_plus': True,
            'is_active': True,
            'location': 'San Carlos'
        },
        {
            'title': 'Volkswagen Gol 2019 - Trend',
            'brand': 'Volkswagen',
            'model': 'Gol',
            'year': 2019,
            'price': 4500000,
            'currency': 'ARS',
            'description': 'VW Gol Trend 2019. Muy cuidado, ideal primer auto. Económico y confiable.',
            'fuel_type': 'Nafta',
            'transmission': 'Manual',
            'kilometers': 62000,
            'whatsapp_number': '2622581554',
            'call_number': '2622581554',
            'contact_type': 'whatsapp',
            'is_plus': False,
            'is_active': True,
            'location': 'Tupungato'
        },
        {
            'title': 'Fiat Cronos 2020 - Drive',
            'brand': 'Fiat',
            'model': 'Cronos',
            'year': 2020,
            'price': 5900000,
            'currency': 'ARS',
            'description': 'Fiat Cronos Drive 2020. Excelente relación precio-calidad. Muy espacioso.',
            'fuel_type': 'Nafta',
            'transmission': 'Manual',
            'kilometers': 55000,
            'whatsapp_number': '2622581554',
            'call_number': '2622581554',
            'contact_type': 'both',
            'is_plus': True,
            'is_active': True,
            'location': 'Tunuyán'
        }
    ]
    
    print("Agregando vehículos de muestra...")
    
    for vehicle_data in sample_vehicles:
        # Verificar si ya existe un vehículo similar
        existing = Vehicle.query.filter_by(
            title=vehicle_data['title']
        ).first()
        
        if not existing:
            vehicle = Vehicle(
                title=vehicle_data['title'],
                brand=vehicle_data['brand'],
                model=vehicle_data['model'],
                year=vehicle_data['year'],
                price=vehicle_data['price'],
                currency=vehicle_data['currency'],
                description=vehicle_data['description'],
                location=vehicle_data['location'],
                fuel_type=vehicle_data['fuel_type'],
                transmission=vehicle_data['transmission'],
                kilometers=vehicle_data['kilometers'],
                whatsapp_number=vehicle_data['whatsapp_number'],
                call_number=vehicle_data['call_number'],
                contact_type=vehicle_data['contact_type'],
                is_plus=vehicle_data['is_plus'],
                is_active=vehicle_data['is_active'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(vehicle)
            print(f"Agregado: {vehicle_data['title']}")
        else:
            print(f"- Ya existe: {vehicle_data['title']}")
    
    try:
        db.session.commit()
        print(f"\nVehiculos agregados exitosamente!")
        
        # Mostrar estadísticas
        total_vehicles = Vehicle.query.count()
        active_vehicles = Vehicle.query.filter_by(is_active=True).count()
        plus_vehicles = Vehicle.query.filter_by(is_plus=True, is_active=True).count()
        
        print(f"Estadisticas:")
        print(f"   Total de vehiculos: {total_vehicles}")
        print(f"   Vehiculos activos: {active_vehicles}")
        print(f"   Publicaciones Plus: {plus_vehicles}")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al agregar vehiculos: {e}")

def add_admin_user():
    """Agrega usuario administrador si no existe"""
    admin = Admin.query.filter_by(username='Ryoma94').first()
    if not admin:
        admin = Admin(
            username='Ryoma94',
            password_hash='admin123',  # Se hasheará automáticamente
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuario administrador creado: Ryoma94")
    else:
        print("- Usuario administrador ya existe")

if __name__ == '__main__':
    with app.app_context():
        print("Inicializando datos de muestra para Marketplace Valle de Uco")
        print("=" * 60)
        
        # Crear tablas si no existen
        db.create_all()
        
        # Agregar usuario admin
        add_admin_user()
        
        # Agregar vehículos de muestra
        add_sample_vehicles()
        
        print("\nDatos de muestra agregados correctamente!")
        print("Ahora puedes acceder a la aplicacion y ver los vehiculos.")
