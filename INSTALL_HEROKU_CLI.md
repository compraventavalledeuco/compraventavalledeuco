# Instalación de Heroku CLI

## Opción 1: Descarga directa (Recomendado)
1. Ve a: https://devcenter.heroku.com/articles/heroku-cli
2. Descarga el instalador para Windows
3. Ejecuta el instalador y sigue las instrucciones

## Opción 2: Con winget (requiere confirmación manual)
```cmd
winget install Heroku.CLI
```
Cuando aparezca la pregunta sobre términos, responde "Y" para aceptar.

## Opción 3: Con npm (si tienes Node.js)
```cmd
npm install -g heroku
```

## Verificar instalación
Después de instalar, abre una nueva ventana de comando y ejecuta:
```cmd
heroku --version
```

## Continuar con el despliegue
Una vez instalado Heroku CLI:
1. Ejecuta: `heroku login`
2. Luego ejecuta: `configurar_heroku_supabase.bat`
3. O alternativamente: `setup_heroku_postgres.bat`
