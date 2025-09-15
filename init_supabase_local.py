#!/usr/bin/env python3
"""
Script para inicializar la base de datos Supabase desde máquina local
Ejecutar este script localmente para configurar Supabase con los datos de producción
"""

import os
import sys
from datetime import datetime

# Configurar la URL de Supabase directamente
SUPABASE_URL = "postgresql://postgres:DiegoPortaz1994@db.vibodlvywbxfthxejshd.supabase.co:5432/postgres?sslmode=require"

def init_supabase_database():
    """Inicializa la base de datos Supabase desde máquina local"""
    print("=== INICIALIZANDO BASE DE DATOS SUPABASE ===")
    
    try:
        # Importar dependencias
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        print("1. Conectando a Supabase...")
        conn = psycopg2.connect(SUPABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("   ✓ Conexión exitosa a Supabase")
        
        # Crear tablas
        print("2. Creando tablas de base de datos...")
        
        # Tabla Admin
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(256) NOT NULL
            );
        """)
        
        # Tabla Vehicle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicle (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                price INTEGER NOT NULL,
                currency VARCHAR(3) DEFAULT 'ARS',
                year INTEGER,
                brand VARCHAR(100),
                model VARCHAR(100),
                kilometers INTEGER,
                fuel_type VARCHAR(50),
                transmission VARCHAR(50),
                color VARCHAR(50),
                images TEXT,
                main_image_index INTEGER DEFAULT 0,
                whatsapp_number VARCHAR(20),
                call_number VARCHAR(20),
                contact_type VARCHAR(20) DEFAULT 'whatsapp',
                phone_number VARCHAR(20),
                is_active BOOLEAN DEFAULT TRUE,
                is_plus BOOLEAN DEFAULT TRUE,
                premium_duration_months INTEGER DEFAULT 1,
                premium_expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location VARCHAR(50),
                tire_condition VARCHAR(50),
                client_request_id INTEGER
            );
        """)
        
        # Tabla Click
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS click (
                id SERIAL PRIMARY KEY,
                vehicle_id INTEGER REFERENCES vehicle(id) ON DELETE CASCADE,
                click_type VARCHAR(50) NOT NULL,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT
            );
        """)
        
        # Tabla VehicleView
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_view (
                id SERIAL PRIMARY KEY,
                vehicle_id INTEGER REFERENCES vehicle(id) ON DELETE CASCADE,
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT
            );
        """)
        
        # Tabla ClientRequest
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_request (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                email VARCHAR(100),
                vehicle_title VARCHAR(200) NOT NULL,
                vehicle_description TEXT NOT NULL,
                price INTEGER,
                currency VARCHAR(3) DEFAULT 'ARS',
                year INTEGER,
                brand VARCHAR(100),
                model VARCHAR(100),
                kilometers INTEGER,
                fuel_type VARCHAR(50),
                transmission VARCHAR(50),
                location VARCHAR(50),
                images TEXT,
                is_processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                notes TEXT
            );
        """)
        
        # Tabla PageVisit
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS page_visit (
                id SERIAL PRIMARY KEY,
                page_name VARCHAR(100) NOT NULL,
                visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT
            );
        """)
        
        # Tabla Gestor
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gestor (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                whatsapp VARCHAR(20),
                email VARCHAR(100),
                location VARCHAR(50),
                specialties TEXT,
                description TEXT,
                profile_image VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        print("   ✓ Tablas creadas exitosamente")
        
        # Verificar si ya existen datos
        cursor.execute("SELECT COUNT(*) FROM vehicle")
        vehicle_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) FROM admin")
        admin_count = cursor.fetchone()['count']
        
        print(f"   - Vehículos existentes: {vehicle_count}")
        print(f"   - Administradores existentes: {admin_count}")
        
        # Crear usuario administrador si no existe
        if admin_count == 0:
            print("3. Creando usuario administrador...")
            # Hash simple para el password (en producción usar bcrypt)
            import hashlib
            import secrets
            
            password = "admin123"
            salt = secrets.token_hex(16)
            salted_password = password + salt
            password_hash = hashlib.sha256(salted_password.encode()).hexdigest()
            full_hash = salt + password_hash
            
            cursor.execute(
                "INSERT INTO admin (username, password_hash) VALUES (%s, %s)",
                ('Ryoma94', full_hash)
            )
            conn.commit()
            print("   ✓ Usuario administrador creado: Ryoma94")
        else:
            print("3. Usuario administrador ya existe")
        
        # Agregar vehículos de muestra si no existen
        if vehicle_count == 0:
            print("4. Agregando vehículos de muestra...")
            add_sample_vehicles(cursor, conn)
        else:
            print("4. Ya existen vehículos en la base de datos")
        
        cursor.close()
        conn.close()
        
        print("\n=== INICIALIZACION COMPLETADA ===")
        return True
        
    except ImportError:
        print("Error: psycopg2 no esta instalado")
        print("   Instala con: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"Error durante la inicializacion: {e}")
        return False

def add_sample_vehicles(cursor, conn):
    """Agrega vehículos de muestra a Supabase"""
    
    sample_vehicles = [
        ('Toyota Corolla 2020 - Excelente Estado', 'Toyota', 'Corolla', 2020, 8500000, 'ARS', 
         'Toyota Corolla 2020 en excelente estado. Único dueño, service oficial completo. Motor 1.8 CVT, muy económico.',
         'Nafta', 'Automática', 45000, '2622581554', '2622581554', 'whatsapp', True, True, 'Tupungato'),
        
        ('Ford Focus 2018 - Titanium', 'Ford', 'Focus', 2018, 6200000, 'ARS',
         'Ford Focus Titanium 2018. Full equipo, cuero, climatizador automático, excelente estado general.',
         'Nafta', 'Manual', 78000, '2622581554', '2622581554', 'whatsapp', False, True, 'Tunuyán'),
        
        ('Chevrolet Onix 2021 - Como Nuevo', 'Chevrolet', 'Onix', 2021, 7800000, 'ARS',
         'Chevrolet Onix 2021 prácticamente nuevo. Pocos kilómetros, garantía vigente.',
         'Nafta', 'Manual', 15000, '2622581554', '2622581554', 'phone', True, True, 'San Carlos'),
        
        ('Volkswagen Gol 2019 - Trend', 'Volkswagen', 'Gol', 2019, 4500000, 'ARS',
         'VW Gol Trend 2019. Muy cuidado, ideal primer auto. Económico y confiable.',
         'Nafta', 'Manual', 62000, '2622581554', '2622581554', 'whatsapp', False, True, 'Tupungato'),
        
        ('Fiat Cronos 2020 - Drive', 'Fiat', 'Cronos', 2020, 5900000, 'ARS',
         'Fiat Cronos Drive 2020. Excelente relación precio-calidad. Muy espacioso.',
         'Nafta', 'Manual', 55000, '2622581554', '2622581554', 'both', True, True, 'Tunuyán')
    ]
    
    vehicles_added = 0
    
    for vehicle_data in sample_vehicles:
        # Verificar si ya existe
        cursor.execute("SELECT COUNT(*) FROM vehicle WHERE title = %s", (vehicle_data[0],))
        exists = cursor.fetchone()['count'] > 0
        
        if not exists:
            cursor.execute("""
                INSERT INTO vehicle (
                    title, brand, model, year, price, currency, description,
                    fuel_type, transmission, kilometers, whatsapp_number, call_number,
                    contact_type, is_plus, is_active, location, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, vehicle_data + (datetime.utcnow(), datetime.utcnow()))
            
            vehicles_added += 1
            print(f"   ✓ Agregado: {vehicle_data[0]}")
    
    if vehicles_added > 0:
        conn.commit()
        print(f"   ✓ {vehicles_added} vehículos agregados exitosamente")
        
        # Mostrar estadísticas finales
        cursor.execute("SELECT COUNT(*) FROM vehicle")
        total_vehicles = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) FROM vehicle WHERE is_active = TRUE")
        active_vehicles = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) FROM vehicle WHERE is_plus = TRUE AND is_active = TRUE")
        plus_vehicles = cursor.fetchone()['count']
        
        print(f"\nESTADISTICAS FINALES:")
        print(f"   - Total de vehiculos: {total_vehicles}")
        print(f"   - Vehiculos activos: {active_vehicles}")
        print(f"   - Publicaciones Plus: {plus_vehicles}")
    else:
        print("   - No se agregaron vehículos (ya existían)")

if __name__ == '__main__':
    print("Inicializando base de datos Supabase desde maquina local...")
    success = init_supabase_database()
    
    if success:
        print("\nBase de datos Supabase inicializada correctamente!")
        print("   La aplicacion web en Heroku ahora deberia funcionar con Supabase.")
    else:
        print("\nError en la inicializacion.")
        sys.exit(1)
