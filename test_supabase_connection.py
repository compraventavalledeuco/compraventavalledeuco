#!/usr/bin/env python3
"""
Script para probar la conexión a Supabase
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def test_supabase_connection():
    """Test connection to Supabase database"""
    
    # Tu URL de Supabase
    database_url = "postgresql://postgres:DiegoPortaz1994@db.vibodlvywbxfthxejshd.supabase.co:5432/postgres"
    
    print("🔍 Probando conexión a Supabase...")
    print(f"URL: {database_url.replace('DiegoPortaz1994', '***PASSWORD***')}")
    
    try:
        # Crear engine con configuración similar a tu app
        engine = create_engine(
            database_url,
            pool_recycle=300,
            pool_pre_ping=True,
            echo=True  # Para ver las queries SQL
        )
        
        # Probar conexión básica
        print("\n✅ Probando conexión básica...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Conexión exitosa! PostgreSQL version: {version}")
            
            # Probar permisos básicos
            print("\n✅ Probando permisos de base de datos...")
            
            # Listar tablas existentes
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"📋 Tablas existentes ({len(tables)}):")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("📋 No hay tablas en el esquema 'public'")
            
            # Probar creación de tabla temporal
            print("\n✅ Probando permisos de escritura...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    test_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Insertar datos de prueba
            connection.execute(text("""
                INSERT INTO test_connection (test_message) 
                VALUES ('Conexión de prueba exitosa');
            """))
            
            # Leer datos de prueba
            result = connection.execute(text("SELECT * FROM test_connection LIMIT 1;"))
            test_data = result.fetchone()
            print(f"✅ Escritura/Lectura exitosa: {test_data}")
            
            # Limpiar tabla de prueba
            connection.execute(text("DROP TABLE test_connection;"))
            
            connection.commit()
            print("✅ Todas las pruebas pasaron correctamente!")
            
    except SQLAlchemyError as e:
        print(f"❌ Error de SQLAlchemy: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return False
    
    return True

def test_with_environment_variable():
    """Test using environment variable like the app does"""
    print("\n" + "="*50)
    print("🔍 Probando con variable de entorno...")
    
    # Simular como lo hace tu app
    os.environ["DATABASE_URL"] = "postgresql://postgres:DiegoPortaz1994@db.vibodlvywbxfthxejshd.supabase.co:5432/postgres"
    
    database_url = os.environ.get("DATABASE_URL", "sqlite:///vehicle_marketplace.db")
    
    # Fix for Heroku PostgreSQL URL format (como en tu app)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print(f"URL procesada: {database_url.replace('DiegoPortaz1994', '***PASSWORD***')}")
    
    try:
        engine = create_engine(
            database_url,
            pool_recycle=300,
            pool_pre_ping=True
        )
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 'Environment variable test successful' as message;"))
            message = result.fetchone()[0]
            print(f"✅ {message}")
            
    except Exception as e:
        print(f"❌ Error con variable de entorno: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de conexión a Supabase")
    print("="*50)
    
    # Prueba 1: Conexión directa
    success1 = test_supabase_connection()
    
    # Prueba 2: Con variable de entorno
    success2 = test_with_environment_variable()
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"  Conexión directa: {'✅ EXITOSA' if success1 else '❌ FALLÓ'}")
    print(f"  Variable de entorno: {'✅ EXITOSA' if success2 else '❌ FALLÓ'}")
    
    if success1 and success2:
        print("\n🎉 ¡Tu configuración de Supabase está correcta!")
        print("\n💡 PRÓXIMOS PASOS:")
        print("1. Asegúrate de que DATABASE_URL esté configurada en tu plataforma de deployment")
        print("2. Ejecuta: python app.py init-db  (para inicializar las tablas)")
        print("3. Tu aplicación debería funcionar correctamente")
    else:
        print("\n🔧 POSIBLES SOLUCIONES:")
        print("1. Verifica que la contraseña sea correcta")
        print("2. Verifica que la URL de Supabase sea correcta")
        print("3. Verifica que tu proyecto de Supabase esté activo")
        print("4. Revisa los logs de Supabase para más detalles")
    
    print("\n" + "="*50)
