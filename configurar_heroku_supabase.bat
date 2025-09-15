@echo off
echo ========================================
echo CONFIGURANDO HEROKU CON SUPABASE
echo ========================================

echo.
echo Configurando variables de entorno en Heroku...

echo.
echo 1. Configurando base de datos Supabase...
heroku config:set DATABASE_URL="postgresql://postgres:DiegoPortaz1994@db.vibodlvywbxfthxejshd.supabase.co:5432/postgres" --app compraventavalledeuco

echo.
echo 2. Configurando clave de sesion...
heroku config:set SESSION_SECRET="valle-uco-marketplace-secret-key-2025-production" --app compraventavalledeuco

echo.
echo 3. Configurando password de administrador...
heroku config:set ADMIN_PASSWORD="DiegoPortaz7" --app compraventavalledeuco

echo.
echo Verificando configuracion...
heroku config --app compraventavalledeuco

echo.
echo Desplegando aplicacion...
heroku git:remote -a compraventavalledeuco
git push heroku main

echo.
echo Inicializando base de datos...
heroku run python app.py init-db --app compraventavalledeuco

echo.
echo Verificando que la aplicacion funcione...
heroku logs --tail --app compraventavalledeuco

echo.
echo ========================================
echo CONFIGURACION COMPLETADA!
echo ========================================
echo.
echo Tu aplicacion esta disponible en:
echo https://compraventavalledeuco.herokuapp.com
echo.
echo Panel de administracion:
echo https://compraventavalledeuco.herokuapp.com/panel
echo Usuario: Ryoma94
echo Password: DiegoPortaz7
echo.
echo Base de datos: Supabase PostgreSQL
echo ========================================

pause
