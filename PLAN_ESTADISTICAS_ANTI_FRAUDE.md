# 📊 Plan de Estadísticas Mejoradas con Sistema Anti-Fraude

## 🎯 Objetivos

1. **Calendario de visualizaciones** por día
2. **Registro detallado** de visitantes con más datos
3. **Sistema anti-fraude** para evitar inflado de vistas
4. **Dashboard visual** con gráficos y métricas

---

## 🔍 Datos que Podemos Recolectar

### Datos Actuales (Ya implementados)
- ✅ IP address
- ✅ User-Agent
- ✅ Timestamp

### Nuevos Datos Propuestos
- 🆕 **Device type** (Mobile, Desktop, Tablet)
- 🆕 **Browser** (Chrome, Firefox, Safari, etc.)
- 🆕 **Operating System** (Windows, iOS, Android, etc.)
- 🆕 **Referrer** (de dónde viene el visitante)
- 🆕 **Session ID** (identificador único de sesión)
- 🆕 **City/Province** (ubicación aproximada por IP)
- 🆕 **Is unique visit** (bandera si es vista única del día)
- 🆕 **View duration** (tiempo en la página)

---

## 🛡️ Sistema Anti-Fraude

### Problema Actual
- Personas entran/salen repetidamente del mismo perfil
- Inflan artificialmente el contador de vistas
- No es justo para vehículos con vistas genuinas

### Soluciones Propuestas

#### 1. **Cooldown por IP (Recomendado)**
```python
# No contar vista si la misma IP vio el vehículo hace menos de 30 minutos
COOLDOWN_MINUTES = 30
```
**Ventajas:**
- Simple de implementar
- Permite vistas legítimas espaciadas
- No afecta a múltiples personas con la misma IP (ej: café, trabajo)

#### 2. **Límite Diario por IP**
```python
# Máximo 5 vistas del mismo vehículo por IP al día
MAX_VIEWS_PER_DAY = 5
```
**Ventajas:**
- Previene spam extremo
- Permite revisar el anuncio varias veces
- Resetea diariamente

#### 3. **Session Fingerprinting**
```python
# Combinar IP + User-Agent + navegador para identificar sesión
session_id = hash(ip + user_agent + browser)
```
**Ventajas:**
- Más preciso que solo IP
- Diferencia usuarios en la misma red
- Dificulta evadir el sistema

#### 4. **Rate Limiting Inteligente**
```python
# Si detectamos > 10 vistas en 5 minutos = posible fraude
# Bloquear IP temporalmente (1 hora)
```
**Ventajas:**
- Detecta comportamiento anómalo
- Penaliza solo a abusadores
- Protección agresiva contra bots

### **Recomendación Final: Combinar Cooldown + Límite Diario**
```python
# Configuración sugerida:
COOLDOWN_MINUTES = 30  # 30 minutos entre vistas del mismo vehículo
MAX_VIEWS_PER_DAY = 10  # Máximo 10 vistas al día por IP
```

---

## 📈 Nuevo Modelo de Datos

### VehicleView (Mejorado)
```python
class VehicleView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    
    # Datos actuales
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NUEVOS CAMPOS
    session_id = db.Column(db.String(64))  # Hash de identificación única
    device_type = db.Column(db.String(20))  # mobile, desktop, tablet
    browser = db.Column(db.String(50))  # Chrome, Firefox, Safari
    os = db.Column(db.String(50))  # Windows, iOS, Android
    referrer = db.Column(db.String(500))  # De dónde viene
    city = db.Column(db.String(100))  # Ciudad aproximada
    country = db.Column(db.String(50))  # País
    is_unique_today = db.Column(db.Boolean, default=False)  # Primera vista del día
    is_counted = db.Column(db.Boolean, default=True)  # Si se contó en stats
    blocked_reason = db.Column(db.String(100))  # Por qué se bloqueó (si aplica)
```

