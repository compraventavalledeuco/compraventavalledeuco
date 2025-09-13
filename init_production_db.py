#!/usr/bin/env python3
"""
Script para inicializar la base de datos en producción
Ejecutar este script después del despliegue para crear tablas y datos de muestra
"""

import os
import sys
from app import app, db
from models import Vehicle, Admin
from datetime import datetime

def init_production_database():
    """Inicializa la base de datos en producción"""
    print("=== INICIALIZANDO BASE DE DATOS EN PRODUCCION ===")
    
    with app.app_context():
        try:
            # Crear todas las tablas
            print("1. Creando tablas de base de datos...")
            db.create_all()
            print("   ✓ Tablas creadas exitosamente")
            
            # Verificar si ya existen datos
            vehicle_count = Vehicle.query.count()
            admin_count = Admin.query.count()
            
            print(f"   - Vehículos existentes: {vehicle_count}")
            print(f"   - Administradores existentes: {admin_count}")
            
            # Crear usuario administrador si no existe
            if admin_count == 0:
                print("2. Creando usuario administrador...")
                admin = Admin(
                    username='Ryoma94',
                    password_hash='admin123'  # Se hasheará automáticamente
                )
                db.session.add(admin)
                db.session.commit()
                print("   ✓ Usuario administrador creado: Ryoma94")
            else:
                print("2. Usuario administrador ya existe")
            
            # Agregar vehículos de muestra si no existen
            if vehicle_count == 0:
                print("3. Agregando vehículos de muestra...")
                add_sample_vehicles()
            else:
                print("3. Ya existen vehículos en la base de datos")
            
            print("\n=== INICIALIZACION COMPLETADA ===")
            return True
            
        except Exception as e:
            print(f"❌ Error durante la inicialización: {e}")
            return False

def add_sample_vehicles():
    """Agrega vehículos de muestra para producción"""
    
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
    
    vehicles_added = 0
    
    for vehicle_data in sample_vehicles:
        # Verificar si ya existe
        existing = Vehicle.query.filter_by(title=vehicle_data['title']).first()
        
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
            vehicles_added += 1
            print(f"   ✓ Agregado: {vehicle_data['title']}")
    
    if vehicles_added > 0:
        db.session.commit()
        print(f"   ✓ {vehicles_added} vehículos agregados exitosamente")
        
        # Mostrar estadísticas finales
        total_vehicles = Vehicle.query.count()
        active_vehicles = Vehicle.query.filter_by(is_active=True).count()
        plus_vehicles = Vehicle.query.filter_by(is_plus=True, is_active=True).count()
        
        print(f"\n📊 ESTADISTICAS FINALES:")
        print(f"   - Total de vehículos: {total_vehicles}")
        print(f"   - Vehículos activos: {active_vehicles}")
        print(f"   - Publicaciones Plus: {plus_vehicles}")
    else:
        print("   - No se agregaron vehículos (ya existían)")

if __name__ == '__main__':
    # Verificar que estamos en producción o que se forzó la ejecución
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        print("🚀 Forzando inicialización de base de datos...")
        success = init_production_database()
    elif os.environ.get('DATABASE_URL'):
        print("🌐 Detectado entorno de producción, inicializando...")
        success = init_production_database()
    else:
        print("⚠️  Este script está diseñado para producción.")
        print("   Para ejecutar en desarrollo, usa: python init_production_db.py --force")
        success = False
    
    if success:
        print("\n🎉 ¡Base de datos inicializada correctamente!")
        print("   La aplicación web ahora debería mostrar contenido.")
    else:
        print("\n❌ Error en la inicialización.")
        sys.exit(1)
