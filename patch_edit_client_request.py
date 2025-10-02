"""Script para agregar 18 departamentos y campo de sub-ubicacion a edit_client_request.html"""
import re

file_path = 'templates/edit_client_request.html'

# Leer el archivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Texto viejo a reemplazar
old_pattern = '''                            <div class="col-md-6 mb-3">
                                <label for="location" class="form-label">
                                    <i class="fas fa-map-marker-alt me-2"></i>Ubicación *
                                </label>
                                <select class="form-select" id="location" name="location" required>
                                    <option value="">Seleccionar ubicación...</option>
                                    <option value="Tunuyán" {{ "selected" if client_request.location == "Tunuyán" else "" }}>Tunuyán</option>
                                    <option value="Tupungato" {{ "selected" if client_request.location == "Tupungato" else "" }}>Tupungato</option>
                                    <option value="San Carlos" {{ "selected" if client_request.location == "San Carlos" else "" }}>San Carlos</option>
                                </select>
                                <div class="invalid-feedback">Por favor selecciona la ubicación.</div>
                            </div>
                            
                            <div class="col-12 mb-3">'''

# Nuevo texto con 18 departamentos + sub-ubicacion
new_pattern = '''                            <div class="col-md-6 mb-3">
                                <label for="location" class="form-label">
                                    <i class="fas fa-map-marker-alt me-2"></i>Departamento *
                                </label>
                                <select class="form-select" id="location" name="location" required>
                                    <option value="">Seleccionar departamento...</option>
                                    <optgroup label="Valle de Uco">
                                        <option value="Tunuyán" {{ "selected" if client_request.location == "Tunuyán" else "" }}>Tunuyán</option>
                                        <option value="Tupungato" {{ "selected" if client_request.location == "Tupungato" else "" }}>Tupungato</option>
                                        <option value="San Carlos" {{ "selected" if client_request.location == "San Carlos" else "" }}>San Carlos</option>
                                    </optgroup>
                                    <optgroup label="Zona Sur">
                                        <option value="San Rafael" {{ "selected" if client_request.location == "San Rafael" else "" }}>San Rafael</option>
                                        <option value="General Alvear" {{ "selected" if client_request.location == "General Alvear" else "" }}>General Alvear</option>
                                        <option value="Malargüe" {{ "selected" if client_request.location == "Malargüe" else "" }}>Malargüe</option>
                                    </optgroup>
                                    <optgroup label="Área Metropolitana">
                                        <option value="Capital" {{ "selected" if client_request.location == "Capital" else "" }}>Capital</option>
                                        <option value="Godoy Cruz" {{ "selected" if client_request.location == "Godoy Cruz" else "" }}>Godoy Cruz</option>
                                        <option value="Guaymallén" {{ "selected" if client_request.location == "Guaymallén" else "" }}>Guaymallén</option>
                                        <option value="Luján de Cuyo" {{ "selected" if client_request.location == "Luján de Cuyo" else "" }}>Luján de Cuyo</option>
                                        <option value="Maipú" {{ "selected" if client_request.location == "Maipú" else "" }}>Maipú</option>
                                    </optgroup>
                                    <optgroup label="Zona Este">
                                        <option value="Rivadavia" {{ "selected" if client_request.location == "Rivadavia" else "" }}>Rivadavia</option>
                                        <option value="Junín" {{ "selected" if client_request.location == "Junín" else "" }}>Junín</option>
                                        <option value="San Martín" {{ "selected" if client_request.location == "San Martín" else "" }}>San Martín</option>
                                    </optgroup>
                                    <optgroup label="Zona Norte">
                                        <option value="Las Heras" {{ "selected" if client_request.location == "Las Heras" else "" }}>Las Heras</option>
                                        <option value="Lavalle" {{ "selected" if client_request.location == "Lavalle" else "" }}>Lavalle</option>
                                    </optgroup>
                                    <optgroup label="Otras Zonas">
                                        <option value="La Paz" {{ "selected" if client_request.location == "La Paz" else "" }}>La Paz</option>
                                        <option value="Santa Rosa" {{ "selected" if client_request.location == "Santa Rosa" else "" }}>Santa Rosa</option>
                                    </optgroup>
                                </select>
                                <div class="invalid-feedback">Por favor selecciona el departamento.</div>
                            </div>
                            
                            <div class="col-md-6 mb-3">
                                <label for="sub_location" class="form-label">
                                    <i class="fas fa-map-pin me-2"></i>Sub-ubicación (Barrio/Zona)
                                </label>
                                <input type="text" class="form-control" id="sub_location" name="sub_location" 
                                       value="{{ client_request.sub_location or '' }}" 
                                       placeholder="Ej: Ciudad, Cuadro Benegas, Vista Flores...">
                                <div class="form-text">Lugar específico dentro del departamento (opcional)</div>
                            </div>
                            
                            <div class="col-12 mb-3">'''

# Reemplazar
if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print("[OK] Actualizado selector de departamentos y agregado campo de sub-ubicacion en edit_client_request.html")
else:
    print("[ERROR] No se encontro el patron exacto")

# Escribir
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCCESS] Archivo edit_client_request.html procesado")
