@echo off
echo ========================================
echo SUBIENDO MARKETPLACE VALLE DE UCO A GITHUB
echo ========================================

echo.
echo Configurando repositorio remoto...
git remote set-url origin https://github.com/compraventavalledeuco/compraventavalledeuco.git

echo.
echo Agregando archivos principales de la aplicacion...
git add app.py
git add requirements.txt
git add models.py
git add routes.py

echo.
echo Agregando archivos de configuracion para despliegue...
git add Procfile
git add runtime.txt
git add .gitignore

echo.
echo Agregando templates y archivos estaticos...
git add templates/
git add static/

echo.
echo Agregando documentacion...
git add README.md
git add HEROKU_SETUP.md
git add railway.json
git add render.yaml

echo.
echo Verificando archivos agregados...
git status

echo.
echo Haciendo commit...
git commit -m "Actualizar configuracion de base de datos y archivos esenciales"

echo.
echo Subiendo a GitHub...
git push origin main

echo.
echo ========================================
echo REPOSITORIO ACTUALIZADO EN GITHUB!
echo URL: https://github.com/compraventavalledeuco/compraventavalledeuco
echo ========================================

pause
