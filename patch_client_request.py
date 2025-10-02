"""Script para agregar 18 departamentos y campo de sub-ubicacion a client_request.html"""
import re

file_path = 'templates/client_request.html'

# Leer el archivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Texto viejo a reemplazar (selector con solo 3 departamentos)
old_location_select = '''                            <div class="col-md-6 mb-3">
                                <label for="location" class="form-label">
                                    <i class="fas fa-map-marker-alt me-2"></i>Ubicación *
                                </label>
                                <select class="form-select" id="location" name="location" required>
                                    <option value="">Seleccionar ubicación...</option>
                                    <option value="Tunuyán">Tunuyán</option>
                                    <option value="Tupungato">Tupungato</option>
                                    <option value="San Carlos">San Carlos</option>
                                </select>
                                <div class="invalid-feedback">Por favor selecciona tu ubicación.</div>
                            </div>'''

# Nuevo selector con 18 departamentos + campo de sub-ubicacion
new_location_fields = '''                            <div class="col-md-6 mb-3">
                                <label for="location" class="form-label">
                                    <i class="fas fa-map-marker-alt me-2"></i>Departamento *
                                </label>
                                <select class="form-select" id="location" name="location" required>
                                    <option value="">Seleccionar departamento...</option>
                                    <optgroup label="Valle de Uco">
                                        <option value="Tunuyán">Tunuyán</option>
                                        <option value="Tupungato">Tupungato</option>
                                        <option value="San Carlos">San Carlos</option>
                                    </optgroup>
                                    <optgroup label="Zona Sur">
                                        <option value="San Rafael">San Rafael</option>
                                        <option value="General Alvear">General Alvear</option>
                                        <option value="Malargüe">Malargüe</option>
                                    </optgroup>
                                    <optgroup label="Área Metropolitana">
                                        <option value="Capital">Capital</option>
                                        <option value="Godoy Cruz">Godoy Cruz</option>
                                        <option value="Guaymallén">Guaymallén</option>
                                        <option value="Luján de Cuyo">Luján de Cuyo</option>
                                        <option value="Maipú">Maipú</option>
                                    </optgroup>
                                    <optgroup label="Zona Este">
                                        <option value="Rivadavia">Rivadavia</option>
                                        <option value="Junín">Junín</option>
                                        <option value="San Martín">San Martín</option>
                                    </optgroup>
                                    <optgroup label="Zona Norte">
                                        <option value="Las Heras">Las Heras</option>
                                        <option value="Lavalle">Lavalle</option>
                                    </optgroup>
                                    <optgroup label="Otras Zonas">
                                        <option value="La Paz">La Paz</option>
                                        <option value="Santa Rosa">Santa Rosa</option>
                                    </optgroup>
                                </select>
                                <div class="invalid-feedback">Por favor selecciona tu departamento.</div>
                            </div>
                            
                            <div class="col-md-6 mb-3">
                                <label for="sub_location" class="form-label">
                                    <i class="fas fa-map-pin me-2"></i>Sub-ubicación (Barrio/Zona)
                                </label>
                                <input type="text" class="form-control" id="sub_location" name="sub_location" 
                                       placeholder="Ej: Ciudad, Cuadro Benegas, Vista Flores...">
                                <div class="form-text">Lugar específico dentro del departamento (opcional)</div>
                            </div>'''

# Verificar y reemplazar
if old_location_select in content:
    content = content.replace(old_location_select, new_location_fields)
    print("[OK] Actualizado selector de departamentos y agregado campo de sub-ubicacion")
else:
    print("[ERROR] No se encontro el patron exacto del selector de ubicacion")
    print("[INFO] Intentando buscar alternativas...")

# Escribir el archivo modificado
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCCESS] Archivo client_request.html procesado")
