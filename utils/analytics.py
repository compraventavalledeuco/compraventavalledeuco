"""
Analytics and Anti-Fraud System
Maneja tracking de vistas, detección de fraude y estadísticas
"""

import hashlib
import re
from datetime import datetime, timedelta
from flask import request
from models import db, VehicleView

# Configuración del sistema anti-fraude
COOLDOWN_MINUTES = 180  # Tiempo mínimo entre vistas del mismo vehículo por IP (3 horas)
MAX_VIEWS_PER_DAY = 10  # Máximo de vistas al día por IP del mismo vehículo
RATE_LIMIT_MINUTES = 5  # Ventana de tiempo para detectar spam
RATE_LIMIT_MAX = 15  # Máximo de vistas en la ventana de tiempo


def generate_session_id(ip_address, user_agent):
    """
    Genera un ID único de sesión basado en IP + User Agent
    Esto ayuda a identificar usuarios únicos más allá de solo la IP
    """
    raw_string = f"{ip_address}:{user_agent}"
    return hashlib.sha256(raw_string.encode()).hexdigest()


def parse_user_agent(user_agent_string):
    """
    Extrae información del User-Agent: dispositivo, navegador, OS
    Usando regex simple para no depender de librerías externas inicialmente
    """
    if not user_agent_string:
        return {
            'device_type': 'unknown',
            'browser': 'unknown',
            'os': 'unknown'
        }
    
    ua_lower = user_agent_string.lower()
    
    # Detectar tipo de dispositivo
    if 'mobile' in ua_lower or 'android' in ua_lower or 'iphone' in ua_lower:
        device_type = 'mobile'
    elif 'tablet' in ua_lower or 'ipad' in ua_lower:
        device_type = 'tablet'
    else:
        device_type = 'desktop'
    
    # Detectar navegador
    if 'edg' in ua_lower:
        browser = 'Edge'
    elif 'chrome' in ua_lower:
        browser = 'Chrome'
    elif 'firefox' in ua_lower:
        browser = 'Firefox'
    elif 'safari' in ua_lower and 'chrome' not in ua_lower:
        browser = 'Safari'
    elif 'opera' in ua_lower or 'opr' in ua_lower:
        browser = 'Opera'
    else:
        browser = 'Other'
    
    # Detectar sistema operativo
    if 'windows' in ua_lower:
        os = 'Windows'
    elif 'mac' in ua_lower:
        os = 'macOS'
    elif 'iphone' in ua_lower or 'ipad' in ua_lower:
        os = 'iOS'
    elif 'android' in ua_lower:
        os = 'Android'
    elif 'linux' in ua_lower:
        os = 'Linux'
    else:
        os = 'Other'
    
    return {
        'device_type': device_type,
        'browser': browser,
        'os': os
    }


def should_count_view(vehicle_id, ip_address):
    """
    Determina si se debe contar la vista según las reglas anti-fraude
    
    Returns:
        tuple: (should_count: bool, reason: str or None, is_unique_today: bool)
    """
    now = datetime.utcnow()
    today = now.date()
    
    # 1. Check cooldown - No contar si vio el vehículo hace menos de COOLDOWN_MINUTES
    last_view = VehicleView.query.filter_by(
        vehicle_id=vehicle_id,
        ip_address=ip_address
    ).order_by(VehicleView.timestamp.desc()).first()
    
    if last_view:
        minutes_ago = (now - last_view.timestamp).total_seconds() / 60
        if minutes_ago < COOLDOWN_MINUTES:
            return False, f"cooldown_{int(COOLDOWN_MINUTES - minutes_ago)}min", False
    
    # 2. Check daily limit - No contar si excede el máximo diario
    views_today = VehicleView.query.filter(
        VehicleView.vehicle_id == vehicle_id,
        VehicleView.ip_address == ip_address,
        db.func.date(VehicleView.timestamp) == today
    ).count()
    
    if views_today >= MAX_VIEWS_PER_DAY:
        return False, "daily_limit_exceeded", False
    
    # 3. Check rate limiting - Detectar spam extremo
    rate_limit_window = now - timedelta(minutes=RATE_LIMIT_MINUTES)
    recent_views = VehicleView.query.filter(
        VehicleView.ip_address == ip_address,
        VehicleView.timestamp >= rate_limit_window
    ).count()
    
    if recent_views >= RATE_LIMIT_MAX:
        return False, "rate_limit_spam_detected", False
    
    # 4. Check if es vista única del día
    is_unique = views_today == 0
    
    # Todas las validaciones pasaron
    return True, None, is_unique


