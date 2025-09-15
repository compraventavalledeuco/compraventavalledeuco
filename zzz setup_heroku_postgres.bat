@echo off
echo ========================================
echo Configurando PostgreSQL de Heroku
echo ========================================

echo.
echo Agregando addon PostgreSQL de Heroku...
heroku addons:create heroku-postgresql:mini --app compraventavalledeuco

echo.
echo Configurando variables de entorno...
heroku config:set SESSION_SECRET=tu_clave_secreta_muy_larga_y_segura_2024 --app compraventavalledeuco
heroku config:set ADMIN_PASSWORD=DiegoPortaz7 --app compraventavalledeuco

echo.
echo Verificando configuracion...
heroku config --app compraventavalledeuco

echo.
echo Desplegando aplicacion...
git add .
git commit -m "Configuracion para PostgreSQL de Heroku"
git push heroku main

echo.
echo Inicializando base de datos...
heroku run python app.py init-db --app compraventavalledeuco

echo.
echo Abriendo aplicacion...
heroku open --app compraventavalledeuco

echo.
echo ========================================
echo CONFIGURACION COMPLETADA!
echo PostgreSQL de Heroku configurado exitosamente
echo ========================================
pause
