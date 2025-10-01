"""Script para agregar campos de sub-ubicación a edit_vehicle.html"""
import re

file_path = 'templates/edit_vehicle.html'

# Leer el archivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# PATCH 1: Agregar sub_location después del campo de color
snippet1 = '''                            
                            <div class="col-md-6 mb-3" id="sub-location-field">
                                <label for="sub_location" class="form-label">
                                    <i class="fas fa-map-pin me-2"></i>Sub-ubicación (barrio/zona)
                                </label>
                                <input type="text" class="form-control" id="sub_location" name="sub_location" 
                                       value="{{ vehicle.sub_location or '' }}" 
                                       placeholder="Vista Flores, Cordón del Plata, Cuadro Benegas...">
                                <div class="form-text">Lugares principales dentro del departamento.</div>
                            </div>
'''

# Buscar después del campo color y antes de tire-condition
pattern1 = r'(name="color"[^>]*>\s*</div>\s*)'
replacement1 = r'\1' + snippet1

# Verificar si ya existe el campo
if 'id="sub-location-field"' not in content:
    content = re.sub(pattern1, replacement1, content, count=1)
    print("[OK] Agregado campo sub_location en seccion de vehiculo")
else:
    print("[INFO] Campo sub_location ya existe en seccion de vehiculo")

# PATCH 2: Agregar user_sub_location después del campo user_location
snippet2 = '''                            <div class="col-md-6 mb-3">
                                <label for="user_sub_location" class="form-label">
                                    <i class="fas fa-thumbtack me-2"></i>Sub-ubicación
                                </label>
                                <input type="text" class="form-control" id="user_sub_location" name="user_sub_location" 
                                       value="{{ vehicle.sub_location or '' }}" 
                                       placeholder="Ciudad, Vista Flores, Cuadro Nacional...">
                            </div>
'''

# Buscar después de user_location y antes de user_address (que usa col-12)
pattern2 = r'(name="user_location"[^>]*>\s*</div>\s*)([\s]*<div class="col-12)'
replacement2 = r'\1' + snippet2 + r'\2'

# Verificar si ya existe el campo
if 'id="user_sub_location"' not in content:
    content = re.sub(pattern2, replacement2, content, count=1)
    print("[OK] Agregado campo user_sub_location en seccion de usuario")
else:
    print("[INFO] Campo user_sub_location ya existe en seccion de usuario")

# Escribir el archivo modificado
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCCESS] Archivo edit_vehicle.html actualizado exitosamente")
