import os
import json
import hashlib
import secrets
import logging
from flask import render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import uuid
import base64
import re
from cloudinary_storage import upload_to_cloudinary, delete_from_cloudinary
from app import app, db
from models import Vehicle, Admin, Click, VehicleView, ClientRequest, PageVisit, Gestor
import urllib.parse
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required(f):
    """Decorador para requerir autenticación de administrador"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session or not session.get('admin_logged_in'):
            flash('Acceso denegado. Debes iniciar sesión como administrador.', 'error')
            return redirect(url_for('panel_login'))
        return f(*args, **kwargs)
    return decorated_function

def verify_password_sha256(password, stored_hash):
    """Verifica una contraseña contra su hash SHA-256 almacenado"""
    if len(stored_hash) < 32:  # Salt debe ser al menos 16 bytes (32 hex chars)
        return False
    
    # Extraer salt (primeros 32 caracteres)
    salt = stored_hash[:32]
    
    # Extraer hash (resto de caracteres)
    password_hash = stored_hash[32:]
    
    # Generar hash de la contraseña ingresada
    salted_password = password + salt
    computed_hash = hashlib.sha256(salted_password.encode()).hexdigest()
    
    # Comparar hashes
    return computed_hash == password_hash

def track_page_visit(page_name):
    """Track page visits for analytics"""
    try:
        # Get client information
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user_agent = request.headers.get('User-Agent')
        referrer = request.headers.get('Referer')
        
        # Create page visit record
        visit = PageVisit(
            page=page_name,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer
        )
        
        db.session.add(visit)
        db.session.commit()
    except Exception as e:
        # Log error but don't break the page
        print(f"Error tracking page visit: {e}")
        db.session.rollback()

@app.route('/terminos-y-condiciones')
def terms_conditions():
    from datetime import datetime
    now = datetime.utcnow()
    return render_template('terms_conditions.html', now=now)

@app.route('/')
def index():
    # Track page visit
    track_page_visit('index')
    
    # Get search and filter parameters
    search_query = request.args.get('search', '').strip()
    price_min = request.args.get('price_min', type=int)
    price_max = request.args.get('price_max', type=int)
    brand = request.args.get('brand', '').strip()
    year_min = request.args.get('year_min', type=int)
    year_max = request.args.get('year_max', type=int)
    location = request.args.get('location', '').strip()
    fuel_type = request.args.get('fuel_type', '').strip()
    transmission = request.args.get('transmission', '').strip()
    km_min = request.args.get('km_min', type=int)
    km_max = request.args.get('km_max', type=int)
    
    # Start with base query
    query = Vehicle.query.filter_by(is_active=True)
    
    # Apply search filter
    if search_query:
        search_filter = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Vehicle.title.ilike(search_filter),
                Vehicle.brand.ilike(search_filter),
                Vehicle.model.ilike(search_filter),
                Vehicle.description.ilike(search_filter),
                Vehicle.seller_keyword.ilike(search_filter)
            )
        )
    
    # Apply price filters
    if price_min is not None:
        query = query.filter(Vehicle.price >= price_min)
    if price_max is not None:
        query = query.filter(Vehicle.price <= price_max)
    
    # Apply brand filter
    if brand:
        query = query.filter(Vehicle.brand.ilike(f"%{brand}%"))
    
    # Apply year filters
    if year_min is not None:
        query = query.filter(Vehicle.year >= year_min)
    if year_max is not None:
        query = query.filter(Vehicle.year <= year_max)
    
    # Apply location filter (assuming location is stored in a field)
    if location:
        query = query.filter(Vehicle.title.ilike(f"%{location}%"))
    
    # Apply fuel type filter
    if fuel_type:
        query = query.filter(Vehicle.fuel_type == fuel_type)
    
    # Apply transmission filter
    if transmission:
        query = query.filter(Vehicle.transmission == transmission)
    
    # Apply kilometers filters
    if km_min is not None:
        query = query.filter(Vehicle.kilometers >= km_min)
    if km_max is not None:
        query = query.filter(Vehicle.kilometers <= km_max)
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Order vehicles: Plus first, then Free, then by creation date (newest first)
    all_vehicles = query.order_by(
        Vehicle.is_plus.desc(),  # Plus vehicles first (True > False)
        Vehicle.created_at.desc()  # Then by newest first
    ).all()
    
    # Calculate pagination
    total_vehicles = len(all_vehicles)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    vehicles = all_vehicles[start_index:end_index]
    
    # Calculate pagination info
    total_pages = (total_vehicles + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    # Get most viewed vehicles for the carousel (only Plus publications)
    from sqlalchemy import func
    most_viewed_vehicles = db.session.query(
        Vehicle,
        func.count(VehicleView.id).label('view_count')
    ).outerjoin(VehicleView).filter(
        Vehicle.is_active == True,
        Vehicle.is_plus == True  # Only Plus publications
    ).group_by(Vehicle.id).order_by(
        func.count(VehicleView.id).desc()
    ).limit(10).all()
    
    # Get unique brands for filter dropdown
    unique_brands = db.session.query(Vehicle.brand).filter(
        Vehicle.is_active == True,
        Vehicle.brand.isnot(None),
        Vehicle.brand != ''
    ).distinct().order_by(Vehicle.brand).all()
    brands = [brand[0] for brand in unique_brands]
    
    return render_template('index.html', 
                         vehicles=vehicles, 
                         most_viewed_vehicles=most_viewed_vehicles,
                         brands=brands,
                         pagination={
                             'page': page,
                             'per_page': per_page,
                             'total_vehicles': total_vehicles,
                             'total_pages': total_pages,
                             'has_prev': has_prev,
                             'has_next': has_next,
                             'prev_num': page - 1 if has_prev else None,
                             'next_num': page + 1 if has_next else None
                         },
                         current_filters={
                             'search': search_query,
                             'price_min': price_min,
                             'price_max': price_max,
                             'brand': brand,
                             'year_min': year_min,
                             'year_max': year_max,
                             'location': location,
                             'fuel_type': fuel_type,
                             'transmission': transmission,
                             'km_min': km_min,
                             'km_max': km_max
                         })

@app.route('/api/search')
def api_search():
    """API endpoint for AJAX search"""
    search_query = request.args.get('q', '').strip()
    
    if not search_query:
        return jsonify({'vehicles': []})
    
    # Search in title, brand, model, description, and seller keyword
    search_filter = f"%{search_query}%"
    vehicles = Vehicle.query.filter(
        Vehicle.is_active == True,
        db.or_(
            Vehicle.title.ilike(search_filter),
            Vehicle.brand.ilike(search_filter),
            Vehicle.model.ilike(search_filter),
            Vehicle.description.ilike(search_filter),
            Vehicle.seller_keyword.ilike(search_filter)
        )
    ).limit(10).all()
    
    # Format results for JSON response
    results = []
    for vehicle in vehicles:
        results.append({
            'id': vehicle.id,
            'title': vehicle.title,
            'brand': vehicle.brand,
            'model': vehicle.model,
            'price': vehicle.format_price(),
            'year': vehicle.year,
            'kilometers': vehicle.kilometers,
            'fuel_type': vehicle.fuel_type,
            'image': vehicle.get_main_image(),
            'url': url_for('vehicle_detail', id=vehicle.id)
        })
    
    return jsonify({'vehicles': results})

@app.route('/vehicle/<int:id>')
def vehicle_detail(id):
    vehicle = Vehicle.query.get_or_404(id)
    
    # Track view
    view = VehicleView(
        vehicle_id=vehicle.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:500]
    )
    db.session.add(view)
    db.session.commit()
    
    # Check if seller has multiple vehicles (for share button)
    seller_vehicle_count = 0
    seller_name = "Vendedor"
    
    if vehicle.client_request_id:
        # Get the original client request to find DNI
        client_request = ClientRequest.query.get(vehicle.client_request_id)
        if client_request and client_request.dni:
            # Count vehicles from the same DNI (through client requests)
            seller_requests = ClientRequest.query.filter_by(
                dni=client_request.dni,
                status='approved'
            ).all()
            
            # Count active vehicles from these requests
            for req in seller_requests:
                vehicle_from_request = Vehicle.query.filter_by(
                    client_request_id=req.id,
                    is_active=True
                ).first()
                if vehicle_from_request:
                    seller_vehicle_count += 1
            
            seller_name = client_request.full_name
    
    return render_template('vehicle_detail.html', 
                         vehicle=vehicle, 
                         seller_vehicle_count=seller_vehicle_count,
                         seller_name=seller_name)

@app.route('/track_click/<int:vehicle_id>/<click_type>')
def track_click(vehicle_id, click_type):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Track click
    click = Click(
        vehicle_id=vehicle_id,
        click_type=click_type,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:500]
    )
    db.session.add(click)
    db.session.commit()
    
    # Generate WhatsApp URL
    if click_type == 'whatsapp':
        message = vehicle.get_whatsapp_contact_message()
    elif click_type == 'offer':
        offer_amount = request.args.get('offer', '0')
        try:
            offer_amount = int(offer_amount.replace('.', '').replace(',', ''))
        except:
            offer_amount = 0
        message = vehicle.get_whatsapp_offer_message(offer_amount)
    else:
        message = f"Consulta sobre: {vehicle.title}"
    
    whatsapp_url = f"https://wa.me/{vehicle.whatsapp_number.replace('+', '')}?text={urllib.parse.quote(message)}"
    return redirect(whatsapp_url)


@app.route('/panel', methods=['GET', 'POST'])
def panel_login():
    # Verificar si ya está logueado
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        import time
        
        # Control de intentos fallidos
        failed_attempts = session.get('failed_attempts', 0)
        if failed_attempts >= 5:
            flash('Demasiados intentos fallidos. Intente más tarde.', 'error')
            return render_template('login.html')
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validaciones básicas
        if not username or not password:
            session['failed_attempts'] = failed_attempts + 1
            flash('Acceso denegado', 'error')
            return render_template('login.html')
        
        # Timing constante para prevenir ataques de timing
        start_time = time.time()
        
        admin = Admin.query.filter_by(username=username).first()
        is_valid = False
        
        if admin:
            # Verificar contraseña con SHA-256
            is_valid = verify_password_sha256(password, admin.password_hash)
        else:
            # Ejecutar verificación falsa para mantener timing constante
            verify_password_sha256(password, 'fake_hash_to_maintain_timing')
        
        # Mantener un tiempo mínimo de procesamiento
        elapsed = time.time() - start_time
        if elapsed < 0.5:  # Mínimo 500ms
            time.sleep(0.5 - elapsed)
        
        if is_valid and admin:
            # Log del acceso exitoso
            logging.info(f"Acceso autorizado desde IP: {request.remote_addr}")
            
            session.permanent = True
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            session['failed_attempts'] = 0  # Reset contador
            return redirect(url_for('admin_dashboard'))
        else:
            # Log del intento fallido
            logging.warning(f"Intento de acceso no autorizado desde IP: {request.remote_addr}, UA: {request.headers.get('User-Agent', 'Unknown')}")
            
            session['failed_attempts'] = failed_attempts + 1
            flash('Acceso denegado', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    return redirect(url_for('index'))

@app.route('/admin')
@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('panel_login'))
    
    # Get sorting parameters
    sort_by = request.args.get('sort_by', 'views')  # 'views' or 'clicks'
    sort_order = request.args.get('sort_order', 'desc')  # 'desc' or 'asc'
    
    # Get statistics
    active_vehicles = Vehicle.query.filter_by(is_active=True).count()
    total_vehicles = Vehicle.query.count()
    total_whatsapp_clicks = Click.query.filter_by(click_type='whatsapp').count()
    total_views = VehicleView.query.count()
    pending_requests_count = ClientRequest.query.filter_by(status='pending').count()
    
    # Get page visit statistics
    total_page_visits = PageVisit.query.filter_by(page='index').count()
    today_visits = PageVisit.query.filter(
        PageVisit.page == 'index',
        PageVisit.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    # Most viewed vehicles with dynamic sorting
    from sqlalchemy import func
    
    # Subconsulta para vistas
    views_subquery = db.session.query(
        VehicleView.vehicle_id,
        func.count(VehicleView.id).label('view_count')
    ).group_by(VehicleView.vehicle_id).subquery()
    
    # Subconsulta para clicks
    clicks_subquery = db.session.query(
        Click.vehicle_id,
        func.count(Click.id).label('click_count')
    ).group_by(Click.vehicle_id).subquery()
    
    # Query principal con joins separados
    query = db.session.query(
        Vehicle,
        func.coalesce(views_subquery.c.view_count, 0).label('view_count'),
        func.coalesce(clicks_subquery.c.click_count, 0).label('click_count')
    ).outerjoin(views_subquery, Vehicle.id == views_subquery.c.vehicle_id
    ).outerjoin(clicks_subquery, Vehicle.id == clicks_subquery.c.vehicle_id
    ).filter(Vehicle.is_active == True)
    
    # Apply sorting
    if sort_by == 'clicks':
        if sort_order == 'desc':
            query = query.order_by(func.coalesce(clicks_subquery.c.click_count, 0).desc())
        else:
            query = query.order_by(func.coalesce(clicks_subquery.c.click_count, 0).asc())
    else:  # sort_by == 'views'
        if sort_order == 'desc':
            query = query.order_by(func.coalesce(views_subquery.c.view_count, 0).desc())
        else:
            query = query.order_by(func.coalesce(views_subquery.c.view_count, 0).asc())
    
    most_viewed = query.limit(10).all()
    
    stats = {
        'active_vehicles': active_vehicles,
        'total_vehicles': total_vehicles,
        'total_whatsapp_clicks': total_whatsapp_clicks,
        'total_views': total_views,
        'most_viewed': most_viewed,
        'pending_requests_count': pending_requests_count,
        'total_page_visits': total_page_visits,
        'today_visits': today_visits,
        'sort_by': sort_by,
        'sort_order': sort_order
    }
    
    return render_template('admin_dashboard.html', stats=stats)


@app.route('/admin/edit_vehicle/<int:id>', methods=['GET', 'POST'])
def edit_vehicle(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('panel_login'))
    
    vehicle = Vehicle.query.get_or_404(id)
    
    if request.method == 'POST':
        # Update vehicle data
        price_str = request.form['price'].replace('.', '').replace(',', '').replace(' ', '')
        
        vehicle.title = request.form['title']
        vehicle.description = request.form['description']
        vehicle.price = int(price_str)
        vehicle.currency = request.form.get('currency', 'ARS')
        vehicle.year = int(request.form['year']) if request.form.get('year') else None
        vehicle.mileage = int(request.form['mileage']) if request.form.get('mileage') else None
        vehicle.fuel_type = request.form.get('fuel_type', '')
        vehicle.transmission = request.form.get('transmission', '')
        vehicle.brand = request.form.get('brand', '')
        vehicle.model = request.form.get('model', '')
        vehicle.color = request.form.get('color', '')
        vehicle.tire_condition = request.form.get('tire_condition')
        vehicle.seller_keyword = request.form.get('seller_keyword', '')
        vehicle.doors = int(request.form['doors']) if request.form.get('doors') else None
        vehicle.engine = request.form.get('engine', '')
        vehicle.condition = request.form.get('condition', '')
        vehicle.location = request.form.get('location', '')
        vehicle.phone_number = request.form.get('phone_number', '')
        vehicle.whatsapp_number = request.form.get('whatsapp_number', '')
        vehicle.plan = request.form.get('plan', '')
        
        # Update user information
        vehicle.full_name = request.form.get('user_full_name', '')
        vehicle.dni = request.form.get('user_dni', '')
        vehicle.email = request.form.get('user_email', '')
        vehicle.location = request.form.get('user_location', '')
        vehicle.address = request.form.get('user_address', '')
        
        # Handle image uploads with Cloudinary (Admin UI uses hidden base64 inputs)
        new_image_urls = []
        
        # 1) Process hidden base64 inputs generated by the admin UI
        image_index = 0
        processed_hidden = 0
        while f'vehicle_images_data_{image_index}' in request.form:
            image_data = request.form[f'vehicle_images_data_{image_index}']
            if image_data and image_data.startswith('data:image/'):
                try:
                    # Extract base64 data
                    header, data = image_data.split(',', 1)
                    image_binary = base64.b64decode(data)
                    
                    # Determine extension
                    if 'jpeg' in header or 'jpg' in header:
                        ext = 'jpg'
                    elif 'png' in header:
                        ext = 'png'
                    elif 'webp' in header:
                        ext = 'webp'
                    else:
                        ext = 'jpg'
                    
                    # Unique filename
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    uid = str(uuid.uuid4())[:8]
                    filename = f"admin_{ts}_{uid}.{ext}"
                    
                    # Upload to Cloudinary
                    from io import BytesIO
                    file_obj = BytesIO(image_binary)
                    file_obj.name = filename
                    print(f"[ADMIN EDIT] Uploading hidden image index={image_index} filename={filename}")
                    upload_result = upload_to_cloudinary(file_obj, 'vehicle_images')
                    if upload_result['success']:
                        new_image_urls.append(upload_result['url'])
                        print(f"[ADMIN EDIT] Hidden image uploaded OK -> {upload_result['url']}")
                    else:
                        flash(f"Error subiendo imagen {image_index}: {upload_result['error']}", 'error')
                        print(f"[ADMIN EDIT] Hidden image upload ERROR -> {upload_result['error']}")
                except Exception as e:
                    print(f"Error procesando imagen {image_index}: {e}")
                processed_hidden += 1
            image_index += 1
        print(f"[ADMIN EDIT] Hidden images found: {processed_hidden}")
        
        # 2) Fallback: if no hidden images, check traditional file input 'vehicle_images'
        if not new_image_urls and 'vehicle_images' in request.files:
            files = request.files.getlist('vehicle_images') if hasattr(request.files, 'getlist') else [request.files.get('vehicle_images')]
            print(f"[ADMIN EDIT] Fallback file input count: {len([f for f in files if getattr(f, 'filename', '')])}")
            for file in files:
                if file and getattr(file, 'filename', ''):
                    print(f"[ADMIN EDIT] Uploading file input: {file.filename}")
                    upload_result = upload_to_cloudinary(file, 'vehicle_images')
                    if upload_result['success']:
                        new_image_urls.append(upload_result['url'])
                        print(f"[ADMIN EDIT] File image uploaded OK -> {upload_result['url']}")
                    else:
                        flash(f"Error subiendo imagen: {upload_result['error']}", 'error')
                        print(f"[ADMIN EDIT] File image upload ERROR -> {upload_result['error']}")
        
        # 3) Persist results: update gallery and main index if we uploaded new images
        if new_image_urls:
            vehicle.images = json.dumps(new_image_urls)
            # Backward-compat: also map first 10 to image_1..image_10
            for idx, url in enumerate(new_image_urls[:10], start=1):
                setattr(vehicle, f'image_{idx}', url)
            # Set main image index
            try:
                main_image_index = int(request.form.get('main_image_index', 0))
                if main_image_index < 0 or main_image_index >= len(new_image_urls):
                    main_image_index = 0
                vehicle.main_image_index = main_image_index
            except (ValueError, TypeError):
                vehicle.main_image_index = 0
            print(f"[ADMIN EDIT] Saved {len(new_image_urls)} images to gallery. main_image_index={vehicle.main_image_index}")
        else:
            print("[ADMIN EDIT] No new images uploaded in this request")
        
        db.session.commit()
        flash('Vehículo actualizado exitosamente', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_vehicle.html', vehicle=vehicle)

@app.route('/admin/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    
    try:
        print(f"DEBUG: Editing user with ID: {user_id}")
        print(f"DEBUG: Form data: {dict(request.form)}")
        
        # Find the client request by user_id
        client_request = ClientRequest.query.get_or_404(user_id)
        print(f"DEBUG: Found client request: {client_request.full_name}")
        
        # Update user information in ClientRequest
        client_request.full_name = request.form.get('full_name', '')
        client_request.dni = request.form.get('dni', '')
        client_request.email = request.form.get('email', '')
        client_request.phone_number = request.form.get('phone_number', '')
        client_request.location = request.form.get('location', '')
        client_request.address = request.form.get('address', '')
        
        print(f"DEBUG: Updated client request data: {client_request.full_name}, {client_request.phone_number}")
        
        # Also update all vehicles associated with this client request
        vehicles = Vehicle.query.filter_by(client_request_id=user_id).all()
        print(f"DEBUG: Found {len(vehicles)} vehicles to update")
        
        for vehicle in vehicles:
            vehicle.full_name = client_request.full_name
            vehicle.dni = client_request.dni
            vehicle.email = client_request.email
            vehicle.phone_number = client_request.phone_number
            vehicle.location = client_request.location
            vehicle.address = client_request.address
        
        db.session.commit()
        print("DEBUG: Changes committed successfully")
        
        return jsonify({'success': True, 'message': 'Usuario actualizado exitosamente'})
        
    except Exception as e:
        print(f"DEBUG: Error occurred: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/delete_vehicle/<int:id>', methods=['POST'])
def delete_vehicle(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('panel_login'))
    
    vehicle = Vehicle.query.get_or_404(id)
    
    print(f"🔍 DEBUG: Vehicle images field: {vehicle.images}")
    print(f"🔍 DEBUG: Vehicle images type: {type(vehicle.images)}")
    
    if vehicle.images:
        try:
            image_urls = json.loads(vehicle.images)
            print(f"🔍 DEBUG: Parsed JSON images: {image_urls}")
        except Exception as e:
            print(f"🔍 DEBUG: JSON parse failed: {e}, treating as single string")
            image_urls = [vehicle.images]
        
        print(f"🔍 DEBUG: Processing {len(image_urls)} images")
        
        for i, image_url in enumerate(image_urls):
            print(f"🔍 DEBUG: Processing image {i+1}: {image_url}")
            
            # Delete from Cloudinary if it's a Cloudinary URL
            if 'cloudinary.com' in image_url or 'res.cloudinary.com' in image_url:
                print(f"🔍 DEBUG: Detected Cloudinary URL: {image_url}")
                try:
                    # Extract public_id from Cloudinary URL
                    # URL format: https://res.cloudinary.com/cloud_name/image/upload/v123456/folder/public_id.ext
                    url_parts = image_url.split('/')
                    print(f"🔍 DEBUG: URL parts: {url_parts}")
                    
                    if len(url_parts) >= 2:
                        # Find the part after 'upload' or 'upload/v123456'
                        upload_index = -1
                        for j, part in enumerate(url_parts):
                            if part == 'upload':
                                upload_index = j
                                break
                        
                        print(f"🔍 DEBUG: Upload index found at: {upload_index}")
                        
                        if upload_index != -1:
                            # Get everything after upload (skip version if present)
                            remaining_parts = url_parts[upload_index + 1:]
                            print(f"🔍 DEBUG: Remaining parts after upload: {remaining_parts}")
                            
                            if remaining_parts and remaining_parts[0].startswith('v'):
                                # Skip version number
                                remaining_parts = remaining_parts[1:]
                                print(f"🔍 DEBUG: After skipping version: {remaining_parts}")
                            
                            if remaining_parts:
                                # Join the remaining parts and remove file extension
                                public_id = '/'.join(remaining_parts)
                                public_id = os.path.splitext(public_id)[0]  # Remove extension
                                
                                print(f"🗑️ Attempting to delete Cloudinary image with public_id: {public_id}")
                                success = delete_from_cloudinary(public_id)
                                if success:
                                    print(f"✅ Successfully deleted from Cloudinary: {public_id}")
                                else:
                                    print(f"❌ Failed to delete from Cloudinary: {public_id}")
                            else:
                                print(f"❌ No remaining parts to form public_id")
                        else:
                            print(f"❌ 'upload' not found in URL parts")
                    else:
                        print(f"❌ URL has insufficient parts: {len(url_parts)}")
                except Exception as e:
                    print(f"❌ Error deleting Cloudinary image {image_url}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Also try to delete from local filesystem (legacy support)
            elif image_url.startswith('uploads/'):
                print(f"🔍 DEBUG: Processing local image: {image_url}")
                image_path = os.path.join('static', image_url)
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        print(f"🗑️ Deleted local image: {image_path}")
                    except OSError as e:
                        print(f"❌ Error deleting local image {image_path}: {e}")
                else:
                    print(f"🔍 DEBUG: Local file not found: {image_path}")
            else:
                print(f"🔍 DEBUG: Skipping image (not Cloudinary or local): {image_url}")
    else:
        print("🔍 DEBUG: No images found in vehicle.images")
    
    # Delete related VehicleView records first
    VehicleView.query.filter_by(vehicle_id=id).delete()
    
    # Delete related Click records
    Click.query.filter_by(vehicle_id=id).delete()
    
    # Delete vehicle from database
    db.session.delete(vehicle)
    db.session.commit()
    
    flash('Vehículo eliminado exitosamente', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/solicitar-publicacion', methods=['GET', 'POST'])
def client_request():
    if request.method == 'POST':
        # Handle form submission
        price_str = request.form['price'].replace('.', '').replace(',', '').replace(' ', '')
        
        # Validate price range (PostgreSQL integer limit is ~2.1 billion)
        try:
            price_value = int(price_str)
            if price_value < 0:
                flash('El precio no puede ser negativo', 'danger')
                return render_template('client_request.html')
            if price_value > 2000000000:  # 2 billion limit
                flash('El precio es demasiado alto. Máximo permitido: $2.000.000.000', 'danger')
                return render_template('client_request.html')
        except ValueError:
            flash('El precio debe ser un número válido', 'danger')
            return render_template('client_request.html')
        
        # Handle contact numbers - add +549 prefix automatically
        whatsapp_number = request.form.get('whatsapp_number', '').strip()
        call_number = request.form.get('call_number', '').strip()
        
        # Add +549 prefix if numbers are provided
        if whatsapp_number:
            whatsapp_number = f"+549{whatsapp_number}"
        if call_number:
            call_number = f"+549{call_number}"
        
        # Ensure at least one contact number is provided
        if not request.form.get('whatsapp_number', '').strip() and not request.form.get('call_number', '').strip():
            flash('Debes proporcionar al menos un número de contacto (WhatsApp o llamada)', 'danger')
            return render_template('client_request.html')
        
        # Optional seller keyword
        seller_keyword = request.form.get('seller_keyword', '').strip()
        dni_clean = request.form['dni'].replace('.', '')  # Remove dots from DNI
        
        # Check if this DNI already has a different seller_keyword
        if seller_keyword:
            existing_requests = ClientRequest.query.filter_by(dni=dni_clean).all()
            if existing_requests:
                # Update all existing requests from this DNI to use the new seller_keyword
                for existing_req in existing_requests:
                    if existing_req.seller_keyword != seller_keyword:
                        existing_req.seller_keyword = seller_keyword
                        
                        # Also update any vehicles associated with those requests
                        vehicles_to_update = Vehicle.query.filter_by(client_request_id=existing_req.id).all()
                        for vehicle in vehicles_to_update:
                            vehicle.seller_keyword = seller_keyword
                
                db.session.commit()

        client_request = ClientRequest(
            full_name=request.form['full_name'],
            dni=dni_clean,
            whatsapp_number=whatsapp_number if whatsapp_number else None,
            call_number=call_number if call_number else None,
            phone_number=whatsapp_number or call_number,  # Legacy field compatibility
            location=request.form['location'],
            address=request.form.get('address', ''),
            seller_keyword=seller_keyword if seller_keyword else None,
            title=request.form['title'],
            description=request.form['description'],
            price=price_value,
            currency=request.form['currency'],
            publication_type=request.form.get('publication_type', 'plus'),
            year=int(request.form['year']) if request.form['year'] else None,
            brand=request.form['brand'],
            model=request.form['model'],
            kilometers=int(request.form['kilometers'].replace('.', '').replace(',', '').replace(' ', '')) if request.form['kilometers'] else None,
            fuel_type=request.form['fuel_type'],
            transmission=request.form['transmission'],
            color=request.form['color']
        )
        
        # Handle uploaded images
        image_urls = []
        main_image_index = 0  # Default to first image
        
        # Process base64 image data from JavaScript
        import base64
        import uuid
        
        # Look for vehicle_images_data_* fields
        image_index = 0
        while f'vehicle_images_data_{image_index}' in request.form:
            image_data = request.form[f'vehicle_images_data_{image_index}']
            if image_data and image_data.startswith('data:image/'):
                try:
                    # Extract base64 data
                    header, data = image_data.split(',', 1)
                    image_binary = base64.b64decode(data)
                    
                    # Determine file extension from header
                    if 'jpeg' in header or 'jpg' in header:
                        ext = 'jpg'
                    elif 'png' in header:
                        ext = 'png'
                    elif 'webp' in header:
                        ext = 'webp'
                    else:
                        ext = 'jpg'  # Default
                    
                    # Generate unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"client_{timestamp}_{unique_id}.{ext}"
                    
                    # Upload to Cloudinary
                    from io import BytesIO
                    file_obj = BytesIO(image_binary)
                    file_obj.name = filename
                    
                    upload_result = upload_to_cloudinary(file_obj, 'vehicle_images')
                    if upload_result['success']:
                        image_urls.append(upload_result['url'])
                    else:
                        print(f"Error uploading image {image_index}: {upload_result['error']}")
                    
                except Exception as e:
                    print(f"Error processing image {image_index}: {e}")
                    
            image_index += 1
        
        # Fallback: Handle traditional file uploads if no base64 data
        if not image_urls and 'vehicle_images' in request.files:
            files = request.files.getlist('vehicle_images')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    # Generate unique filename
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    filename = f"client_{timestamp}_{filename}"
                    
                    # Upload to Cloudinary
                    upload_result = upload_to_cloudinary(file, 'vehicle_images')
                    if upload_result['success']:
                        image_urls.append(upload_result['url'])
                    else:
                        print(f"Error uploading image: {upload_result['error']}")
        
        # Get main image index from form
        try:
            main_image_index = int(request.form.get('main_image_index', 0))
            # Ensure index is valid
            if main_image_index < 0 or main_image_index >= len(image_urls):
                main_image_index = 0
        except (ValueError, TypeError):
            main_image_index = 0
        
        client_request.images = json.dumps(image_urls)
        client_request.main_image_index = main_image_index
        
        db.session.add(client_request)
        db.session.commit()
        
        flash('Tu solicitud ha sido enviada exitosamente. La revisaremos y te contactaremos pronto.', 'success')
        return redirect(url_for('index'))
    
    return render_template('client_request.html')

@app.route('/admin/solicitudes-pendientes')
def admin_pending_requests():
    if not session.get('admin_logged_in'):
        return redirect(url_for('panel_login'))
    
    pending_requests = ClientRequest.query.filter_by(status='pending').order_by(ClientRequest.created_at.desc()).all()
    
    return render_template('admin_pending_requests.html', requests=pending_requests)


@app.route('/admin/procesar-solicitud/<int:request_id>/<action>')
def process_client_request(request_id, action):
    if not session.get('admin_logged_in'):
        return redirect(url_for('panel_login'))
    
    from datetime import datetime, timedelta
    from models import Admin
    
    # Validar que el admin_id de la sesión realmente existe
    admin_id = session.get('admin_id')
    if admin_id:
        admin_exists = Admin.query.get(admin_id)
        if not admin_exists:
            # Si el admin no existe, limpiar sesión y forzar nuevo login
            session.clear()
            flash('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'warning')
            return redirect(url_for('panel_login'))
    else:
        # Si no hay admin_id en sesión, forzar login
        return redirect(url_for('panel_login'))
    
    client_request = ClientRequest.query.get_or_404(request_id)
    
    if action == 'approve':
        try:
            # Get premium duration from query parameter
            duration_months = int(request.args.get('duration', 1))
            print(f"Processing approval for request {request_id} with duration {duration_months} months")
            
            # Get main image index from client request
            main_image_index = 0
            try:
                if hasattr(client_request, 'main_image_index'):
                    main_image_index = client_request.main_image_index or 0
            except:
                main_image_index = 0
            
            # Create vehicle from client request
            vehicle = Vehicle(
                title=client_request.title,
                description=client_request.description,
                price=client_request.price,
                currency=client_request.currency,
                year=client_request.year,
                brand=client_request.brand,
                model=client_request.model,
                kilometers=client_request.kilometers,
                fuel_type=client_request.fuel_type,
                transmission=client_request.transmission,
                color=client_request.color,
                images=client_request.images,
                main_image_index=client_request.main_image_index,
                whatsapp_number=client_request.whatsapp_number,
                call_number=client_request.call_number,
                is_plus=(client_request.publication_type == 'plus'),
                seller_keyword=client_request.seller_keyword,
                client_request_id=client_request.id,
                premium_duration_months=duration_months
            )
            
            # Set premium expiration date
            vehicle.premium_expires_at = datetime.utcnow() + timedelta(days=duration_months * 30)
            
            db.session.add(vehicle)
            client_request.status = 'approved'
            client_request.processed_at = datetime.utcnow()
            client_request.processed_by_admin_id = admin_id
            
            db.session.commit()
            print(f"Successfully approved request {request_id}")
            flash(f'Solicitud aprobada y vehículo publicado: {vehicle.title} (Premium por {duration_months} meses)', 'success')
            
        except Exception as e:
            db.session.rollback()
            print(f"Error approving request {request_id}: {str(e)}")
            flash(f'Error al aprobar la solicitud: {str(e)}', 'error')
    
    elif action == 'reject':
        client_request.status = 'rejected'
        client_request.processed_at = datetime.utcnow()
        client_request.processed_by_admin_id = admin_id
        
        flash(f'Solicitud rechazada: {client_request.title}', 'warning')
    
    db.session.commit()
    return redirect(url_for('admin_pending_requests'))

@app.route('/admin/editar-solicitud/<int:request_id>', methods=['GET', 'POST'])
def edit_client_request(request_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('panel_login'))
    
    client_request = ClientRequest.query.get_or_404(request_id)
    
    if request.method == 'POST':
        # Update client request data
        price_str = request.form['price'].replace('.', '').replace(',', '').replace(' ', '')
        
        client_request.full_name = request.form['full_name']
        client_request.dni = request.form['dni']
        new_seller_keyword = request.form.get('seller_keyword', '').strip() or None
        
        # Check if this DNI already has a different seller_keyword in other requests
        if new_seller_keyword and new_seller_keyword != client_request.seller_keyword:
            existing_requests = ClientRequest.query.filter_by(dni=client_request.dni).all()
            for existing_req in existing_requests:
                if existing_req.seller_keyword != new_seller_keyword:
                    existing_req.seller_keyword = new_seller_keyword
                    
                    # Also update any vehicles associated with those requests
                    vehicles_to_update = Vehicle.query.filter_by(client_request_id=existing_req.id).all()
                    for vehicle in vehicles_to_update:
                        vehicle.seller_keyword = new_seller_keyword
        
        client_request.seller_keyword = new_seller_keyword
        client_request.email = request.form.get('email', '')
        client_request.phone_number = request.form.get('phone_number', '')
        client_request.location = request.form.get('location', '')
        client_request.address = request.form.get('address', '')
        client_request.title = request.form['title']
        client_request.description = request.form['description']
        client_request.price = int(price_str)
        client_request.currency = request.form['currency']
        client_request.year = int(request.form['year']) if request.form.get('year') else None
        client_request.brand = request.form.get('brand', '')
        client_request.model = request.form.get('model', '')
        client_request.kilometers = int(request.form.get('kilometers', '0').replace('.', '').replace(',', '').replace(' ', '')) if request.form.get('kilometers') else None
        client_request.fuel_type = request.form.get('fuel_type', '')
        client_request.transmission = request.form.get('transmission', '')
        client_request.color = request.form.get('color', '')
        client_request.admin_notes = request.form.get('admin_notes', '')
        
        # Handle new uploaded images
        new_image_urls = []
        if 'vehicle_images' in request.files:
            files = request.files.getlist('vehicle_images')
            if any(file.filename for file in files):  # If new images are uploaded
                for file in files:
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                        filename = f"client_{timestamp}_{filename}"
                        
                        # Upload to Cloudinary
                        upload_result = upload_to_cloudinary(file, 'vehicle_images')
                        if upload_result['success']:
                            new_image_urls.append(upload_result['url'])
                        else:
                            flash(f'Error uploading image: {upload_result["error"]}', 'error')
                
                if new_image_urls:  # Replace images only if new ones were uploaded
                    client_request.images = json.dumps(new_image_urls)
        
        # Also update the associated vehicle if it exists
        vehicle = Vehicle.query.filter_by(client_request_id=request_id).first()
        if vehicle:
            print(f"DEBUG: Updating vehicle ID {vehicle.id} for client_request_id {request_id}")
            vehicle.title = client_request.title
            vehicle.description = client_request.description
            vehicle.price = client_request.price
            vehicle.currency = client_request.currency
            vehicle.year = client_request.year
            vehicle.brand = client_request.brand
            vehicle.model = client_request.model
            vehicle.kilometers = client_request.kilometers
            vehicle.fuel_type = client_request.fuel_type
            vehicle.transmission = client_request.transmission
            vehicle.color = client_request.color
            vehicle.full_name = client_request.full_name
            vehicle.dni = client_request.dni
            vehicle.seller_keyword = client_request.seller_keyword
            vehicle.email = client_request.email
            vehicle.phone_number = client_request.phone_number
            vehicle.whatsapp_number = client_request.phone_number  # Use phone as WhatsApp
            vehicle.call_number = client_request.phone_number
            vehicle.location = client_request.location
            vehicle.address = client_request.address
            
            # Update images if new ones were uploaded
            if new_image_urls:
                vehicle.images = json.dumps(new_image_urls)
            print(f"DEBUG: Vehicle updated - Title: {vehicle.title}, Price: {vehicle.price}")
        else:
            print(f"DEBUG: No vehicle found for client_request_id {request_id}")
        
        db.session.commit()
        flash('Solicitud y vehículo actualizados exitosamente', 'success')
        return redirect(url_for('admin_pending_requests'))
    
    return render_template('edit_client_request.html', client_request=client_request)

@app.route('/admin/usuarios-vehiculos')
def admin_users_vehicles():
    if not session.get('admin_logged_in'):
        return redirect(url_for('panel_login'))
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 10 registros por página
    
    # Get all vehicles grouped by owner (from client request)
    from sqlalchemy import distinct
    
    # Get vehicles with their original client request data
    vehicles_with_owners = db.session.query(
        Vehicle, ClientRequest
    ).join(
        ClientRequest, Vehicle.client_request_id == ClientRequest.id
    ).order_by(ClientRequest.full_name, Vehicle.created_at.desc()).all()
    
    # Group vehicles by owner using DNI as primary key
    owners = {}
    for vehicle, client_request in vehicles_with_owners:
        # Use DNI as the primary grouping key, fallback to name if DNI is empty
        owner_key = client_request.dni if client_request.dni else f"SIN_DNI_{client_request.full_name}"
        
        if owner_key not in owners:
            owners[owner_key] = {
                'client_data': client_request,
                'vehicles': []
            }
        else:
            # If we already have this DNI, update client_data with the most recent info
            # (in case there are slight variations in name/contact info)
            existing_client = owners[owner_key]['client_data']
            current_client = client_request
            
            # Keep the most complete/recent client data
            if (current_client.whatsapp_number and not existing_client.whatsapp_number) or \
               (current_client.call_number and not existing_client.call_number) or \
               (current_client.address and not existing_client.address) or \
               (len(current_client.full_name) > len(existing_client.full_name)):
                owners[owner_key]['client_data'] = current_client
        
        owners[owner_key]['vehicles'].append(vehicle)
    
    # Get all client requests for complete client history (including deleted vehicles)
    all_client_requests = ClientRequest.query.order_by(ClientRequest.created_at.desc()).all()
    
    # Group client requests by DNI for complete client history
    client_history = {}
    for client_request in all_client_requests:
        # Use DNI as the primary grouping key, fallback to name if DNI is empty
        client_key = client_request.dni if client_request.dni else f"SIN_DNI_{client_request.full_name}"
        
        if client_key not in client_history:
            client_history[client_key] = {
                'client_data': client_request,
                'all_requests': []
            }
        else:
            # Keep the most recent/complete client data
            existing_client = client_history[client_key]['client_data']
            current_client = client_request
            
            if (current_client.whatsapp_number and not existing_client.whatsapp_number) or \
               (current_client.call_number and not existing_client.call_number) or \
               (current_client.address and not existing_client.address) or \
               (current_client.created_at > existing_client.created_at):
                client_history[client_key]['client_data'] = current_client
        
        client_history[client_key]['all_requests'].append(client_request)
    
    # Implementar paginación para client_history
    client_history_list = list(client_history.items())
    total_clients = len(client_history_list)
    
    # Calcular paginación
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_client_history = dict(client_history_list[start_index:end_index])
    
    # Calcular información de paginación
    total_pages = (total_clients + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None
    
    # Generar lista de páginas para mostrar
    page_numbers = []
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)
    
    for p in range(start_page, end_page + 1):
        page_numbers.append(p)
    
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': total_clients,
        'pages': total_pages,
        'has_prev': has_prev,
        'prev_num': prev_num,
        'has_next': has_next,
        'next_num': next_num,
        'page_numbers': page_numbers
    }
    
    from datetime import datetime
    now = datetime.utcnow()
    return render_template('admin_users_vehicles.html', 
                         owners=owners, 
                         client_history=paginated_client_history, 
                         pagination=pagination_info,
                         now=now)

@app.route('/admin/update-premium-duration/<int:vehicle_id>/<int:months>', methods=['POST'])
def update_premium_duration(vehicle_id, months):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    if months < 1 or months > 12:
        return jsonify({'success': False, 'error': 'Duración inválida'})
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Update premium duration
    vehicle.premium_duration_months = months
    
    # Calculate new expiration date
    from datetime import datetime, timedelta
    if vehicle.premium_expires_at and vehicle.premium_expires_at > datetime.utcnow():
        # Extend from current expiration date
        vehicle.premium_expires_at = vehicle.premium_expires_at + timedelta(days=months * 30)
    else:
        # Set new expiration date from now
        vehicle.premium_expires_at = datetime.utcnow() + timedelta(days=months * 30)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Duración premium actualizada a {months} meses'})

@app.route('/admin/toggle-vehicle/<int:vehicle_id>', methods=['POST'])
def toggle_vehicle_status(vehicle_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        vehicle.is_active = not vehicle.is_active
        db.session.commit()
        
        status_text = "activado" if vehicle.is_active else "pausado"
        return jsonify({
            'success': True, 
            'message': f'Vehículo "{vehicle.title}" ha sido {status_text}',
            'new_status': vehicle.is_active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/delete-vehicle/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle_ajax(vehicle_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        # Delete associated images from Cloudinary and filesystem
        import os
        upload_folder = app.config['UPLOAD_FOLDER']
        
        print(f"🔍 DEBUG: Vehicle images field: {vehicle.images}")
        print(f"🔍 DEBUG: Vehicle images type: {type(vehicle.images)}")
        
        if vehicle.images:
            # Handle both JSON string and list formats
            if isinstance(vehicle.images, str):
                try:
                    image_urls = json.loads(vehicle.images)
                    print(f"🔍 DEBUG: Parsed JSON images: {image_urls}")
                except Exception as e:
                    print(f"🔍 DEBUG: JSON parse failed: {e}, treating as single string")
                    image_urls = [vehicle.images]  # Single image as string
            else:
                image_urls = vehicle.images if isinstance(vehicle.images, list) else []
                print(f"🔍 DEBUG: Using images as list: {image_urls}")
            
            print(f"🔍 DEBUG: Processing {len(image_urls)} images")
            
            for i, image_url in enumerate(image_urls):
                print(f"🔍 DEBUG: Processing image {i+1}: {image_url}")
                
                # Skip invalid or empty image URLs
                if not isinstance(image_url, str) or not image_url.strip():
                    print(f"🔍 DEBUG: Skipping invalid/empty image URL: {image_url}")
                    continue
                
                # Skip directory paths and invalid paths
                if image_url in ['/', '.', '..'] or image_url.endswith('/.') or image_url.endswith('/..'):
                    print(f"🔍 DEBUG: Skipping directory path: {image_url}")
                    continue
                
                # Skip paths that look like directories (no file extension and end with /)
                if image_url.endswith('/') and '.' not in os.path.basename(image_url):
                    print(f"🔍 DEBUG: Skipping directory-like path: {image_url}")
                    continue
                
                # Delete from Cloudinary if it's a Cloudinary URL
                if 'cloudinary.com' in image_url or 'res.cloudinary.com' in image_url:
                    print(f"🔍 DEBUG: Detected Cloudinary URL: {image_url}")
                    try:
                        # Extract public_id from Cloudinary URL
                        url_parts = image_url.split('/')
                        print(f"🔍 DEBUG: URL parts: {url_parts}")
                        
                        if len(url_parts) >= 2:
                            # Find the part after 'upload'
                            upload_index = -1
                            for j, part in enumerate(url_parts):
                                if part == 'upload':
                                    upload_index = j
                                    break
                            
                            print(f"🔍 DEBUG: Upload index found at: {upload_index}")
                            
                            if upload_index != -1:
                                # Get everything after upload (skip version if present)
                                remaining_parts = url_parts[upload_index + 1:]
                                print(f"🔍 DEBUG: Remaining parts after upload: {remaining_parts}")
                                
                                if remaining_parts and remaining_parts[0].startswith('v'):
                                    # Skip version number
                                    remaining_parts = remaining_parts[1:]
                                    print(f"🔍 DEBUG: After skipping version: {remaining_parts}")
                                
                                if remaining_parts:
                                    # Join the remaining parts and remove file extension
                                    public_id = '/'.join(remaining_parts)
                                    public_id = os.path.splitext(public_id)[0]  # Remove extension
                                    
                                    print(f"🗑️ Attempting to delete Cloudinary image with public_id: {public_id}")
                                    success = delete_from_cloudinary(public_id)
                                    if success:
                                        print(f"✅ Successfully deleted from Cloudinary: {public_id}")
                                    else:
                                        print(f"❌ Failed to delete from Cloudinary: {public_id}")
                                else:
                                    print(f"❌ No remaining parts to form public_id")
                            else:
                                print(f"❌ 'upload' not found in URL parts")
                        else:
                            print(f"❌ URL has insufficient parts: {len(url_parts)}")
                    except Exception as e:
                        print(f"❌ Error deleting Cloudinary image {image_url}: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Also try to delete from local filesystem (legacy support)
                elif not image_url.startswith('http'):
                    print(f"🔍 DEBUG: Processing local image: {image_url}")
                    
                    # Additional validation for local paths
                    if not image_url or image_url.startswith('/') or '..' in image_url:
                        print(f"🔍 DEBUG: Skipping potentially dangerous local path: {image_url}")
                        continue
                    
                    upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
                    full_path = os.path.join(upload_folder, image_url)
                    
                    # Ensure the path is within the upload folder (security check)
                    try:
                        real_upload_folder = os.path.realpath(upload_folder)
                        real_full_path = os.path.realpath(full_path)
                        if not real_full_path.startswith(real_upload_folder):
                            print(f"🔍 DEBUG: Skipping path outside upload folder: {image_url}")
                            continue
                    except Exception as e:
                        print(f"🔍 DEBUG: Error validating path {image_url}: {e}")
                        continue
                    
                    if os.path.exists(full_path) and os.path.isfile(full_path):
                        try:
                            os.remove(full_path)
                            print(f"🗑️ Deleted local image: {full_path}")
                        except OSError as e:
                            print(f"❌ Error deleting local image {full_path}: {e}")
                    else:
                        print(f"🔍 DEBUG: Local file not found or is not a file: {full_path}")
                else:
                    print(f"🔍 DEBUG: Skipping image (not Cloudinary or local): {image_url}")
        else:
            print("🔍 DEBUG: No images found in vehicle.images")
        
        # Delete related VehicleView records first
        VehicleView.query.filter_by(vehicle_id=vehicle_id).delete()
        
        # Delete related Click records
        Click.query.filter_by(vehicle_id=vehicle_id).delete()
        
        # Delete vehicle from database
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Vehículo "{vehicle.brand} {vehicle.model}" eliminado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False, 
            'error': f'Error al eliminar el vehículo: {str(e)}'
        })


# Gestores Routes
@app.route('/gestores')
def gestores():
    """Display list of active automotive managers/brokers"""
    featured_gestores = Gestor.query.filter_by(is_active=True, is_featured=True).all()
    regular_gestores = Gestor.query.filter_by(is_active=True, is_featured=False).all()
    
    # Track page visit
    try:
        page_visit = PageVisit(page='gestores')
        db.session.add(page_visit)
        db.session.commit()
    except:
        pass  # Don't fail if tracking fails
    
    return render_template('gestores.html', 
                         featured_gestores=featured_gestores,
                         regular_gestores=regular_gestores)

# Admin Gestores Routes
@app.route('/admin/gestores')
@admin_required
def admin_gestores():
    """Admin page to manage gestores"""
    gestores = Gestor.query.order_by(Gestor.is_featured.desc(), Gestor.name.asc()).all()
    return render_template('admin_gestores.html', gestores=gestores)

@app.route('/admin/gestores/add', methods=['GET', 'POST'])
@admin_required
def admin_add_gestor():
    """Add new gestor"""
    if request.method == 'POST':
        try:
            # Handle image upload
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    # Generate unique filename
                    import uuid
                    from werkzeug.utils import secure_filename
                    import os
                    
                    filename = secure_filename(file.filename)
                    name, ext = os.path.splitext(filename)
                    unique_filename = f"{uuid.uuid4().hex[:8]}_{name}{ext}"
                    
                    # Upload to Cloudinary
                    upload_result = upload_to_cloudinary(file, 'gestores')
                    if upload_result['success']:
                        image_filename = upload_result['url']
                    else:
                        flash(f'Error uploading gestor image: {upload_result["error"]}', 'error')
                        image_filename = None
            
            gestor = Gestor(
                name=request.form.get('name'),
                business_name=request.form.get('business_name'),
                phone_number=request.form.get('phone_number'),
                whatsapp_number=request.form.get('whatsapp_number'),
                email=request.form.get('email'),
                location=request.form.get('location'),
                specializations=request.form.get('specializations'),
                years_experience=int(request.form.get('years_experience', 0)) if request.form.get('years_experience') else None,
                description=request.form.get('description'),
                image_filename=image_filename,
                is_featured=bool(request.form.get('is_featured')),
                is_active=True
            )
            
            db.session.add(gestor)
            db.session.commit()
            
            flash('Gestor agregado exitosamente', 'success')
            return redirect(url_for('admin_gestores'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar gestor: {str(e)}', 'error')
    
    return render_template('admin_add_gestor.html')

@app.route('/admin/gestores/edit/<int:gestor_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_gestor(gestor_id):
    """Edit existing gestor"""
    gestor = Gestor.query.get_or_404(gestor_id)
    
    if request.method == 'POST':
        try:
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    # Delete old image if exists
                    if gestor.image_filename:
                        import os
                        old_image_path = os.path.join(app.root_path, 'static', 'uploads', 'gestores', gestor.image_filename)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    
                    # Save new image
                    import uuid
                    from werkzeug.utils import secure_filename
                    import os
                    
                    filename = secure_filename(file.filename)
                    name, ext = os.path.splitext(filename)
                    unique_filename = f"{uuid.uuid4().hex[:8]}_{name}{ext}"
                    
                    # Upload to Cloudinary
                    upload_result = upload_to_cloudinary(file, 'gestores')
                    if upload_result['success']:
                        gestor.image_filename = upload_result['url']
                    else:
                        flash(f'Error uploading gestor image: {upload_result["error"]}', 'error')
            
            gestor.name = request.form.get('name')
            gestor.business_name = request.form.get('business_name')
            gestor.phone_number = request.form.get('phone_number')
            gestor.whatsapp_number = request.form.get('whatsapp_number')
            gestor.email = request.form.get('email')
            gestor.location = request.form.get('location')
            gestor.specializations = request.form.get('specializations')
            gestor.years_experience = int(request.form.get('years_experience', 0)) if request.form.get('years_experience') else None
            gestor.description = request.form.get('description')
            gestor.is_featured = bool(request.form.get('is_featured'))
            gestor.is_active = bool(request.form.get('is_active'))
            
            db.session.commit()
            
            flash('Gestor actualizado exitosamente', 'success')
            return redirect(url_for('admin_gestores'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar gestor: {str(e)}', 'error')
    
    return render_template('admin_edit_gestor.html', gestor=gestor)

@app.route('/admin/gestores/delete/<int:gestor_id>', methods=['POST'])
@admin_required
def admin_delete_gestor(gestor_id):
    """Delete gestor"""
    try:
        gestor = Gestor.query.get_or_404(gestor_id)
        name = gestor.name
        
        db.session.delete(gestor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Gestor "{name}" eliminado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al eliminar gestor: {str(e)}'
        })

@app.route('/admin/gestores/toggle-featured/<int:gestor_id>', methods=['POST'])
@admin_required
def admin_toggle_gestor_featured(gestor_id):
    """Toggle gestor featured status"""
    try:
        gestor = Gestor.query.get_or_404(gestor_id)
        gestor.is_featured = not gestor.is_featured
        
        db.session.commit()
        
        status = "destacado" if gestor.is_featured else "regular"
        return jsonify({
            'success': True,
            'message': f'Gestor "{gestor.name}" marcado como {status}',
            'is_featured': gestor.is_featured
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al cambiar estado: {str(e)}'
        })

def admin_new_gestor():
    """Create new gestor"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        try:
            # Handle image upload
            image_url = None
            if 'gestor_image' in request.files:
                file = request.files['gestor_image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    filename = f"gestor_{timestamp}_{filename}"
                    
                    # Upload to Cloudinary
                    upload_result = upload_to_cloudinary(file, 'gestores')
                    if upload_result['success']:
                        image_url = upload_result['url']
                    else:
                        flash(f'Error uploading gestor image: {upload_result["error"]}', 'error')
                        image_url = None
            
            gestor = Gestor(
                name=request.form['name'],
                business_name=request.form.get('business_name', ''),
                phone_number=request.form.get('phone_number', ''),
                whatsapp_number=request.form.get('whatsapp_number', ''),
                email=request.form.get('email', ''),
                address=request.form.get('address', ''),
                location=request.form.get('location', ''),
                specializations=request.form.get('specializations', ''),
                years_experience=int(request.form.get('years_experience', 0)) if request.form.get('years_experience') else None,
                description=request.form.get('description', ''),
                image_url=image_url,
                is_active=request.form.get('is_active') == 'on',
                is_featured=request.form.get('is_featured') == 'on'
            )
            
            db.session.add(gestor)
            db.session.commit()
            
            flash('Gestor creado exitosamente', 'success')
            return redirect(url_for('admin_gestores'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear gestor: {str(e)}', 'danger')
    
    return render_template('admin_gestor_form.html')


@app.route('/admin/export_client_history_pdf', methods=['POST'])
@admin_required
def export_client_history_pdf():
    """Exportar historial completo de clientes a PDF"""
    try:
        # Obtener todos los clientes con sus solicitudes
        client_requests = ClientRequest.query.order_by(ClientRequest.created_at.desc()).all()
        
        # Agrupar por cliente
        client_history = {}
        for request in client_requests:
            client_key = f"{request.full_name}_{request.whatsapp_number or request.call_number}"
            
            if client_key not in client_history:
                client_history[client_key] = {
                    'client_data': request,
                    'all_requests': []
                }
            
            client_history[client_key]['all_requests'].append(request)
        
        # Crear PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=30)
        
        # Contenido del PDF
        story = []
        
        # Título
        title = Paragraph("Historial Completo de Clientes", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Fecha de generación
        fecha = Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
        story.append(fecha)
        story.append(Spacer(1, 20))
        
        # Datos de la tabla
        data = [['Cliente', 'DNI', 'Contacto', 'Ubicación', 'Vehículos', 'Primera Pub.']]
        
        for client_key, client_info in client_history.items():
            client_data = client_info['client_data']
            requests = client_info['all_requests']
            first_request = min(requests, key=lambda x: x.created_at)
            
            # Contacto
            contacto = []
            if client_data.whatsapp_number:
                contacto.append(f"W: {client_data.whatsapp_number}")
            if client_data.call_number:
                contacto.append(f"T: {client_data.call_number}")
            contacto_str = "\n".join(contacto)
            
            # Vehículos
            vehiculos_info = []
            for req in requests:
                status = "✓" if req.status == 'approved' else "✗" if req.status == 'rejected' else "?"
                tipo = "+" if req.publication_type == 'plus' else "G"
                vehiculos_info.append(f"{status}{tipo} {req.brand} {req.model}")
            vehiculos_str = "\n".join(vehiculos_info[:3])  # Máximo 3 para no saturar
            if len(vehiculos_info) > 3:
                vehiculos_str += f"\n... y {len(vehiculos_info)-3} más"
            
            row = [
                client_data.full_name,
                client_data.dni or "Sin DNI",
                contacto_str,
                client_data.location,
                vehiculos_str,
                first_request.created_at.strftime('%d/%m/%Y')
            ]
            data.append(row)
        
        # Crear tabla
        table = Table(data, colWidths=[2*inch, 1*inch, 1.5*inch, 1*inch, 2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
        
        # Resumen
        story.append(Spacer(1, 20))
        resumen = Paragraph(f"Total de clientes: {len(client_history)}", styles['Normal'])
        story.append(resumen)
        
        total_requests = sum(len(info['all_requests']) for info in client_history.values())
        total_requests_p = Paragraph(f"Total de solicitudes: {total_requests}", styles['Normal'])
        story.append(total_requests_p)
        
        # Construir PDF
        doc.build(story)
        
        # Preparar respuesta
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=historial_clientes_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
        
        buffer.close()
        return response
        
    except Exception as e:
        flash(f'Error al generar PDF: {str(e)}', 'danger')
        return redirect(url_for('admin_users_vehicles'))



# Seller Keywords Management Routes
@app.route('/admin/seller_keywords')
def admin_seller_keywords():
    if not session.get('admin_logged_in'):
        return redirect(url_for('panel_login'))
    
    try:
        # Get statistics - with error handling for missing column
        total_keywords = db.session.query(Vehicle.seller_keyword).filter(Vehicle.seller_keyword != '').filter(Vehicle.seller_keyword.isnot(None)).distinct().count()
        total_vehicles_with_keywords = Vehicle.query.filter(Vehicle.seller_keyword != '').filter(Vehicle.seller_keyword.isnot(None)).count()
        vehicles_without_keywords = Vehicle.query.filter(db.or_(Vehicle.seller_keyword == '', Vehicle.seller_keyword.is_(None))).count()
        
        avg_vehicles_per_keyword = 0
        if total_keywords > 0:
            avg_vehicles_per_keyword = round(total_vehicles_with_keywords / total_keywords, 1)
        
        stats = {
            'total_keywords': total_keywords,
            'total_vehicles_with_keywords': total_vehicles_with_keywords,
            'vehicles_without_keywords': vehicles_without_keywords,
            'avg_vehicles_per_keyword': avg_vehicles_per_keyword
        }
        
        # Get keyword statistics with DNI information
        keyword_stats = []
        keywords = db.session.query(Vehicle.seller_keyword).filter(Vehicle.seller_keyword != '').filter(Vehicle.seller_keyword.isnot(None)).distinct().all()
        
        for keyword_tuple in keywords:
            keyword = keyword_tuple[0]
            vehicles = Vehicle.query.filter_by(seller_keyword=keyword).all()
            
            # Get DNI from the first vehicle's client request
            dni = None
            seller_name = None
            for vehicle in vehicles:
                if vehicle.client_request_id:
                    client_request = ClientRequest.query.get(vehicle.client_request_id)
                    if client_request and client_request.dni:
                        dni = client_request.dni
                        seller_name = client_request.full_name
                        break
            
            # Calculate total views and clicks from related tables
            total_views = 0
            total_clicks = 0
            for vehicle in vehicles:
                vehicle_views = VehicleView.query.filter_by(vehicle_id=vehicle.id).count()
                vehicle_clicks = Click.query.filter_by(vehicle_id=vehicle.id).count()
                total_views += vehicle_views
                total_clicks += vehicle_clicks
            
            latest_vehicle_date = max((v.created_at for v in vehicles), default=None)
            
            keyword_stats.append({
                'keyword': keyword,
                'dni': dni,
                'seller_name': seller_name,
                'vehicle_count': len(vehicles),
                'total_views': total_views,
                'total_clicks': total_clicks,
                'latest_vehicle_date': latest_vehicle_date
            })
        
        # Sort by vehicle count descending
        keyword_stats.sort(key=lambda x: x['vehicle_count'], reverse=True)
        
    except Exception as e:
        # If seller_keyword column doesn't exist, show placeholder data
        stats = {
            'total_keywords': 0,
            'total_vehicles_with_keywords': 0,
            'vehicles_without_keywords': Vehicle.query.count(),
            'avg_vehicles_per_keyword': 0
        }
        keyword_stats = []
        flash('La funcionalidad de palabras clave está en proceso de configuración. La columna de base de datos será agregada pronto.', 'info')
    
    # Get pending requests count for sidebar
    pending_requests_count = ClientRequest.query.filter_by(status='pending').count()
    sidebar_stats = {'pending_requests_count': pending_requests_count}
    
    return render_template('admin_seller_keywords.html', stats=sidebar_stats, keyword_stats=keyword_stats, keyword_page_stats=stats)

@app.route('/vendedor/<keyword>')
def seller_profile(keyword):
    """Página de perfil del vendedor que muestra todos sus vehículos"""
    # Track page visit
    track_page_visit(f'seller_profile_{keyword}')
    
    # Get all vehicles for this seller keyword
    vehicles = Vehicle.query.filter_by(seller_keyword=keyword, is_active=True).order_by(
        Vehicle.is_plus.desc(),  # Plus vehicles first
        Vehicle.created_at.desc()  # Then by newest first
    ).all()
    
    if not vehicles:
        # If no vehicles found, redirect to main page with search
        return redirect(url_for('index', search=keyword))
    
    # Get seller information from the first vehicle
    seller_info = {
        'keyword': keyword,
        'name': vehicles[0].full_name if vehicles[0].full_name else 'Vendedor',
        'location': vehicles[0].location if vehicles[0].location else '',
        'whatsapp': vehicles[0].whatsapp_number if vehicles[0].whatsapp_number else '',
        'total_vehicles': len(vehicles)
    }
    
    # Calculate statistics
    total_views = 0
    total_clicks = 0
    for vehicle in vehicles:
        vehicle_views = VehicleView.query.filter_by(vehicle_id=vehicle.id).count()
        vehicle_clicks = Click.query.filter_by(vehicle_id=vehicle.id).count()
        total_views += vehicle_views
        total_clicks += vehicle_clicks
    
    seller_stats = {
        'total_views': total_views,
        'total_clicks': total_clicks,
        'avg_price': sum(v.price for v in vehicles) // len(vehicles) if vehicles else 0
    }
    
    return render_template('seller_profile.html', 
                         vehicles=vehicles, 
                         seller_info=seller_info,
                         seller_stats=seller_stats)

@app.route('/admin/api/keyword-vehicles/<keyword>')
def api_keyword_vehicles(keyword):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    
    try:
        vehicles = Vehicle.query.filter_by(seller_keyword=keyword).all()
        
        vehicles_data = []
        for vehicle in vehicles:
            vehicles_data.append({
                'id': vehicle.id,
                'title': vehicle.title,
                'price_formatted': f"${vehicle.price:,}".replace(',', '.') if vehicle.price else 'Consultar',
                'brand': vehicle.brand or '',
                'model': vehicle.model or '',
                'year': vehicle.year
            })
        
        return jsonify({'success': True, 'vehicles': vehicles_data})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Funcionalidad no disponible temporalmente'})

@app.route('/admin/api/update-keyword', methods=['POST'])
def api_update_keyword():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        old_keyword = data.get('old_keyword')
        new_keyword = data.get('new_keyword')
        
        if not old_keyword or not new_keyword:
            return jsonify({'success': False, 'error': 'Faltan parámetros'})
        
        # Check if new keyword already exists
        existing = Vehicle.query.filter_by(seller_keyword=new_keyword).first()
        if existing and new_keyword != old_keyword:
            return jsonify({'success': False, 'error': 'La nueva palabra clave ya está en uso'})
        
        # Update all vehicles with the old keyword
        vehicles = Vehicle.query.filter_by(seller_keyword=old_keyword).all()
        for vehicle in vehicles:
            vehicle.seller_keyword = new_keyword
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Palabra clave actualizada. {len(vehicles)} vehículos afectados.'})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Funcionalidad no disponible temporalmente'})

@app.route('/admin/api/delete-keyword', methods=['POST'])
def admin_delete_keyword():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        keyword = data.get('keyword')
        
        if not keyword:
            return jsonify({'success': False, 'error': 'Falta el parámetro keyword'})
        
        # Update all vehicles with this keyword to remove it
        vehicles = Vehicle.query.filter_by(seller_keyword=keyword).all()
        for vehicle in vehicles:
            vehicle.seller_keyword = None
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Palabra clave eliminada. {len(vehicles)} vehículos afectados.'})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Error al eliminar la palabra clave'})

@app.route('/admin/restore_backup', methods=['POST'])
def admin_restore_backup():
    if not session.get('admin_logged_in'):
        return redirect(url_for('panel_login'))
    
    try:
        backup_file = request.form.get('backup_file')
        uploaded_file = request.files.get('backup_zip_file')
        
        # Check if we have either a selected backup or an uploaded file
        if not backup_file and not uploaded_file:
            flash('Debe seleccionar un archivo de backup o subir un archivo ZIP', 'error')
            return redirect(url_for('admin_backup_dashboard'))
        
        # Create a backup before restoring
        from backup_system.backup_system import BackupManager
        import os
        import tempfile
        backup_manager = BackupManager()
        
        # Create pre-restore backup
        pre_restore_backup = backup_manager.create_backup(backup_type='pre_restore')
        
        if pre_restore_backup['success']:
            flash(f'Backup de seguridad creado: {pre_restore_backup["filename"]}', 'info')
        
        # Handle uploaded ZIP file
        if uploaded_file and uploaded_file.filename:
            if not uploaded_file.filename.endswith('.zip'):
                flash('El archivo debe ser un ZIP válido', 'error')
                return redirect(url_for('admin_backup_dashboard'))
            
            # Save uploaded file temporarily
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, uploaded_file.filename)
            uploaded_file.save(temp_file_path)
            
            # Use the uploaded file for restoration
            restore_result = backup_manager.restore_backup(temp_file_path)
            
            # Clean up temporary file
            try:
                os.remove(temp_file_path)
                os.rmdir(temp_dir)
            except:
                pass
        else:
            # Use existing backup file
            restore_result = backup_manager.restore_backup(backup_file)
        
        if restore_result['success']:
            flash('Backup restaurado exitosamente', 'success')
        else:
            flash(f'Error al restaurar backup: {restore_result["error"]}', 'error')
            
    except Exception as e:
        flash(f'Error durante la restauración: {str(e)}', 'error')
    
    return redirect(url_for('admin_backup_dashboard'))

@app.route('/admin/delete_backup', methods=['POST'])
def admin_delete_backup():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        data = request.get_json()
        backup_path = data.get('backup_path')
        
        if not backup_path or '..' in backup_path:
            return jsonify({'success': False, 'error': 'Ruta de backup inválida'})
        
        # Check if file exists
        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'error': 'Archivo de backup no encontrado'})
        
        # Delete the backup file
        os.remove(backup_path)
        
        # Also delete manifest file if exists
        manifest_path = backup_path.replace('.zip', '_manifest.json')
        if os.path.exists(manifest_path):
            os.remove(manifest_path)
        
        return jsonify({'success': True, 'message': 'Backup eliminado exitosamente'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/download_backup/<path:backup_file>')
def admin_download_backup(backup_file):
    if not session.get('admin_logged_in'):
        return redirect(url_for('panel_login'))
    
    try:
        # Validate backup file path for security
        if not backup_file or '..' in backup_file:
            flash('Archivo de backup inválido', 'error')
            return redirect(url_for('admin_backup_dashboard'))
        
        # Check if file exists
        if not os.path.exists(backup_file):
            flash('Archivo de backup no encontrado', 'error')
            return redirect(url_for('admin_backup_dashboard'))
        
        # Get filename for download
        filename = os.path.basename(backup_file)
        
        # Send file
        return send_file(
            backup_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        flash(f'Error al descargar backup: {str(e)}', 'error')
        return redirect(url_for('admin_backup_dashboard'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html'), 500
