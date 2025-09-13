#!/usr/bin/env python3
"""
Test final con nueva contraseña de Supabase
"""
from sqlalchemy import create_engine, text

def test_with_new_password():
    print("🔧 PASOS PARA RESOLVER EL PROBLEMA:")
    print("="*50)
    print("1. Ve a tu dashboard de Supabase")
    print("2. Settings → Database")
    print("3. Haz clic en 'Reset database password'")
    print("4. Copia la nueva contraseña")
    print("5. Actualiza la línea 'new_password' abajo")
    print("6. Ejecuta este script")
    print("="*50)
    
    # ACTUALIZA ESTA CONTRASEÑA CON LA NUEVA QUE GENERES
    new_password = "TU_NUEVA_CONTRASEÑA_AQUÍ"
    
    print("🔍 INFORMACIÓN CONFIRMADA:")
    print("✅ Proyecto está ACTIVO")
    print("✅ Project ID: vibodlvywbxfthxejshd")
    print("❌ Problema: Contraseña incorrecta")
    print()
    
    if new_password == "TU_NUEVA_CONTRASEÑA_AQUÍ":
        print("\n❌ Por favor actualiza 'new_password' con tu nueva contraseña")
        return False
    
    # Probar ambos formatos
    urls_to_test = [
        f"postgresql://postgres:{new_password}@db.vibodlvywbxfthxejshd.supabase.co:5432/postgres",
        f"postgresql://postgres.vibodlvywbxfthxejshd:{new_password}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
    ]
    
    for i, url in enumerate(urls_to_test, 1):
        print(f"\n🧪 Probando formato {i}...")
        try:
            engine = create_engine(url, pool_pre_ping=True)
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 'Conexión exitosa!' as message;"))
                message = result.fetchone()[0]
                print(f"✅ {message}")
                print(f"✅ URL correcta: {url.replace(new_password, '***PASSWORD***')}")
                return True
        except Exception as e:
            print(f"❌ Formato {i} falló: {str(e)}")
    
    return False

if __name__ == "__main__":
    test_with_new_password()