### DailyStats (Nuevo)
```python
class DailyStats(db.Model):
    """Estadísticas agregadas por día"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)  # Día de las stats
    
    # Stats globales
    total_page_visits = db.Column(db.Integer, default=0)
    unique_visitors = db.Column(db.Integer, default=0)  # IPs únicas del día
    
    # Stats por vehículo (JSON)
    vehicle_stats = db.Column(db.Text)  # JSON: {vehicle_id: {views, unique_views, clicks}}
    
    # Stats de dispositivos
    mobile_visitors = db.Column(db.Integer, default=0)
    desktop_visitors = db.Column(db.Integer, default=0)
    tablet_visitors = db.Column(db.Integer, default=0)
    
    # Ubicaciones top
    top_cities = db.Column(db.Text)  # JSON: [{"city": "Mendoza", "count": 50}]
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 🎨 Dashboard de Estadísticas

### Página: `/admin/estadisticas`

#### 1. Vista General
```
┌─────────────────────────────────────────┐
│  Resumen Mensual - Octubre 2025         │
├─────────────────────────────────────────┤
│  Total Visitas: 1,234                   │
│  Visitantes Únicos: 567                 │
│  Vistas Bloqueadas (fraude): 89         │
│  Tasa de Conversión: 12.5%              │
└─────────────────────────────────────────┘
```

#### 2. Calendario de Visualizaciones
```
        Octubre 2025
Lu  Ma  Mi  Ju  Vi  Sá  Do
                1   2   3
    45  67  89  123 156  92
4   5   6   7   8   9   10
78  90  102 134 167 203  145
```
- Color más intenso = más visitas
- Click en día = detalles de ese día

#### 3. Gráfico de Línea Temporal
```
Visitas en los últimos 30 días
│
│     ╭─╮
│    ╭╯ ╰╮   ╭─╮
│   ╭╯   ╰─╮╭╯ ╰╮
│  ╭╯      ╰╯   ╰╮
└──────────────────
  1 5 10 15 20 25 30
```

#### 4. Top Vehículos Más Vistos
```
┌────────────────────────────────────────┐
│ 1. Toyota Corolla 2020       523 vistas│
│ 2. Honda Civic 2019          412 vistas│
│ 3. Ford Focus 2021           378 vistas│
│ 4. Chevrolet Cruze 2018      301 vistas│
│ 5. VW Gol 2020               267 vistas│
└────────────────────────────────────────┘
```

#### 5. Dispositivos y Ubicaciones
```
Dispositivos              Ciudades Top
─────────────            ─────────────
Mobile:    65%           Mendoza:     45%
Desktop:   30%           San Rafael:  20%
Tablet:     5%           Tunuyán:     15%
                         Tupungato:   10%
```

### Página: `/admin/vehiculo/{id}/stats`

#### Estadísticas Por Vehículo
```
┌─────────────────────────────────────────┐
│  Toyota Corolla 2020 - Estadísticas     │
├─────────────────────────────────────────┤
│  Vistas Totales: 523                    │
│  Vistas Únicas (hoy): 42                │
│  Vistas Bloqueadas: 12                  │
│  Clicks WhatsApp: 23                    │
│  Clicks Llamada: 8                      │
│  Tasa Conversión: 5.9%                  │
└─────────────────────────────────────────┘

Visitas por Hora (Hoy)
│
│     ╭─╮
│    ╭╯ ╰╮   
│   ╭╯   ╰─╮
│  ╭╯      ╰╮
└──────────────────
  0  6  12  18  24
```

---

## 🔧 Implementación Técnica

### Paso 1: Actualizar models.py
```python
# Agregar campos a VehicleView
# Crear modelo DailyStats
# Migrar base de datos
```

### Paso 2: Crear utils/analytics.py
```python
def should_count_view(vehicle_id, ip_address):
    """Determina si contar la vista (anti-fraude)"""
    # Check cooldown
    last_view = VehicleView.query.filter_by(
        vehicle_id=vehicle_id,
        ip_address=ip_address
    ).order_by(VehicleView.timestamp.desc()).first()
    
    if last_view:
        minutes_ago = (datetime.utcnow() - last_view.timestamp).total_seconds() / 60
        if minutes_ago < COOLDOWN_MINUTES:
            return False, "cooldown"
    
    # Check daily limit
    today = datetime.utcnow().date()
    views_today = VehicleView.query.filter(
        VehicleView.vehicle_id == vehicle_id,
        VehicleView.ip_address == ip_address,
        db.func.date(VehicleView.timestamp) == today
    ).count()
    
    if views_today >= MAX_VIEWS_PER_DAY:
        return False, "daily_limit"
    
    return True, None

