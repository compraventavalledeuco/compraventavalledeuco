# Configuración de AWS S3 para Heroku - Solución a Archivos que Desaparecen

## Problema
En Heroku, las imágenes y backups desaparecen porque el sistema de archivos es **efímero**:
- Se borra cada 24 horas (restart automático)
- Se borra en cada deploy
- Se borra durante mantenimiento

## Solución: AWS S3

### 1. Crear Bucket en AWS S3

1. Ve a [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Crea un nuevo bucket:
   - Nombre: `compraventavalledeuco-storage` (debe ser único globalmente)
   - Región: `us-east-1` (recomendado)
   - Desbloquear acceso público para las imágenes
3. En "Permissions" > "Bucket Policy", agregar:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::compraventavalledeuco-storage/uploads/*"
        }
    ]
}
```

### 2. Crear Usuario IAM

1. Ve a [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Crear nuevo usuario:
   - Nombre: `heroku-app-user`
   - Tipo: Programmatic access
3. Asignar política personalizada:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::compraventavalledeuco-storage",
                "arn:aws:s3:::compraventavalledeuco-storage/*"
            ]
        }
    ]
}
```

4. Guardar las credenciales: `Access Key ID` y `Secret Access Key`

### 3. Configurar Variables de Entorno en Heroku

```bash
heroku config:set S3_BUCKET_NAME="compraventavalledeuco-storage"
heroku config:set AWS_ACCESS_KEY_ID="tu-access-key-id"
heroku config:set AWS_SECRET_ACCESS_KEY="tu-secret-access-key"
heroku config:set AWS_DEFAULT_REGION="us-east-1"
```

### 4. Actualizar requirements.txt

Agregar a `requirements.txt`:
```
boto3==1.34.0
```

### 5. Deploy de los Cambios

```bash
git add .
git commit -m "Add S3 cloud storage integration to fix ephemeral filesystem issue"
git push origin main
```

Luego hacer deploy en Heroku desde GitHub.

## Beneficios

✅ **Imágenes permanentes**: No se borran nunca
✅ **Backups seguros**: Almacenados en S3
✅ **Mejor rendimiento**: CDN de AWS
✅ **Escalabilidad**: Sin límites de almacenamiento
✅ **Costo bajo**: Solo pagas por lo que usas

## Costos Estimados

- **S3 Standard**: ~$0.023 por GB/mes
- **Requests**: ~$0.0004 por 1000 requests
- **Para 1000 imágenes (~1GB)**: ~$0.50/mes

## Próximos Pasos

1. Configurar AWS S3 siguiendo esta guía
2. Actualizar el código para usar S3 en lugar del filesystem local
3. Migrar imágenes existentes (si las hay) a S3
4. Configurar backups automáticos en S3
