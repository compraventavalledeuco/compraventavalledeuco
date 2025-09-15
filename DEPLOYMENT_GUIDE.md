# Guía de Despliegue - Marketplace Valle de Uco

## Cambios Realizados para Solucionar Problemas de Conexión

### ✅ Problema Resuelto: Error "Network is unreachable"

**Causa:** El `db.create_all()` se ejecutaba al iniciar la aplicación, causando fallos cuando Heroku no podía conectar con Supabase.

**Solución:** Se movió la inicialización de base de datos a una función separada que se ejecuta solo cuando es necesario.

### 🔧 Cambios en el Código

1. **app.py - Nueva función `init_database()`:**
   - Maneja la creación de tablas y usuario admin
   - Incluye manejo de errores
   - Se ejecuta solo cuando se solicita explícitamente

2. **Nuevos endpoints y comandos:**
   - `/admin/init-db` - Endpoint para inicializar BD desde el admin
   - `python app.py init-db` - Comando de línea para inicializar BD

3. **Scripts de despliegue actualizados:**
   - Usan el nuevo método de inicialización
   - Incluyen pruebas de conectividad

## 🚀 Opciones de Despliegue

### Opción 1: Continuar con Supabase

```bash
# 1. Probar conectividad
test_db_heroku.bat

# 2. Si funciona, desplegar
configurar_heroku_supabase.bat

# 3. Inicializar BD manualmente si es necesario
init_db_heroku.bat
```

### Opción 2: Cambiar a PostgreSQL de Heroku (Recomendado)

```bash
# Configurar PostgreSQL de Heroku
setup_heroku_postgres.bat
```

**Ventajas de PostgreSQL de Heroku:**
- ✅ Mejor integración con Heroku
- ✅ Red privada, sin problemas de conectividad
- ✅ Configuración automática
- ✅ Backups automáticos
- ✅ Más confiable para producción

## 📋 Pasos Siguientes

1. **Probar conectividad actual:**
   ```bash
   test_db_heroku.bat
   ```

2. **Si Supabase falla, cambiar a Heroku PostgreSQL:**
   ```bash
   setup_heroku_postgres.bat
   ```

3. **Verificar que la aplicación funcione:**
   - Acceder a la URL de Heroku
   - Probar login admin
   - Subir un vehículo de prueba

## 🔍 Comandos de Diagnóstico

```bash
# Ver logs de Heroku
heroku logs --tail --app compraventavalledeuco

# Ver configuración
heroku config --app compraventavalledeuco

# Probar conectividad de BD
heroku run python test_db_connection.py --app compraventavalledeuco

# Inicializar BD manualmente
heroku run python app.py init-db --app compraventavalledeuco
```

## 📝 Notas Importantes

- La aplicación ya no crashea al iniciar
- La inicialización de BD es manual y controlada
- Se incluyen scripts para ambas opciones de BD
- Los logs ahora son más informativos sobre el estado de la conexión

## 🎯 Recomendación

Para mayor confiabilidad, recomiendo usar **PostgreSQL de Heroku** ejecutando `setup_heroku_postgres.bat`. Esto eliminará completamente los problemas de conectividad de red.