def parse_user_agent(user_agent_string):
    """Extrae device, browser, OS del user agent"""
    from user_agents import parse
    ua = parse(user_agent_string)
    return {
        'device_type': 'mobile' if ua.is_mobile else 'tablet' if ua.is_tablet else 'desktop',
        'browser': ua.browser.family,
        'os': ua.os.family
    }

def get_location_from_ip(ip_address):
    """Obtiene ciudad/país de la IP (usando servicio gratuito)"""
    import requests
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}')
        data = response.json()
        return {
            'city': data.get('city'),
            'country': data.get('country')
        }
    except:
        return {'city': None, 'country': None}
```

### Paso 3: Actualizar routes.py
```python
@app.route('/vehicle/<int:id>')
def vehicle_detail(id):
    vehicle = Vehicle.query.get_or_404(id)
    
    # Anti-fraude check
    ip = request.remote_addr
    should_count, reason = should_count_view(id, ip)
    
    # Parse user agent
    ua_info = parse_user_agent(request.headers.get('User-Agent', ''))
    
    # Get location
    location = get_location_from_ip(ip)
    
    # Registrar vista
    view = VehicleView(
        vehicle_id=id,
        ip_address=ip,
        user_agent=request.headers.get('User-Agent'),
        session_id=generate_session_id(ip, request.headers.get('User-Agent')),
        device_type=ua_info['device_type'],
        browser=ua_info['browser'],
        os=ua_info['os'],
        referrer=request.referrer,
        city=location['city'],
        country=location['country'],
        is_counted=should_count,
        blocked_reason=reason
    )
    db.session.add(view)
    
    # Solo incrementar contador si no es fraude
    if should_count:
        vehicle.views_count = (vehicle.views_count or 0) + 1
    
    db.session.commit()
    
    return render_template('vehicle_detail.html', vehicle=vehicle)
```

### Paso 4: Crear templates/admin_statistics.html
```html
<!-- Dashboard con calendario -->
<!-- Gráficos con Chart.js -->
<!-- Tablas de top vehículos -->
```

---

## 📦 Dependencias Nuevas

```txt
user-agents==2.2.0          # Para parsear user-agent
geoip2==4.7.0               # Para geolocalización (opcional, mejor que API)
python-dateutil==2.8.2      # Para manejo de fechas
```

---

## 🚀 Ventajas del Sistema

### Para el Administrador
✅ **Transparencia total** - Ver exactamente quién visita y cuándo
✅ **Detección de fraude** - Identificar comportamiento sospechoso
✅ **Métricas reales** - Datos confiables para tomar decisiones
✅ **Calendario visual** - Entender patrones de tráfico

### Para los Vendedores
✅ **Vistas justas** - No se inflan artificialmente
✅ **Confianza** - Saben que los números son reales
✅ **Insights** - Ver qué días/horas hay más tráfico

### Anti-Fraude
✅ **Cooldown** - Previene refresh constante
✅ **Límite diario** - Bloquea spam extremo
✅ **Session tracking** - Identifica usuarios únicos
✅ **Registro de bloqueos** - Auditoría de intentos de fraude

---

## 🎯 Próximos Pasos

¿Quieres que implemente este sistema completo? El orden sería:

1. **Actualizar modelos** (5 min)
2. **Crear utilidades anti-fraude** (10 min)
3. **Modificar routes** (10 min)
4. **Crear dashboard** (20 min)
5. **Migrar base de datos** (5 min)
6. **Testing** (10 min)

**Tiempo total estimado: ~1 hora**

¿Empezamos? 🚀
