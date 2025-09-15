# Desplegar en Heroku usando GitHub

## Paso 1: Subir código a GitHub

### 1.1 Crear repositorio en GitHub
1. Ve a https://github.com
2. Haz clic en "New repository"
3. Nombre: `compraventa-valle-uco`
4. Descripción: `Marketplace de vehículos del Valle de Uco`
5. **NO** marques "Initialize with README"
6. Haz clic en "Create repository"

### 1.2 Conectar y subir tu código
Ejecuta estos comandos en tu terminal (reemplaza TU-USUARIO con tu nombre de usuario de GitHub):

```bash
# Conectar con GitHub (reemplaza TU-USUARIO)
git remote add origin https://github.com/TU-USUARIO/compraventa-valle-uco.git

# Subir el código
git branch -M main
git push -u origin main
```

## Paso 2: Crear aplicación en Heroku

### 2.1 Crear cuenta y app
1. Ve a https://heroku.com
2. Crea una cuenta gratuita
3. Haz clic en "Create new app"
4. Nombre: `compraventa-valle-uco` (o similar si está ocupado)
5. Región: United States
6. Haz clic en "Create app"

### 2.2 Conectar con GitHub
1. En tu app de Heroku, ve a la pestaña "Deploy"
2. En "Deployment method", selecciona "GitHub"
3. Conecta tu cuenta de GitHub
4. Busca tu repositorio: `compraventa-valle-uco`
5. Haz clic en "Connect"

## Paso 3: Configurar variables de entorno

En tu app de Heroku, ve a "Settings" > "Config Vars" y agrega:

```
SESSION_SECRET = valle-uco-marketplace-secret-key-2024
ADMIN_PASSWORD = AdminValleUco2024
```

## Paso 4: Agregar base de datos

1. Ve a "Resources" en tu app de Heroku
2. En "Add-ons", busca "Heroku Postgres"
3. Selecciona el plan gratuito "Hobby Dev - Free"
4. Haz clic en "Submit Order Form"

## Paso 5: Desplegar

1. Ve a la pestaña "Deploy"
2. En la sección "Manual deploy":
   - Selecciona la rama "main"
   - Haz clic en "Deploy Branch"
3. Espera a que termine el despliegue

## Paso 6: Inicializar base de datos

1. Ve a "More" > "Run console"
2. Ejecuta: `python -c "from app import app, db; app.app_context().push(); db.create_all()"`

## ¡Listo! 🎉

Tu aplicación estará disponible en:
`https://tu-app-name.herokuapp.com`

### Actualizaciones futuras
Para actualizar tu aplicación:
1. Haz cambios en tu código local
2. `git add .`
3. `git commit -m "Descripción de cambios"`
4. `git push origin main`
5. Heroku desplegará automáticamente (si tienes habilitado "Automatic deploys")
