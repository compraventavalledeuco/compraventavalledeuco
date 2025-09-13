#!/usr/bin/env python3
"""
Script para actualizar y probar nueva URL de Supabase
"""
import os
from sqlalchemy import create_engine, text

def test_new_url():
    """Test with the new Supabase URL"""
    print("🔧 Actualiza tu URL de Supabase aquí:")
    print("="*50)
    print("1. Ve a: https://supabase.com/dashboard")
    print("2. Selecciona tu proyecto")
    print("3. Ve a Settings → Database")
    print("4. Copia la 'Connection string'")
    print("5. Reemplaza la URL abajo y ejecuta este script")
    print("="*50)
    
    # PROBANDO DIFERENTES FORMATOS
    # Formato 1: Connection Pooling con formato correcto
    new_url = "postgresql://postgres.vibodlvywbxfthxejshd:DiegoPortaz1994@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
    
    print("🔧 DIAGNÓSTICO DEL PROBLEMA:")
    print("Error 'Tenant or user not found' indica:")
    print("1. El servidor responde (conexión OK)")
    print("2. Problema con credenciales o estado del proyecto")
    print()
    print("VERIFICA EN TU DASHBOARD:")
    print("✓ Proyecto está ACTIVO (no pausado)")
    print("✓ Contraseña es correcta")
    print("✓ Project ID es correcto")
    print()
    
    print(f"\n🔍 URL actual para probar:")
    print(f"   {new_url}")
    
    if "XXXXXX" in new_url or "[TU-PASSWORD]" in new_url:
        print("\n❌ Por favor actualiza la URL con los datos correctos de tu dashboard de Supabase")
        print("\n💡 La URL correcta debería verse así:")
        print("   postgresql://postgres.abc123:[PASSWORD]@aws-0-region.pooler.supabase.com:6543/postgres")
        return False
    
    try:
        engine = create_engine(new_url, pool_pre_ping=True)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 'Conexión exitosa con nueva URL!' as message;"))
            message = result.fetchone()[0]
            print(f"\n✅ {message}")
            print("\n🎉 ¡URL correcta! Ahora actualiza tu variable de entorno DATABASE_URL")
            return True
            
    except Exception as e:
        print(f"\n❌ Error con nueva URL: {str(e)}")
        return False

if __name__ == "__main__":
    test_new_url()
