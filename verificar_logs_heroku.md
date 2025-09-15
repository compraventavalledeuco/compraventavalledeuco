# Diagnosticar Error en Heroku

## Error: "Application error"

### Posibles causas comunes:

1. **Variables de entorno faltantes**
2. **Error en la conexión a Supabase**
3. **Problema con dependencias**
4. **Error en el código de inicialización**

## Verificar logs en Heroku Dashboard:

### Método 1: Dashboard Web
1. Ve a: https://dashboard.heroku.com/apps/compraventavalledeuco
2. Haz clic en **More** → **View logs**
3. Busca errores en rojo

### Método 2: Verificar Config Vars
1. Ve a **Settings** → **Config Vars**
2. Verifica que estén configuradas:
   - `DATABASE_URL`: `postgresql://postgres:DiegoPortaz1994@db.vibodlvywbxfthxejshd.supabase.co:5432/postgres`
   - `SESSION_SECRET`: tu clave personalizada
   - `ADMIN_PASSWORD`: `DiegoPortaz7`

## Soluciones rápidas:

### Si falta alguna variable:
1. Agrégala en Config Vars
2. La app se reiniciará automáticamente

### Si el error persiste:
1. Ve a **Deploy** → **Manual deploy**
2. Haz clic en **Deploy Branch**
3. Espera a que termine el despliegue

### Verificar conexión a Supabase:
- Asegúrate que la URL de Supabase sea correcta
- Verifica que la base de datos esté activa en Supabase

## Comandos útiles (si tienes Heroku CLI):
```bash
heroku logs --tail --app compraventavalledeuco
heroku restart --app compraventavalledeuco
```