def get_location_from_ip(ip_address):
    """
    Obtiene ciudad y país de la IP
    Por ahora retorna None, se puede integrar con ip-api.com o geoip2
    """
    # TODO: Integrar con servicio de geolocalización
    # Por ahora retornamos valores por defecto
    if ip_address and ip_address != '127.0.0.1':
        # En producción, usar:
        # import requests
        # response = requests.get(f'http://ip-api.com/json/{ip_address}')
        # data = response.json()
        # return {'city': data.get('city'), 'country': data.get('country')}
        return {'city': None, 'country': 'Argentina'}  # Default
    return {'city': None, 'country': None}


def create_vehicle_view(vehicle_id, ip_address, user_agent, referrer=None):
    """
    Crea un registro de vista de vehículo con toda la información
    y aplicando las reglas anti-fraude
    
    Returns:
        tuple: (view: VehicleView, counted: bool)
    """
    # Aplicar reglas anti-fraude
    should_count, blocked_reason, is_unique = should_count_view(vehicle_id, ip_address)
    
    # Parse user agent
    ua_info = parse_user_agent(user_agent)
    
    # Get location
    location = get_location_from_ip(ip_address)
    
    # Generate session ID
    session_id = generate_session_id(ip_address, user_agent or '')
    
    # Crear registro de vista
    view = VehicleView(
        vehicle_id=vehicle_id,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id,
        device_type=ua_info['device_type'],
        browser=ua_info['browser'],
        os=ua_info['os'],
        referrer=referrer,
        city=location['city'],
        country=location['country'],
        is_unique_today=is_unique,
        is_counted=should_count,
        blocked_reason=blocked_reason
    )
    
    return view, should_count


def get_vehicle_stats(vehicle_id, days=30):
    """
    Obtiene estadísticas de un vehículo en los últimos N días
    
    Returns:
        dict: Estadísticas del vehículo
    """
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Total de vistas
    total_views = VehicleView.query.filter(
        VehicleView.vehicle_id == vehicle_id,
        VehicleView.timestamp >= from_date
    ).count()
    
    # Vistas contadas (no bloqueadas)
    counted_views = VehicleView.query.filter(
        VehicleView.vehicle_id == vehicle_id,
        VehicleView.timestamp >= from_date,
        VehicleView.is_counted == True
    ).count()
    
    # Vistas bloqueadas
    blocked_views = total_views - counted_views
    
    # Visitantes únicos (IPs únicas)
    unique_visitors = db.session.query(
        db.func.count(db.func.distinct(VehicleView.ip_address))
    ).filter(
        VehicleView.vehicle_id == vehicle_id,
        VehicleView.timestamp >= from_date,
        VehicleView.is_counted == True
    ).scalar()
    
    # Vistas por dispositivo
    device_stats = db.session.query(
        VehicleView.device_type,
        db.func.count(VehicleView.id)
    ).filter(
        VehicleView.vehicle_id == vehicle_id,
        VehicleView.timestamp >= from_date,
        VehicleView.is_counted == True
    ).group_by(VehicleView.device_type).all()
    
    devices = {device: count for device, count in device_stats}
    
    return {
        'total_views': total_views,
        'counted_views': counted_views,
        'blocked_views': blocked_views,
        'unique_visitors': unique_visitors,
        'devices': devices,
        'period_days': days
    }


def get_daily_views(vehicle_id=None, days=30):
    """
    Obtiene vistas por día para gráfico
    
    Args:
        vehicle_id: ID del vehículo (None para todas)
        days: Cantidad de días hacia atrás
    
    Returns:
        list: [{date: '2025-10-01', views: 42, unique: 28}, ...]
    """
    from_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.session.query(
        db.func.date(VehicleView.timestamp).label('date'),
        db.func.count(VehicleView.id).label('views'),
        db.func.count(db.func.distinct(VehicleView.ip_address)).label('unique')
    ).filter(
        VehicleView.timestamp >= from_date,
        VehicleView.is_counted == True
    )
    
    if vehicle_id:
        query = query.filter(VehicleView.vehicle_id == vehicle_id)
    
    results = query.group_by(db.func.date(VehicleView.timestamp)).all()
    
    return [
        {
            'date': str(row.date),
            'views': row.views,
            'unique': row.unique
        }
        for row in results
    ]


def get_top_vehicles(days=30, limit=10):
    """
    Obtiene los vehículos más vistos
    
    Returns:
        list: [(vehicle_id, views_count), ...]
    """
    from_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.session.query(
        VehicleView.vehicle_id,
        db.func.count(VehicleView.id).label('views')
    ).filter(
        VehicleView.timestamp >= from_date,
        VehicleView.is_counted == True
    ).group_by(
        VehicleView.vehicle_id
    ).order_by(
        db.func.count(VehicleView.id).desc()
    ).limit(limit).all()
    
    return [(vehicle_id, views) for vehicle_id, views in results]
