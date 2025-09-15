@echo off
echo ========================================
echo CONFIGURACION DE HEROKU POSTGRESQL
echo ========================================
echo.
echo 1. Agregando addon de PostgreSQL...
heroku addons:create heroku-postgresql:essential-0 --app tu-app-name

echo.
echo 2. Verificando configuracion...
heroku config --app tu-app-name

echo.
echo 3. Obteniendo informacion de la base de datos...
heroku pg:info --app tu-app-name

echo.
echo ========================================
echo INSTRUCCIONES:
echo 1. Reemplaza 'tu-app-name' con el nombre real de tu app
echo 2. Ejecuta este archivo
echo 3. Heroku automaticamente creara DATABASE_URL
echo ========================================
pause
