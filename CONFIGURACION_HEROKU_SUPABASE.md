# Configuración Heroku + Supabase

## Variables de entorno configuradas:

### 1. Base de datos Supabase
```
DATABASE_URL = postgresql://postgres:DiegoPortaz1994@db.vibodlvywbxfthxejshd.supabase.co:5432/postgres
```

### 2. Configuración de aplicación
```
SESSION_SECRET = valle-uco-marketplace-secret-key-2024-production
ADMIN_PASSWORD = AdminValleUco2024
```

## Pasos para configurar en Heroku:

### Opción 1: Usar el script automático
Ejecuta: `configurar_heroku_supabase.bat`

### Opción 2: Configuración manual en Heroku Dashboard

1. **Ve a tu app en Heroku**: https://dashboard.heroku.com/apps/compraventavalledeuco

2. **Settings → Config Vars → Reveal Config Vars**

3. **Agrega estas variables**:
   - `DATABASE_URL`: `postgresql://postgres:DiegoPortaz1994@db.vibodlvywbxfthxejshd.supabase.co:5432/postgres`
   - `SESSION_SECRET`: `valle-uco-marketplace-secret-key-2024-production`
   - `ADMIN_PASSWORD`: `AdminValleUco2024`

4. **Deploy → Manual deploy → Deploy Branch**

5. **More → Run console → Ejecuta**:
   ```
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

## URLs de tu aplicación:
- **Aplicación**: https://compraventavalledeuco.herokuapp.com
- **Panel Admin**: https://compraventavalledeuco.herokuapp.com/panel
  - Usuario: `Ryoma94`
  - Password: `AdminValleUco2024`

## Verificación:
- ✅ Repositorio GitHub conectado
- ✅ Variables de entorno configuradas
- ✅ Base de datos Supabase conectada
- ✅ Aplicación lista para desplegar
