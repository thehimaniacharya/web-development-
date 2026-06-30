import os
from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash, jsonify
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import pooling
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
import threading
import time

app = Flask(__name__, template_folder='templates', static_folder='static')

BASE_URL = "https://24071099.tbcstudentserver.com"

# ------------------ SESSION CONFIG ------------------
app.config['SECRET_KEY'] = 'secret123'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ------------------ DATABASE CONNECTION POOL ------------------
dbconfig = {
    "host": "103.191.208.50",
    "user": "sacstrsx_24071099",
    "password": "aGqnl%t]^R.V,cVY",
    "database": "sacstrsx_24071099",
    "port": 3306,
    "pool_name": "hotel_pool",
    "pool_size": 10,
    "pool_reset_session": True,
    "autocommit": True,
    "buffered": True
}

try:
    connection_pool = pooling.MySQLConnectionPool(**dbconfig)
    print(" Database connection pool created successfully")
except mysql.connector.Error as err:
    print(f" Error creating connection pool: {err}")
    connection_pool = None

# Thread-local storage for database connections
thread_local = threading.local()

def get_db():
    """Get a database connection from the pool for current request"""
    try:
        # Get or create connection for this thread
        if not hasattr(thread_local, "connection"):
            if connection_pool:
                thread_local.connection = connection_pool.get_connection()
                print(f" New connection created for thread")
            else:
                # Fallback to direct connection if pool fails
                thread_local.connection = mysql.connector.connect(
                    host="103.191.208.50",
                    user="sacstrsx_24071099",
                    password="aGqnl%t]^R.V,cVY",
                    database="sacstrsx_24071099",
                    port=3306,
                    autocommit=True
                )
                print(" Using direct connection (pool not available)")
        else:
            # Check if connection is still alive
            try:
                thread_local.connection.ping(reconnect=True, attempts=1, delay=0)
            except:
                # Reconnect if ping fails
                if connection_pool:
                    thread_local.connection = connection_pool.get_connection()
                    print("♻️  Connection recreated (ping failed)")
        
        return thread_local.connection
    except mysql.connector.Error as err:
        print(f" Database connection error: {err}")
        # Try to create a direct connection as last resort
        try:
            thread_local.connection = mysql.connector.connect(
                host="103.191.208.50",
                user="sacstrsx_24071099",
                password="aGqnl%t]^R.V,cVY",
                database="sacstrsx_24071099",
                port=3306,
                autocommit=True
            )
            return thread_local.connection
        except Exception as e:
            print(f" Critical: Cannot connect to database: {e}")
            return None

@app.teardown_appcontext
def close_db_connection(exception=None):
    """Close database connection at end of request"""
    if hasattr(thread_local, "connection"):
        try:
            thread_local.connection.close()
            del thread_local.connection
        except:
            pass

# ------------------ UPLOAD CONFIG ------------------
UPLOAD_FOLDER = 'static/uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Hotel pagination config
INITIAL_HOTELS = 9
LOAD_MORE_HOTELS = 8

# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'thehimaniacharya@gmail.com'
app.config['MAIL_PASSWORD'] = 'pyme ozbg htgl dlwv'
app.config['MAIL_DEFAULT_SENDER'] = 'thehimaniacharya@gmail.com'

mail = Mail(app)

# Token generator
serializer = URLSafeTimedSerializer(app.secret_key)

# ==================== ADMIN DECORATOR ====================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session or session.get('role') != 'admin':
            flash('Access denied. Please login as admin.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== USER DECORATOR ====================
def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session or session.get('role') != 'user':
            flash('Please login as user to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROLE CHECKING MIDDLEWARE ====================
@app.before_request
def check_user_role():
    if request.endpoint in ['static', 'login', 'register', 'index', 'about', 
                           'contact', 'hotels', 'hotel_detail', 'rooms',
                           'booking', 'booking_hotel', 'booking_confirmation',
                           'create_booking', 'logout', 'activate', 'privacy',
                           'terms']:
        return
    
    # If user is logged in
    if 'loggedin' in session:
        role = session.get('role')
        
        # Admin trying to access user routes
        if role == 'admin' and request.endpoint in ['user_dashboard', 'user_profile', 
                                                    'edit_profile', 'my_bookings']:
            return redirect(url_for('admin_dashboard'))
        
        # User trying to access admin routes
        if role == 'user' and request.endpoint in ['admin_dashboard', 'manage_hotels',
                                                   'manage_rooms', 'manage_bookings',
                                                   'manage_users', 'admin_reports',
                                                   'add_hotel', 'edit_hotel', 'delete_hotel',
                                                   'add_room', 'mark_unavailable', 'mark_available',
                                                   'confirm_booking_admin', 'cancel_booking_admin',
                                                   'reset_user_password', 'make_admin', 'delete_user_admin',
                                                   'generate_report_pdf', 'manage_currencies',
                                                   'change_password']:
            flash('Admin access required.', 'error')
            return redirect(url_for('user_dashboard'))

# Prevent caching
@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ------------------ HOME / STATIC PAGES ------------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

# ------------------ CONTACT PAGE ------------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        
        ip_address = request.remote_addr
        
        try:
            db = get_db()
            if not db:
                flash('Database connection error. Please try again.', 'error')
                return redirect(url_for('contact'))
                
            cursor = db.cursor()
            insert_query = """
                INSERT INTO contact_messages 
                (name, email, subject, message, ip_address, status) 
                VALUES (%s, %s, %s, %s, %s, 'new')
            """
            cursor.execute(insert_query, (name, email, subject, message, ip_address))
            db.commit()
            cursor.close()
            
            flash('Thank you for contacting us! We will get back to you soon.', 'success')
            
        except Exception as e:
            print(f"Error: {e}")
            flash('Sorry, there was an error. Please try again.', 'error')
        
        return redirect(url_for('contact'))
    
    return render_template("contact.html")

# ------------------ HOTELS ------------------
@app.route("/hotels")
def hotels():
    offset = int(request.args.get('offset', 0))
    city = request.args.get('city', '')
    sort_by = request.args.get('sort', 'recommended')
    
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return render_template("hotels.html", hotels=[], more=False, total_hotels=0, cities=[])
    
    cursor = db.cursor(dictionary=True)
    limit = INITIAL_HOTELS if offset == 0 else LOAD_MORE_HOTELS

    query = "SELECT hotel_id, city, title, price, image, description FROM hotels"
    params = []
    if city:
        query += " WHERE city = %s"
        params.append(city)
    
    if sort_by == 'price-low':
        query += " ORDER BY price ASC"
    elif sort_by == 'price-high':
        query += " ORDER BY price DESC"
    elif sort_by == 'name':
        query += " ORDER BY title ASC"
    else:
        query += " ORDER BY hotel_id ASC"
    
    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, tuple(params))
    hotels = cursor.fetchall()

    count_query = "SELECT COUNT(*) as total FROM hotels"
    if city:
        count_query += " WHERE city = %s"
        cursor.execute(count_query, (city,))
    else:
        cursor.execute(count_query)
    
    total_hotels = cursor.fetchone()['total']
    more = total_hotels > offset + limit
    next_offset = offset + limit

    cursor.execute("SELECT DISTINCT city FROM hotels ORDER BY city")
    cities = [row['city'] for row in cursor.fetchall()]
    cursor.close()

    return render_template(
        "hotels.html", 
        hotels=hotels, 
        more=more, 
        next_offset=next_offset,
        total_hotels=total_hotels,
        cities=cities,
        selected_city=city,
        selected_sort=sort_by
    )

# ------------------ ROOMS PAGE ------------------
@app.route('/rooms/<int:hotel_id>')
def rooms(hotel_id):
    return redirect(url_for('hotel_detail', hotel_id=hotel_id))

# ------------------ HOTEL DETAILS ------------------
@app.route('/hotel/<int:hotel_id>')
def hotel_detail(hotel_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('hotels'))
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM hotels WHERE hotel_id=%s", (hotel_id,))
    hotel = cursor.fetchone()
    cursor.close()

    if not hotel:
        return "Hotel not found", 404

    if 'hero_image' not in hotel or not hotel['hero_image']:
        hotel['hero_image'] = url_for('static', filename='images/hotels/' + hotel.get('image', 'default.jpg'))

    return render_template("room.html", hotel=hotel)

# ------------------ BOOKING FLOW ------------------
@app.route('/booking')
def booking():
    flash('Please select a hotel to book', 'info')
    return redirect(url_for('hotels'))

@app.route('/booking/<int:hotel_id>')
def booking_hotel(hotel_id):
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    num_guests = request.args.get('num_guests', 2, type=int)
    room_type = request.args.get('room_type', 'all')
    
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('hotels'))
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM hotels WHERE hotel_id=%s", (hotel_id,))
    hotel = cursor.fetchone()
    
    if not hotel:
        cursor.close()
        flash('Hotel not found.', 'error')
        return redirect(url_for('hotels'))
    
    cursor.execute("""
        SELECT room_type, COUNT(*) as available_count 
        FROM rooms 
        WHERE hotel_id = %s AND status = 'available'
        GROUP BY room_type
    """, (hotel_id,))
    
    room_availability = {row['room_type']: row['available_count'] for row in cursor.fetchall()}
    cursor.close()
    
    nights = 0
    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
            nights = (check_out_date - check_in_date).days
        except:
            nights = 0
    
    if 'hero_image' not in hotel or not hotel['hero_image']:
        hotel['hero_image'] = url_for('static', filename='images/hotels/' + hotel.get('image', 'default.jpg'))
    
    return render_template('booking.html', 
                         hotel=hotel,
                         check_in=check_in,
                         check_out=check_out,
                         num_guests=num_guests,
                         selected_room_type=room_type,
                         nights=nights)

# ------------------ BOOKING CONFIRMATION ------------------
@app.route('/booking_confirmation/<int:hotel_id>')
def booking_confirmation(hotel_id):
    if 'loggedin' not in session:
        flash('Please login first to make a booking.', 'warning')
        session['redirect_after_login'] = request.url
        return redirect(url_for('login'))
    
    room_type = request.args.get('room_type')
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    num_guests = request.args.get('num_guests', 1, type=int)
    
    if not all([room_type, check_in, check_out]):
        flash('Missing booking information. Please select dates and room type.', 'error')
        return redirect(url_for('booking_hotel', hotel_id=hotel_id))
    
    valid_room_types = ['single', 'double', 'family']
    if room_type not in valid_room_types:
        flash('Invalid room type selected.', 'error')
        return redirect(url_for('booking_hotel', hotel_id=hotel_id))
    
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('booking_hotel', hotel_id=hotel_id))
    
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM hotels WHERE hotel_id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        
        if not hotel:
            flash('Hotel not found.', 'error')
            return redirect(url_for('hotels'))
        
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
        num_nights = (check_out_date - check_in_date).days
        
        if num_nights <= 0:
            flash('Check-out date must be after check-in date.', 'error')
            return redirect(url_for('booking_hotel', hotel_id=hotel_id))
        
        city_prices = {
            'Aberdeen': {'peak': 140, 'offpeak': 70},
            'Belfast': {'peak': 130, 'offpeak': 70},
            'Birmingham': {'peak': 150, 'offpeak': 75},
            'Bristol': {'peak': 140, 'offpeak': 70},
            'Cardiff': {'peak': 130, 'offpeak': 70},
            'Edinburgh': {'peak': 160, 'offpeak': 80},
            'Glasgow': {'peak': 150, 'offpeak': 75},
            'London': {'peak': 200, 'offpeak': 100},
            'Manchester': {'peak': 180, 'offpeak': 90},
            'Newcastle': {'peak': 120, 'offpeak': 70},
            'Oxford': {'peak': 180, 'offpeak': 90},
            'Kent': {'peak': 140, 'offpeak': 80}
        }
        
        month = check_in_date.month
        is_peak_season = (4 <= month <= 8) or (month == 11 or month == 12)
        season_name = "Peak Season" if is_peak_season else "Off-Peak Season"
        
        city = hotel['city']
        city_price = city_prices.get(city, city_prices['London'])
        standard_price = city_price['peak'] if is_peak_season else city_price['offpeak']
        
        peak_surcharge = standard_price * 0.30 if is_peak_season else 0
        base_price = standard_price
        
        room_type_surcharge = 0
        room_type_multiplier = 0
        
        if room_type == 'double':
            room_type_multiplier = 0.20
            room_type_surcharge = standard_price * room_type_multiplier
        elif room_type == 'family':
            room_type_multiplier = 0.50
            room_type_surcharge = standard_price * room_type_multiplier
        
        guest_surcharge = standard_price * 0.10 if (room_type == 'double' and num_guests >= 2) else 0
        
        price_per_night = base_price + peak_surcharge + room_type_surcharge + guest_surcharge
        subtotal = price_per_night * num_nights
        
        days_in_advance = max(0, (check_in_date - datetime.now()).days)
        discount_percent = 0
        discount_name = "No discount"
        
        if 80 <= days_in_advance <= 90:
            discount_percent = 30
            discount_name = "30% (80-90 days in advance)"
        elif 60 <= days_in_advance <= 79:
            discount_percent = 20
            discount_name = "20% (60-79 days in advance)"
        elif 45 <= days_in_advance <= 59:
            discount_percent = 10
            discount_name = "10% (45-59 days in advance)"
        
        advance_discount = subtotal * (discount_percent / 100)
        total_price = subtotal - advance_discount
        
        pricing = {
            'standard_price': standard_price,
            'peak_surcharge': peak_surcharge,
            'room_type_surcharge': room_type_surcharge,
            'guest_surcharge': guest_surcharge,
            'base_price': base_price,
            'price_per_night': price_per_night,
            'num_nights': num_nights,
            'subtotal': subtotal,
            'discount_percent': discount_percent,
            'discount_name': discount_name,
            'advance_discount': advance_discount,
            'total_price': total_price,
            'is_peak_season': is_peak_season,
            'season_name': season_name,
            'days_in_advance': days_in_advance,
            'room_type_multiplier': room_type_multiplier * 100,
            
            'standard_price_fmt': f"£{standard_price:.2f}",
            'peak_surcharge_fmt': f"£{peak_surcharge:.2f}",
            'room_type_surcharge_fmt': f"£{room_type_surcharge:.2f}",
            'guest_surcharge_fmt': f"£{guest_surcharge:.2f}",
            'base_price_fmt': f"£{base_price:.2f}",
            'price_per_night_fmt': f"£{price_per_night:.2f}",
            'subtotal_fmt': f"£{subtotal:.2f}",
            'advance_discount_fmt': f"£{advance_discount:.2f}",
            'total_price_fmt': f"£{total_price:.2f}"
        }
        
        user_info = {
            'email': session.get('email', ''),
            'username': session.get('username', ''),
            'id': session.get('id', '')
        }
        
        if 'hero_image' not in hotel or not hotel['hero_image']:
            hotel['hero_image'] = url_for('static', filename='images/hotels/' + hotel.get('image', 'default.jpg'))
        
    except Exception as e:
        print(f"Error in booking confirmation: {e}")
        flash('Error processing booking details. Please try again.', 'error')
        return redirect(url_for('booking_hotel', hotel_id=hotel_id))
    finally:
        cursor.close()
    
    current_time = datetime.now()
    
    return render_template('booking_confirmation.html',
                         hotel=hotel,
                         room_type=room_type,
                         check_in=check_in,
                         check_out=check_out,
                         num_guests=num_guests,
                         num_nights=num_nights,
                         pricing=pricing,
                         user_info=user_info,
                         now=current_time)

# ------------------ CREATE BOOKING (Final Confirmation) ------------------
@app.route('/create_booking')
def create_booking():
    print(f"DEBUG [create_booking]: Starting. User ID: {session.get('id')}, Username: {session.get('username')}")
    
    if 'loggedin' not in session:
        flash('Please login first to make a booking.', 'warning')
        return redirect(url_for('login'))
    
    hotel_id = request.args.get('hotel_id', type=int)
    room_type = request.args.get('room_type')
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    num_guests = request.args.get('num_guests', 1, type=int)
    
    print(f"DEBUG: Parameters received - hotel_id: {hotel_id}, room_type: {room_type}, check_in: {check_in}, check_out: {check_out}")
    
    if not all([hotel_id, room_type, check_in, check_out]):
        flash('Missing required booking information.', 'error')
        return redirect(url_for('hotels'))
    
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('booking_hotel', hotel_id=hotel_id))
    
    cursor = db.cursor(dictionary=True)
    
    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
        num_nights = (check_out_date - check_in_date).days
        
        if num_nights <= 0:
            flash('Check-out date must be after check-in date.', 'error')
            return redirect(url_for('booking_hotel', hotel_id=hotel_id))
        
        cursor.execute("SELECT * FROM hotels WHERE hotel_id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        
        if not hotel:
            flash('Hotel not found.', 'error')
            return redirect(url_for('hotels'))
        
        city_prices = {
            'Aberdeen': {'peak': 140, 'offpeak': 70},
            'Belfast': {'peak': 130, 'offpeak': 70},
            'Birmingham': {'peak': 150, 'offpeak': 75},
            'Bristol': {'peak': 140, 'offpeak': 70},
            'Cardiff': {'peak': 130, 'offpeak': 70},
            'Edinburgh': {'peak': 160, 'offpeak': 80},
            'Glasgow': {'peak': 150, 'offpeak': 75},
            'London': {'peak': 200, 'offpeak': 100},
            'Manchester': {'peak': 180, 'offpeak': 90},
            'Newcastle': {'peak': 120, 'offpeak': 70},
            'Oxford': {'peak': 180, 'offpeak': 90},
            'Kent': {'peak': 140, 'offpeak': 80}
        }
        
        month = check_in_date.month
        is_peak_season = (4 <= month <= 8) or (month == 11 or month == 12)
        
        city = hotel['city']
        city_price = city_prices.get(city, city_prices['London'])
        standard_price = city_price['peak'] if is_peak_season else city_price['offpeak']
        
        peak_surcharge = standard_price * 0.30 if is_peak_season else 0
        base_price = standard_price
        
        room_type_surcharge = 0
        if room_type == 'double':
            room_type_surcharge = standard_price * 0.20
        elif room_type == 'family':
            room_type_surcharge = standard_price * 0.50
        
        guest_surcharge = standard_price * 0.10 if (room_type == 'double' and num_guests >= 2) else 0
        
        price_per_night = base_price + peak_surcharge + room_type_surcharge + guest_surcharge
        subtotal = price_per_night * num_nights
        
        days_in_advance = max(0, (check_in_date - datetime.now()).days)
        discount_percent = 0
        if 80 <= days_in_advance <= 90:
            discount_percent = 30
        elif 60 <= days_in_advance <= 79:
            discount_percent = 20
        elif 45 <= days_in_advance <= 59:
            discount_percent = 10
        
        advance_discount = subtotal * (discount_percent / 100)
        total_price = subtotal - advance_discount
        
        username = session.get('username', 'Guest')
        user_email = session.get('email', '')
        
        if not user_email and username:
            user_email = f"{username}@example.com"
        
        print(f"DEBUG: User details - username: {username}, email: {user_email}, session id: {session['id']}")
        
        cursor.execute("""
            INSERT INTO bookings (
                user_id, hotel_id, room_type, 
                check_in, check_out, guests, num_nights,
                guest_name, guest_email,
                base_price, peak_surcharge, room_type_surcharge, guest_surcharge,
                subtotal, advance_discount_percent, advance_discount_amount, total_price,
                status, booking_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmed', NOW())
        """, (
            session['id'], hotel_id, room_type,
            check_in, check_out, num_guests, num_nights,
            username, user_email,
            standard_price, peak_surcharge, room_type_surcharge, guest_surcharge,
            subtotal, discount_percent, advance_discount, total_price
        ))
        
        booking_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM bookings WHERE booking_id = %s", (booking_id,))
        inserted_booking = cursor.fetchone()
        print(f"DEBUG: Inserted booking - ID: {booking_id}, User ID: {inserted_booking['user_id']}")
        
        db.commit()
        cursor.close()
        
        print(f"DEBUG: Booking created successfully! ID: {booking_id}, Redirecting to receipt...")
        
        try:
            msg = Message('Booking Confirmation #{}'.format(booking_id),
                         recipients=[user_email])
            msg.body = f"""
Dear {username},

Thank you for your booking with Hotel Booking System!

Booking Details:
----------------
Booking ID: #{booking_id}
Hotel: {hotel['title']}
Location: {hotel['city']}
Room Type: {room_type.title()}
Check-in: {check_in}
Check-out: {check_out}
Guests: {num_guests}
Total Amount: £{total_price:.2f}

Your booking has been confirmed.

You can view your booking details at: http://localhost:5002/receipt/{booking_id}

Thank you for choosing us!

Best regards,
Hotel Booking System Team
"""
            mail.send(msg)
            print(f"DEBUG: Confirmation email sent to {user_email}")
        except Exception as e:
            print(f"DEBUG: Email sending failed: {e}")
        
        receipt_url = url_for('receipt', booking_id=booking_id)
        print(f"DEBUG: Generated receipt URL: {receipt_url}")
        return redirect(receipt_url)
        
    except Exception as e:
        print(f"DEBUG: Booking error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        cursor.close()
        flash('An error occurred while processing your booking. Please try again.', 'error')
        return redirect(url_for('booking_hotel', hotel_id=hotel_id))
    

# ------------------ View Booking ------------------
@app.route('/api/booking/<int:booking_id>')
def get_booking_details(booking_id):
    if 'loggedin' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    db = get_db()
    if not db:
        return jsonify({'error': 'Database connection error'}), 500
    
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                b.booking_id,
                b.hotel_id,
                b.room_type,
                b.check_in,
                b.check_out,
                b.guests,
                b.num_nights,
                COALESCE(b.base_price, 0) as base_price,
                COALESCE(b.peak_surcharge, 0) as peak_surcharge,
                COALESCE(b.room_type_surcharge, 0) as room_type_surcharge,
                COALESCE(b.guest_surcharge, 0) as guest_surcharge,
                COALESCE(b.subtotal, 0) as subtotal,
                COALESCE(b.advance_discount_percent, 0) as advance_discount_percent,
                COALESCE(b.advance_discount_amount, 0) as advance_discount_amount,
                COALESCE(b.total_price, 0) as total_price,
                b.guest_name,
                b.guest_email,
                b.guest_phone,
                b.special_requests,
                b.status,
                b.booking_date,
                h.title as hotel_name, 
                h.city,
                DATE_FORMAT(b.check_in, '%d %b %Y') as check_in_formatted,
                DATE_FORMAT(b.check_out, '%d %b %Y') as check_out_formatted,
                DATE_FORMAT(b.booking_date, '%d %b %Y') as booking_date_formatted,
                u.username,
                u.email as user_email
            FROM bookings b
            LEFT JOIN hotels h ON b.hotel_id = h.hotel_id
            LEFT JOIN users u ON b.user_id = u.id
            WHERE b.booking_id = %s AND b.user_id = %s
        """, (booking_id, session['id']))
        
        booking = cursor.fetchone()
        cursor.close()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        return jsonify(booking)
        
    except Exception as e:
        print(f"Error fetching booking details: {e}")
        cursor.close()
        return jsonify({'error': 'Error loading booking details'}), 500
    

    # ==================== VIEW BOOKING DETAILS ====================
@app.route('/admin/booking/view/<int:booking_id>')
@admin_required
def view_booking_details(booking_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_bookings'))
    
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                b.*,
                u.username as customer_name,
                u.email as customer_email,
                h.title as hotel_name,
                h.city as hotel_city,
                h.address as hotel_address,
                DATE_FORMAT(b.check_in, '%d %b %Y') as check_in_formatted,
                DATE_FORMAT(b.check_out, '%d %b %Y') as check_out_formatted,
                DATE_FORMAT(b.booking_date, '%d %b %Y at %h:%i %p') as booking_date_formatted
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN hotels h ON b.hotel_id = h.hotel_id
            WHERE b.booking_id = %s
        """, (booking_id,))
        
        booking = cursor.fetchone()
        cursor.close()
        
        if not booking:
            flash('Booking not found!', 'error')
            return redirect(url_for('manage_bookings'))
        
        return render_template('admin/view_booking.html', booking=booking)
        
    except Exception as e:
        print(f"Error viewing booking: {e}")
        cursor.close()
        flash('Error loading booking details', 'error')
        return redirect(url_for('manage_bookings'))

# ------------------ CANCELLATION INFO API ------------------
@app.route('/api/booking/<int:booking_id>/cancel-info')
def get_cancellation_info(booking_id):
    if 'loggedin' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    db = get_db()
    if not db:
        return jsonify({'error': 'Database connection error'}), 500
    
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                b.booking_id,
                b.check_in,
                b.total_price,
                h.title as hotel_name
            FROM bookings b
            JOIN hotels h ON b.hotel_id = h.hotel_id
            WHERE b.booking_id = %s AND b.user_id = %s AND b.status = 'confirmed'
        """, (booking_id, session['id']))
        
        booking = cursor.fetchone()
        
        if not booking:
            return jsonify({'error': 'Booking not found or cannot be cancelled'}), 404
        
        check_in_date = booking['check_in']
        days_until_checkin = max(0, (check_in_date - datetime.now().date()).days)
        
        cancellation_policy = ""
        cancellation_charges = 0.0
        
        if days_until_checkin >= 30:
            cancellation_policy = "Full refund (cancellation 30+ days before check-in)"
            cancellation_charges = 0.0
        elif 15 <= days_until_checkin < 30:
            cancellation_policy = "75% refund (cancellation 15-29 days before check-in)"
            cancellation_charges = float(booking['total_price']) * 0.25
        elif 7 <= days_until_checkin < 15:
            cancellation_policy = "50% refund (cancellation 7-14 days before check-in)"
            cancellation_charges = float(booking['total_price']) * 0.50
        else:
            cancellation_policy = "No refund (cancellation less than 7 days before check-in)"
            cancellation_charges = float(booking['total_price'])
        
        refund_amount = float(booking['total_price']) - cancellation_charges
        
        cursor.close()
        
        return jsonify({
            'success': True,
            'booking_id': booking_id,
            'hotel_name': booking['hotel_name'],
            'total_price': float(booking['total_price']),
            'days_until_checkin': days_until_checkin,
            'cancellation_charges': round(cancellation_charges, 2),
            'refund_amount': round(refund_amount, 2),
            'policy_message': f"Cancellation charges apply based on how close to check-in you cancel. {cancellation_policy}",
            'full_refund': cancellation_charges == 0
        })
        
    except Exception as e:
        print(f"Error getting cancellation info: {e}")
        cursor.close()
        return jsonify({'error': 'Error loading cancellation information'}), 500

# ------------------ RECEIPT PAGE ------------------
@app.route('/receipt/<int:booking_id>')
def receipt(booking_id):
    print(f"RECEIPT DEBUG: Loading receipt for booking #{booking_id}")
    
    if 'loggedin' not in session:
        flash('Please login to view your booking.', 'error')
        return redirect(url_for('login'))
    
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return render_template('receipt.html', booking=None, error="Database connection error")
    
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT booking_id, user_id FROM bookings WHERE booking_id = %s", (booking_id,))
        booking_check = cursor.fetchone()
        
        if not booking_check:
            print(f"RECEIPT DEBUG: Booking #{booking_id} not found in database")
            cursor.close()
            flash('Booking not found.', 'error')
            return render_template('receipt.html', booking=None, error="Booking not found")
        
        if int(booking_check['user_id']) != int(session.get('id', 0)):
            print(f"RECEIPT DEBUG: User mismatch. Booking user: {booking_check['user_id']}, Session user: {session.get('id')}")
            cursor.close()
            flash('You do not have permission to view this booking.', 'error')
            return redirect(url_for('user_dashboard'))
        
        cursor.execute("""
            SELECT 
                b.booking_id,
                b.hotel_id,
                b.room_type,
                b.check_in,
                b.check_out,
                b.guests,
                b.num_nights,
                COALESCE(b.base_price, 0) as base_price,
                COALESCE(b.peak_surcharge, 0) as peak_surcharge,
                COALESCE(b.room_type_surcharge, 0) as room_type_surcharge,
                COALESCE(b.guest_surcharge, 0) as guest_surcharge,
                COALESCE(b.subtotal, 0) as subtotal,
                COALESCE(b.advance_discount_percent, 0) as advance_discount_percent,
                COALESCE(b.advance_discount_amount, 0) as advance_discount_amount,
                COALESCE(b.total_price, 0) as total_price,
                b.guest_name,
                b.guest_email,
                b.guest_phone,
                b.special_requests,
                b.status,
                b.booking_date,
                h.title as hotel_name, 
                h.city, 
                h.image as hotel_image,
                DATE_FORMAT(b.check_in, '%d %b %Y') as check_in_formatted,
                DATE_FORMAT(b.check_out, '%d %b %Y') as check_out_formatted,
                DATE_FORMAT(b.booking_date, '%d %b %Y at %h:%i %p') as booking_date_full,
                u.username,
                u.email as user_email,
                CASE 
                    WHEN b.advance_discount_percent > 0 THEN 'Yes'
                    ELSE 'No'
                END as has_discount
            FROM bookings b
            LEFT JOIN hotels h ON b.hotel_id = h.hotel_id
            LEFT JOIN users u ON b.user_id = u.id
            WHERE b.booking_id = %s
        """, (booking_id,))
        
        booking = cursor.fetchone()
        cursor.close()
        
        if not booking:
            flash('Booking details not found.', 'error')
            return render_template('receipt.html', booking=None, error="Booking details not found")
        
        print(f"RECEIPT DEBUG: Successfully loaded booking #{booking_id}")
        return render_template('receipt.html', booking=booking)
        
    except Exception as e:
        print(f"RECEIPT ERROR: {str(e)}")
        cursor.close()
        flash('Error loading receipt.', 'error')
        return render_template('receipt.html', booking=None, error=str(e))

# ------------------ PRINTABLE RECEIPT ------------------
@app.route('/print/receipt/<int:booking_id>')
def print_receipt(booking_id):
    if 'loggedin' not in session:
        flash('Please login to view receipt.', 'error')
        return redirect(url_for('login'))
    
    download_mode = request.args.get('download', 0, type=int)
    
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('user_dashboard'))
    
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                b.booking_id,
                b.hotel_id,
                b.room_type,
                b.check_in,
                b.check_out,
                b.guests,
                b.num_nights,
                COALESCE(b.base_price, 0) as base_price,
                COALESCE(b.peak_surcharge, 0) as peak_surcharge,
                COALESCE(b.room_type_surcharge, 0) as room_type_surcharge,
                COALESCE(b.guest_surcharge, 0) as guest_surcharge,
                COALESCE(b.subtotal, 0) as subtotal,
                COALESCE(b.advance_discount_percent, 0) as advance_discount_percent,
                COALESCE(b.advance_discount_amount, 0) as advance_discount_amount,
                COALESCE(b.total_price, 0) as total_price,
                b.guest_name,
                b.guest_email,
                b.guest_phone,
                b.special_requests,
                b.status,
                b.booking_date,
                h.title as hotel_name, 
                h.city, 
                DATE_FORMAT(b.check_in, '%d %b %Y') as check_in_formatted,
                DATE_FORMAT(b.check_out, '%d %b %Y') as check_out_formatted,
                DATE_FORMAT(b.booking_date, '%d %b %Y at %h:%i %p') as booking_date_full,
                u.username,
                u.email as user_email
            FROM bookings b
            JOIN hotels h ON b.hotel_id = h.hotel_id
            JOIN users u ON b.user_id = u.id
            WHERE b.booking_id = %s AND b.user_id = %s
        """, (booking_id, session['id']))
        
        booking = cursor.fetchone()
        cursor.close()
        
        if not booking:
            flash('Booking not found.', 'error')
            return redirect(url_for('user_dashboard'))
        
        return render_template('print_receipt.html', 
                             booking=booking,
                             download_mode=download_mode)
        
    except Exception as e:
        print(f"Error: {e}")
        cursor.close()
        flash('Error loading receipt.', 'error')
        return redirect(url_for('user_dashboard'))

# ------------------ DOWNLOAD RECEIPT ------------------
@app.route('/download/receipt/<int:booking_id>')
def download_receipt(booking_id):
    if 'loggedin' not in session:
        flash('Please login to download receipt.', 'error')
        return redirect(url_for('login'))
    
    return redirect(url_for('print_receipt', booking_id=booking_id))

# ------------------ BOOKING CANCELLATION ------------------
@app.route('/user/booking/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'loggedin' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT booking_id, status, user_id, total_price
            FROM bookings 
            WHERE booking_id = %s AND user_id = %s
        """, (booking_id, session['id']))
        
        booking = cursor.fetchone()
        
        if not booking:
            return jsonify({
                'success': False, 
                'message': 'Booking not found or you do not have permission to cancel it'
            })
        
        if booking['status'] != 'confirmed':
            return jsonify({
                'success': False, 
                'message': f'Cannot cancel booking with status: {booking["status"]}'
            })
        
        cursor.execute("""
            UPDATE bookings 
            SET status = 'cancelled', cancellation_date = NOW() 
            WHERE booking_id = %s
        """, (booking_id,))
        
        db.commit()
        cursor.close()
        
        return jsonify({
            'success': True, 
            'message': 'Booking cancelled successfully! Refund will be processed within 5-7 business days.'
        })
        
    except Exception as e:
        print(f"Error cancelling booking: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        cursor.close()
        return jsonify({
            'success': False, 
            'message': 'Error cancelling booking. Please try again or contact support.'
        })

# ------------------ LOGIN / REGISTER ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username_email = request.form['username_email']
        password = request.form['password']

        db = get_db()
        if not db:
            flash('Database connection error. Please try again.', 'error')
            return redirect(url_for('login'))
        
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, password, role, status FROM users WHERE (username=%s OR email=%s)",
            (username_email, username_email)
        )
        user = cursor.fetchone()
        cursor.close()

        if user and user['status'] == 0:
            flash("Your account is inactive. Contact admin.")
            return redirect(url_for('login'))

        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['status'] = user['status']
            session.permanent = True

            if 'redirect_after_login' in session:
                redirect_url = session.pop('redirect_after_login')
                return redirect(redirect_url)
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            msg = 'Invalid username or password'

    return render_template("login.html", msg=msg)

@app.route('/register', methods=['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        db = get_db()
        if not db:
            flash('Database connection error. Please try again.', 'error')
            return redirect(url_for('register'))
        
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s OR username=%s", (email, username))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password, email, role, status) VALUES (%s,%s,%s,%s,%s)",
                (username, hashed_password, email, 'user', 1)
            )
            db.commit()

            token = serializer.dumps(email, salt='email-confirm')
            link = f"http://localhost:5002/activate/{token}"

            email_msg = Message('Activate Your Account', recipients=[email])
            email_msg.body = f'Click the link to activate your account:\n{link}'
            mail.send(email_msg)

            msg = 'Registration successful! Check your email.'
        cursor.close()

    return render_template("register.html", msg=msg)

@app.route('/activate/<token>')
def activate(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
        db = get_db()
        if not db:
            flash('Database connection error. Please try again.', 'error')
            return redirect(url_for('register'))
        
        cursor = db.cursor()
        cursor.execute("UPDATE users SET status=1 WHERE email=%s", (email,))
        db.commit()
        cursor.close()
        flash('Account activated successfully! You can now login.')
        return redirect(url_for('login'))
    except:
        flash('Activation link is invalid or has expired.')
        return redirect(url_for('register'))

# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect(url_for('login')))
    response.set_cookie('username', '', expires=0)
    return response

# ==================== ADMIN DASHBOARD ====================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return render_template('admin/dashboard.html',
                             total_users=0,
                             total_bookings=0,
                             total_hotels=0,
                             total_revenue=0,
                             recent_bookings=[])
    
    cursor = db.cursor(dictionary=True)
    
    # Initialize ALL variables with default values FIRST
    total_users = 0
    total_bookings = 0
    total_hotels = 0
    total_revenue = 0
    recent_bookings = []
    
    try:
        # Get stats
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        result = cursor.fetchone()
        total_users = result['total_users'] if result else 0
        
        cursor.execute("SELECT COUNT(*) as total_bookings FROM bookings WHERE status = 'confirmed'")
        result = cursor.fetchone()
        total_bookings = result['total_bookings'] if result else 0
        
        cursor.execute("SELECT COUNT(*) as total_hotels FROM hotels")
        result = cursor.fetchone()
        total_hotels = result['total_hotels'] if result else 0
        
        cursor.execute("SELECT COALESCE(SUM(total_price), 0) as total_revenue FROM bookings WHERE status = 'confirmed'")
        result = cursor.fetchone()
        total_revenue = float(result['total_revenue']) if result and result['total_revenue'] else 0
        
        # Get recent bookings
        cursor.execute("""
            SELECT 
                b.booking_id,
                b.hotel_id,
                b.room_type,
                b.check_in,
                b.check_out,
                b.guests,
                b.num_nights,
                b.total_price,
                b.status,
                b.booking_date,
                b.guest_name,
                b.guest_email,
                b.guest_phone,
                b.special_requests,
                u.username as customer_name, 
                h.title as hotel_name,
                DATE_FORMAT(b.check_in, '%d %b %Y') as check_in_formatted,
                DATE_FORMAT(b.check_out, '%d %b %Y') as check_out_formatted
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN hotels h ON b.hotel_id = h.hotel_id
            ORDER BY b.booking_date DESC LIMIT 5
        """)
        recent_bookings = cursor.fetchall()
        
    except Exception as e:
        print(f"Error loading admin dashboard: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
    
    print(f"DEBUG - Dashboard stats: users={total_users}, bookings={total_bookings}, hotels={total_hotels}, revenue={total_revenue}")
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_bookings=total_bookings,
                         total_hotels=total_hotels,
                         total_revenue=total_revenue,
                         recent_bookings=recent_bookings)

# ==================== ADMIN HOTELS ROUTES ====================
@app.route('/admin/hotels')
@admin_required
def manage_hotels():
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return render_template('admin/manage_hotels.html', hotels=[])
    
    cursor = db.cursor(dictionary=True)
    
    try:
        # Get hotels with room count
        cursor.execute("""
            SELECT 
                h.hotel_id,
                h.title,
                h.city,
                h.price,
                h.address,
                COUNT(r.room_id) as total_rooms,
                SUM(CASE WHEN r.status = 'available' THEN 1 ELSE 0 END) as available_rooms
            FROM hotels h
            LEFT JOIN rooms r ON h.hotel_id = r.hotel_id
            GROUP BY h.hotel_id, h.title, h.city, h.price, h.address
            ORDER BY h.city, h.title
        """)
        hotels = cursor.fetchall()
        
        for hotel in hotels:
            print(f"DEBUG: {hotel['title']} - {hotel['total_rooms']} rooms, {hotel['available_rooms']} available")
        
        cursor.close()
        
        return render_template('admin/manage_hotels.html', hotels=hotels)
    except Exception as e:
        print(f"Error loading hotels: {e}")
        cursor.close()
        return render_template('admin/manage_hotels.html', hotels=[])

#-------------add hotel--------------------------------

@app.route('/admin/hotel/add', methods=['GET', 'POST'])
@admin_required
def add_hotel():
    print("DEBUG: add_hotel route called")
    
    if request.method == 'POST':
        print("DEBUG: POST request received")
        try:
            # Get form data
            name = request.form['name']
            city = request.form['city']
            price = request.form.get('standard_price_peak', 100.00)
            address = request.form.get('address', 'Hotel Address, City, Country')
            description = request.form.get('description', '')
            
            print(f"DEBUG: Form data - Name: {name}, City: {city}, Price: {price}")
            
            # Convert to appropriate types
            price = float(price) if price else 100.00
            
            db = get_db()
            if not db:
                flash('Database connection error. Please try again.', 'error')
                return redirect(url_for('add_hotel'))
            
            cursor = db.cursor()
            print("DEBUG: Executing SQL insert for hotel...")
            
            # 1. INSERT HOTEL
            cursor.execute('''
                INSERT INTO hotels (title, city, price, description, image, address)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (name, city, price, description, 'default.jpg', address))
            
            hotel_id = cursor.lastrowid
            print(f"DEBUG: Hotel created with ID: {hotel_id}")
            
            # 2. AUTOMATICALLY CREATE DEFAULT ROOMS FOR THIS HOTEL
            print("DEBUG: Creating default rooms...")
            
            # Create UNIQUE room numbers by combining hotel_id with room suffix
            room_prefix = str(hotel_id * 100)  # Creates 100, 200, 300, etc.
            
            default_rooms = [
                # (hotel_id, room_number, room_type, price, status, capacity, max_guests, price_multiplier, features)
                (hotel_id, f"{room_prefix}01", 'Single', price * 0.8, 'available', 1, 1, 1.0, 
                 'Single bed, TV, WiFi, En-suite bathroom'),
                
                (hotel_id, f"{room_prefix}02", 'Double', price, 'available', 2, 2, 1.2, 
                 'Double bed, TV, WiFi, Mini-fridge, En-suite bathroom'),
                
                (hotel_id, f"{room_prefix}03", 'Family', price * 1.2, 'available', 4, 4, 1.5, 
                 'Two double beds, TV, WiFi, Mini-fridge, Sofa, En-suite bathroom'),
            ]
            
            cursor.executemany('''
                INSERT INTO rooms (hotel_id, room_number, room_type, price, status, 
                                  capacity, max_guests, price_multiplier, features)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', default_rooms)
            
            rooms_added = cursor.rowcount
            print(f"DEBUG: Added {rooms_added} default rooms to hotel {hotel_id}")
            print(f"DEBUG: Room numbers: {default_rooms[0][1]}, {default_rooms[1][1]}, {default_rooms[2][1]}")
            
            db.commit()
            cursor.close()
            
            flash(f'Hotel "{name}" added successfully with {rooms_added} default rooms!', 'success')
            return redirect(url_for('manage_hotels'))
            
        except Exception as e:
            print(f"ERROR adding hotel: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Error adding hotel: {str(e)}', 'error')
            return redirect(url_for('add_hotel'))
    
    # GET request - show form
    print("DEBUG: Showing add hotel form")
    return render_template('admin/add_hotel.html')

#-------------edit hotel-----------------------------------------

@app.route('/admin/hotel/edit/<int:hotel_id>', methods=['GET', 'POST'])
@admin_required
def edit_hotel(hotel_id):
    if request.method == 'POST':
        try:
            name = request.form['name']
            city = request.form['city']
            price = float(request.form['price'])
            address = request.form.get('address', '')
            description = request.form.get('description', '')
            
            db = get_db()
            if not db:
                flash('Database connection error. Please try again.', 'error')
                return redirect(url_for('edit_hotel', hotel_id=hotel_id))
            
            cursor = db.cursor()
            cursor.execute('''
                UPDATE hotels SET 
                    title = %s, 
                    city = %s, 
                    price = %s, 
                    address = %s, 
                    description = %s
                WHERE hotel_id = %s
            ''', (name, city, price, address, description, hotel_id))
            
            db.commit()
            cursor.close()
            
            flash('Hotel updated successfully!', 'success')
            return redirect(url_for('manage_hotels'))
            
        except Exception as e:
            print(f"Error updating hotel: {str(e)}")
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('edit_hotel', hotel_id=hotel_id))
    
    # GET request - load hotel data
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_hotels'))
    
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM hotels WHERE hotel_id = %s', (hotel_id,))
    hotel = cursor.fetchone()
    cursor.close()
    
    if not hotel:
        flash('Hotel not found!', 'error')
        return redirect(url_for('manage_hotels'))
    
    return render_template('admin/edit_hotel.html', hotel=hotel)



#----------delete hotel-------------------------------------

@app.route('/admin/hotel/delete/<int:hotel_id>')
@admin_required
def delete_hotel(hotel_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_hotels'))
    
    cursor = db.cursor()
    
    try:
        cursor.execute('DELETE FROM hotels WHERE hotel_id = %s', (hotel_id,))
        db.commit()
        flash('Hotel deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('manage_hotels'))

# ==================== ADMIN ROOMS ROUTES ====================
@app.route('/admin/rooms')
@admin_required
def manage_rooms():
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return render_template('admin/manage_rooms.html', rooms=[], hotels=[])
    
    cursor = db.cursor(dictionary=True)
    
    hotel_id = request.args.get('hotel_id', type=int)
    
    try:
        if hotel_id:
            cursor.execute('''
                SELECT r.*, h.title as hotel_name, h.city 
                FROM rooms r 
                JOIN hotels h ON r.hotel_id = h.hotel_id 
                WHERE r.hotel_id = %s
                ORDER BY r.room_number
            ''', (hotel_id,))
        else:
            cursor.execute('''
                SELECT r.*, h.title as hotel_name, h.city 
                FROM rooms r 
                JOIN hotels h ON r.hotel_id = h.hotel_id 
                ORDER BY h.title, r.room_number
            ''')
        
        rooms = cursor.fetchall()
        
        cursor.execute('SELECT hotel_id, title, city FROM hotels ORDER BY title')
        hotels = cursor.fetchall()
        cursor.close()
        
        return render_template('admin/manage_rooms.html', rooms=rooms, hotels=hotels)
    except Exception as e:
        print(f"Error loading rooms: {e}")
        cursor.close()
        return render_template('admin/manage_rooms.html', rooms=[], hotels=[])

#------------add rooms------------------------------
@app.route('/admin/room/add', methods=['GET', 'POST'])
@admin_required
def add_room():
    if request.method == 'POST':
        try:
            hotel_id = int(request.form['hotel_id'])
            room_number = request.form['room_number']
            room_type = request.form['room_type']
            
            if room_type == 'standard':
                price_multiplier = 1.0
                max_guests = 1
            elif room_type == 'double':
                price_multiplier = 1.2
                max_guests = 2
            elif room_type == 'family':
                price_multiplier = 1.5
                max_guests = 4
            else:
                price_multiplier = 1.0
                max_guests = 1
            
            features = request.form.get('features', '')
            
            db = get_db()
            if not db:
                flash('Database connection error. Please try again.', 'error')
                return redirect(url_for('add_room'))
            
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO rooms (hotel_id, room_number, room_type, max_guests, 
                                 price_multiplier, features, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'available')
            ''', (hotel_id, room_number, room_type, max_guests, price_multiplier, features))
            
            db.commit()
            cursor.close()
            flash('Room added successfully!', 'success')
            return redirect(url_for('manage_rooms'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('add_room'))
    
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_rooms'))
    
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT hotel_id, title, city FROM hotels ORDER BY title')
    hotels = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/add_room.html', hotels=hotels)

#---------------unaviable-----------------------------
@app.route('/admin/room/mark_unavailable/<int:room_id>')
@admin_required
def mark_unavailable(room_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_rooms'))
    
    cursor = db.cursor()
    try:
        cursor.execute('UPDATE rooms SET status = "maintenance" WHERE room_id = %s', (room_id,))
        db.commit()
        flash('Room marked as unavailable for maintenance', 'warning')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
    return redirect(url_for('manage_rooms'))

#---------------available--------------------------
@app.route('/admin/room/mark_available/<int:room_id>')
@admin_required
def mark_available(room_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_rooms'))
    
    cursor = db.cursor()
    try:
        cursor.execute('UPDATE rooms SET status = "available" WHERE room_id = %s', (room_id,))
        db.commit()
        flash('Room marked as available', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
    return redirect(url_for('manage_rooms'))

#--------------booked---------------------

@app.route('/admin/room/mark_booked/<int:room_id>')
@admin_required
def mark_booked(room_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_rooms'))
    
    cursor = db.cursor()
    try:
        cursor.execute('UPDATE rooms SET status = "booked" WHERE room_id = %s', (room_id,))
        db.commit()
        flash('Room marked as booked', 'info')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
    return redirect(url_for('manage_rooms'))


# ==================== ADMIN DELETE ROOM ROUTE ====================
@app.route('/admin/room/delete/<int:room_id>')
@admin_required
def delete_room(room_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_rooms'))
    
    cursor = db.cursor()
    
    try:
        # First check if the room has any bookings
        cursor.execute('SELECT COUNT(*) as bookings FROM bookings WHERE room_id = %s', (room_id,))
        bookings = cursor.fetchone()['bookings']
        
        if bookings > 0:
            flash(f'Cannot delete room with {bookings} bookings! Please cancel bookings first.', 'error')
            return redirect(url_for('manage_rooms'))
        
        # Delete the room
        cursor.execute('DELETE FROM rooms WHERE room_id = %s', (room_id,))
        db.commit()
        
        flash('Room deleted successfully!', 'success')
        
    except Exception as e:
        print(f"Error deleting room: {str(e)}")
        flash(f'Error deleting room: {str(e)}', 'error')
        db.rollback()
    finally:
        cursor.close()
    
    return redirect(url_for('manage_rooms'))



# ==================== ADMIN EDIT ROOM ROUTE ====================
@app.route('/admin/room/edit/<int:room_id>', methods=['GET', 'POST'])
@admin_required
def edit_room(room_id):
    if request.method == 'POST':
        try:
            hotel_id = int(request.form['hotel_id'])
            room_number = request.form['room_number']
            room_type = request.form['room_type']
            price = float(request.form['price'])
            
            status = request.form['status']
            if status not in ['available', 'booked', 'maintenance']:
                status = 'available'  # Default
            
            capacity = int(request.form['capacity'])
            max_guests = int(request.form.get('max_guests', capacity))
            price_multiplier = float(request.form.get('price_multiplier', 1.0))
            features = request.form.get('features', '')
            
            db = get_db()
            if not db:
                flash('Database connection error. Please try again.', 'error')
                return redirect(url_for('edit_room', room_id=room_id))
            
            cursor = db.cursor()
            cursor.execute('''
                UPDATE rooms SET 
                    hotel_id = %s,
                    room_number = %s,
                    room_type = %s,
                    price = %s,
                    status = %s,
                    capacity = %s,
                    max_guests = %s,
                    price_multiplier = %s,
                    features = %s
                WHERE room_id = %s
            ''', (hotel_id, room_number, room_type, price, status, 
                  capacity, max_guests, price_multiplier, features, room_id))
            
            db.commit()
            flash('Room updated successfully!', 'success')
            cursor.close()
            return redirect(url_for('manage_rooms'))
            
        except Exception as e:
            print(f"Error updating room: {str(e)}")
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('edit_room', room_id=room_id))
    
    # GET request - load room data
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_rooms'))
    
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM rooms WHERE room_id = %s', (room_id,))
        room = cursor.fetchone()
        
        if not room:
            flash('Room not found!', 'error')
            cursor.close()
            return redirect(url_for('manage_rooms'))
        
        # Get hotels for dropdown
        cursor.execute('SELECT hotel_id, title, city FROM hotels ORDER BY title')
        hotels = cursor.fetchall()
        cursor.close()
        
        return render_template('admin/edit_room.html', room=room, hotels=hotels)
        
    except Exception as e:
        print(f"Error loading room data: {str(e)}")
        cursor.close()
        flash('Error loading room data', 'error')
        return redirect(url_for('manage_rooms'))

# ==================== ADMIN BOOKINGS ROUTES ====================
@app.route('/admin/bookings')
@admin_required
def manage_bookings():
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return render_template('admin/manage_bookings.html', bookings=[])
    
    cursor = db.cursor(dictionary=True)
    
    status_filter = request.args.get('status', '')
    
    try:
        query = """
            SELECT 
                b.*, 
                u.username as customer_name, u.email,
                h.title as hotel_name,
                DATE_FORMAT(b.check_in, '%d %b %Y') as check_in_formatted,
                DATE_FORMAT(b.check_out, '%d %b %Y') as check_out_formatted
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN hotels h ON b.hotel_id = h.hotel_id
        """
        
        params = []
        if status_filter:
            query += ' WHERE b.status = %s'
            params.append(status_filter)
        
        query += ' ORDER BY b.booking_date DESC'
        
        cursor.execute(query, tuple(params))
        bookings = cursor.fetchall()
        
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
                SUM(CASE WHEN status = 'confirmed' THEN total_price ELSE 0 END) as revenue
            FROM bookings
        ''')
        stats = cursor.fetchone()
        
        cursor.close()
        
        return render_template('admin/manage_bookings.html', 
                             bookings=bookings,
                             confirmed_count=stats['confirmed'] or 0,
                             pending_count=stats['pending'] or 0,
                             cancelled_count=stats['cancelled'] or 0,
                             total_revenue=stats['revenue'] or 0,
                             current_filter=status_filter)
    except Exception as e:
        print(f"Error loading bookings: {e}")
        cursor.close()
        return render_template('admin/manage_bookings.html', bookings=[])

@app.route('/admin/booking/confirm/<int:booking_id>')
@admin_required
def confirm_booking_admin(booking_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_bookings'))
    
    cursor = db.cursor()
    try:
        cursor.execute('UPDATE bookings SET status = "confirmed" WHERE booking_id = %s', (booking_id,))
        db.commit()
        flash('Booking confirmed successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
    return redirect(url_for('manage_bookings'))

@app.route('/admin/booking/cancel/<int:booking_id>')
@admin_required
def cancel_booking_admin(booking_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_bookings'))
    
    cursor = db.cursor()
    try:
        cursor.execute('UPDATE bookings SET status = "cancelled" WHERE booking_id = %s', (booking_id,))
        db.commit()
        flash('Booking cancelled successfully', 'warning')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
    return redirect(url_for('manage_bookings'))

# ==================== ADMIN USERS ROUTES ====================
@app.route('/admin/users')
@admin_required
def manage_users():
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return render_template('admin/manage_users.html', 
                             users=[],
                             admin_count=0,
                             active_today=0,
                             total_user_bookings=0)
    
    cursor = db.cursor(dictionary=True)
    
    try:
        # Check and add last_login column if it doesn't exist
        cursor.execute("""
            SELECT COUNT(*) as column_exists 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'last_login'
        """)
        column_exists = cursor.fetchone()['column_exists']
        
        if not column_exists:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL DEFAULT NULL AFTER created_at")
            db.commit()
        
        # Rest of your queries...
        cursor.execute('''
            SELECT u.*, 
                   (SELECT COUNT(*) FROM bookings WHERE user_id = u.id) as total_bookings
            FROM users u 
            ORDER BY u.created_at DESC
        ''')
        users = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as admin_count FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()['admin_count'] or 0
        
        cursor.execute("SELECT COUNT(*) as active_today FROM users WHERE DATE(last_login) = CURDATE()")
        active_today = cursor.fetchone()['active_today'] or 0
        
        cursor.execute("SELECT COUNT(*) as total_bookings FROM bookings")
        total_user_bookings_result = cursor.fetchone()
        total_user_bookings = total_user_bookings_result['total_bookings'] if total_user_bookings_result else 0
        
        cursor.close()
        
        return render_template('admin/manage_users.html', 
                             users=users,
                             admin_count=admin_count,
                             active_today=active_today,
                             total_user_bookings=total_user_bookings)
                             
    except Exception as e:
        print(f"Error in manage_users: {e}")
        cursor.close()
        return render_template('admin/manage_users.html', 
                             users=[],
                             admin_count=0,
                             active_today=0,
                             total_user_bookings=0)
    
    #--------------------resetpassword-------------------
@app.route('/admin/user/reset_password', methods=['POST'])
@admin_required
def reset_user_password():
    try:
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        
        if not user_id or not password:
            return jsonify({'success': False, 'message': 'Missing parameters'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        # Use werkzeug's generate_password_hash instead of sha256
        hashed_password = generate_password_hash(password)
        
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'Database connection error'}), 500
        
        cursor = db.cursor()
        cursor.execute(
            'UPDATE users SET password = %s WHERE id = %s', 
            (hashed_password, user_id)
        )
        db.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Password reset successfully'})
        
    except Exception as e:
        print(f"Error resetting password: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

#-----------------create user------------------------------
@app.route('/admin/user/add', methods=['POST'])
@admin_required
def add_user_admin():
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            full_name = request.form.get('full_name', '').strip()
            role = request.form.get('role', 'user')
            status = int(request.form.get('status', 1))
            
            # Basic validation
            errors = []
            
            # Username validation
            if not username:
                errors.append('Username is required')
            elif len(username) < 3 or len(username) > 20:
                errors.append('Username must be 3-20 characters')
            
            # Email validation
            if not email:
                errors.append('Email is required')
            elif '@' not in email or '.' not in email:
                errors.append('Invalid email format')
            
            # Password validation
            if not password:
                errors.append('Password is required')
            elif len(password) < 6:
                errors.append('Password must be at least 6 characters')
            elif password != confirm_password:
                errors.append('Passwords do not match')
            
            # Role validation
            if role not in ['user', 'admin']:
                errors.append('Invalid role selected')
            
            db = get_db()
            if not db:
                return jsonify({'success': False, 'message': 'Database connection error'}), 500
            
            # Check for existing user
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT id FROM users WHERE email = %s OR username = %s", 
                (email, username)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                errors.append('Email or username already exists')
            
            # If there are errors, return them
            if errors:
                cursor.close()
                return jsonify({
                    'success': False, 
                    'message': ' '.join(errors)
                }), 400
            
            # Hash the password
            hashed_password = generate_password_hash(password)
            
            # Insert new user
            cursor.execute("""
                INSERT INTO users (username, email, password, full_name, role, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (username, email, hashed_password, full_name if full_name else None, role, status))
            
            user_id = cursor.lastrowid
            db.commit()
            cursor.close()
            
            return jsonify({
                'success': True, 
                'message': f'User {username} created successfully!',
                'user_id': user_id
            })
            
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False, 
                'message': f'Server error: {str(e)}'
            }), 500
    
    return redirect(url_for('manage_users'))

# ==================== ADMIN UPDATE USER ROLE ROUTE ====================
@app.route('/admin/user/update_role', methods=['POST'])
@admin_required
def update_user_role():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        role = data.get('role')
        
        if not user_id or not role:
            return jsonify({
                'success': False, 
                'message': 'Missing required data'
            }), 400
        
        # Don't allow admin to modify their own role
        if int(user_id) == session.get('id'):
            return jsonify({
                'success': False, 
                'message': 'Cannot modify your own role'
            }), 400
        
        # Validate role
        if role not in ['user', 'admin']:
            return jsonify({
                'success': False, 
                'message': 'Invalid role'
            }), 400
        
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'Database connection error'}), 500
        
        cursor = db.cursor()
        cursor.execute(
            "UPDATE users SET role = %s WHERE id = %s",
            (role, user_id)
        )
        db.commit()
        cursor.close()
        
        return jsonify({
            'success': True, 
            'message': 'User role updated successfully'
        })
        
    except Exception as e:
        print(f"Error updating user role: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Server error: {str(e)}'
        }), 500
    

# ==================== ADMIN TOGGLE USER STATUS ROUTE ====================
@app.route('/admin/user/toggle_status/<int:user_id>')
@admin_required
def toggle_user_status(user_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_users'))
    
    cursor = db.cursor(dictionary=True)
    
    try:
        # Don't allow admin to deactivate themselves
        if user_id == session.get('id'):
            flash('Cannot modify your own account status', 'error')
            return redirect(url_for('manage_users'))
        
        # Get current status
        cursor.execute('SELECT status FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('manage_users'))
        
        # Toggle status (1 = active, 0 = inactive)
        new_status = 0 if user['status'] == 1 else 1
        status_text = 'activated' if new_status == 1 else 'deactivated'
        
        cursor.execute(
            'UPDATE users SET status = %s WHERE id = %s',
            (new_status, user_id)
        )
        db.commit()
        
        flash(f'User {status_text} successfully!', 'success')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('manage_users'))

#--------------------make admin to user user to admin----------------
@app.route('/admin/user/make_admin/<int:user_id>')
@admin_required
def make_admin(user_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_users'))
    
    cursor = db.cursor()
    try:
        cursor.execute('UPDATE users SET role = "admin" WHERE id = %s', (user_id,))
        db.commit()
        flash('User promoted to administrator successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
    return redirect(url_for('manage_users'))

@app.route('/admin/user/delete/<int:user_id>')
@admin_required
def delete_user_admin(user_id):
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('manage_users'))
    
    cursor = db.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) as bookings FROM bookings WHERE user_id = %s', (user_id,))
        bookings = cursor.fetchone()['bookings']
        
        if bookings > 0:
            flash(f'Cannot delete user with {bookings} bookings!', 'error')
            return redirect(url_for('manage_users'))
        
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        db.commit()
        flash('User deleted successfully', 'success')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('manage_users'))

# ==================== ADMIN REPORTS ROUTES ====================
@app.route('/admin/reports')
@admin_required
def admin_reports():
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return render_template('admin/reports.html',
                             monthly_data=[],
                             hotel_performance=[],
                             top_customers=[],
                             booking_trends=[],
                             total_revenue=0,
                             total_bookings=0,
                             avg_booking_value=0,
                             monthly_growth=0,
                             max_bookings=1)
    
    cursor = db.cursor(dictionary=True)
    
    period = request.args.get('period', 'this_month')
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    
    try:
        # Monthly sales report
        if period == 'this_month':
            cursor.execute('''
                SELECT 
                    DATE_FORMAT(booking_date, '%Y-%m') as month,
                    COUNT(*) as bookings,
                    SUM(total_price) as revenue,
                    AVG(total_price) as avg_booking_value
                FROM bookings 
                WHERE booking_date >= DATE_FORMAT(NOW(), '%Y-%m-01')
                GROUP BY DATE_FORMAT(booking_date, '%Y-%m')
            ''')
        elif period == 'custom' and date_from and date_to:
            cursor.execute('''
                SELECT 
                    DATE_FORMAT(booking_date, '%Y-%m') as month,
                    COUNT(*) as bookings,
                    SUM(total_price) as revenue,
                    AVG(total_price) as avg_booking_value
                FROM bookings 
                WHERE booking_date BETWEEN %s AND %s
                GROUP BY DATE_FORMAT(booking_date, '%Y-%m')
            ''', (date_from, date_to))
        else:
            cursor.execute('''
                SELECT 
                    DATE_FORMAT(booking_date, '%Y-%m') as month,
                    COUNT(*) as bookings,
                    SUM(total_price) as revenue,
                    AVG(total_price) as avg_booking_value
                FROM bookings 
                WHERE booking_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                GROUP BY DATE_FORMAT(booking_date, '%Y-%m')
                ORDER BY month DESC
            ''')
        
        monthly_data = cursor.fetchall()
        
        # Hotel performance
        cursor.execute('''
            SELECT 
                h.title as name,
                h.city,
                COUNT(b.booking_id) as bookings,
                COALESCE(SUM(b.total_price), 0) as revenue,
                ROUND((COUNT(b.booking_id) * 100.0 / (SELECT COUNT(*) FROM bookings WHERE status = 'confirmed')), 2) as occupancy,
                CASE 
                    WHEN COALESCE(SUM(b.total_price), 0) > 10000 THEN 1
                    ELSE -1
                END as profit
            FROM hotels h
            LEFT JOIN bookings b ON h.hotel_id = b.hotel_id AND b.status = 'confirmed'
            GROUP BY h.hotel_id
            ORDER BY revenue DESC
            LIMIT 10
        ''')
        hotel_performance = cursor.fetchall()
        
        # Top customers
        cursor.execute('''
            SELECT 
                u.username as name,
                u.email,
                COUNT(b.booking_id) as total_bookings,
                COALESCE(SUM(b.total_price), 0) as total_spent,
                DATE_FORMAT(u.created_at, '%Y-%m-%d') as member_since
            FROM users u
            LEFT JOIN bookings b ON u.id = b.user_id AND b.status = 'confirmed'
            GROUP BY u.id
            ORDER BY total_spent DESC
            LIMIT 10
        ''')
        top_customers = cursor.fetchall()
        
        # Booking trends
        cursor.execute('''
            SELECT 
                DATE_FORMAT(booking_date, '%b') as month,
                COUNT(*) as bookings
            FROM bookings 
            WHERE booking_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(booking_date, '%Y-%m'), DATE_FORMAT(booking_date, '%b')
            ORDER BY DATE_FORMAT(booking_date, '%Y-%m')
        ''')
        booking_trends = cursor.fetchall()
        
        # Calculate stats
        total_revenue = sum([row['revenue'] or 0 for row in monthly_data])
        total_bookings = sum([row['bookings'] or 0 for row in monthly_data])
        avg_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0
        monthly_growth = 12.5  # Example growth percentage
        
        # Calculate max bookings for chart scaling
        max_bookings = max([row['bookings'] or 0 for row in booking_trends]) if booking_trends else 1
        
    except Exception as e:
        print(f"Error loading reports: {e}")
        monthly_data = []
        hotel_performance = []
        top_customers = []
        booking_trends = []
        total_revenue = total_bookings = avg_booking_value = monthly_growth = 0
        max_bookings = 1
    finally:
        cursor.close()
    
    return render_template('admin/reports.html',
                         monthly_data=monthly_data,
                         hotel_performance=hotel_performance,
                         top_customers=top_customers,
                         booking_trends=booking_trends,
                         total_revenue=total_revenue,
                         total_bookings=total_bookings,
                         avg_booking_value=avg_booking_value,
                         monthly_growth=monthly_growth,
                         max_bookings=max_bookings)


@app.route('/admin/reports/pdf')
@admin_required
def generate_report_pdf():
    """Generate PDF report"""
    flash('PDF export feature coming soon!', 'info')
    return redirect(url_for('admin_reports'))

# ==================== ADMIN CURRENCIES ====================
@app.route('/admin/currencies')
@admin_required
def manage_currencies():
    """Manage currencies"""
    flash('Currency management feature coming soon!', 'info')
    return redirect(url_for('admin_dashboard'))

# ==================== ADMIN CHANGE PASSWORD ====================
@app.route('/admin/change_password', methods=['GET', 'POST'])
@admin_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        db = get_db()
        if not db:
            flash('Database connection error. Please try again.', 'error')
            return redirect(url_for('change_password'))
        
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT password FROM users WHERE id = %s', (session['id'],))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password'], current_password):
            flash('Current password is incorrect!', 'error')
            cursor.close()
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('New password and confirmation do not match!', 'error')
            cursor.close()
            return redirect(url_for('change_password'))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            cursor.close()
            return redirect(url_for('change_password'))
        
        hashed_password = generate_password_hash(new_password)
        cursor.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_password, session['id']))
        db.commit()
        cursor.close()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/change_password.html')

# ==================== USER DASHBOARD ====================
@app.route('/user/dashboard')
@user_required
def user_dashboard():
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return render_template('user/user_dashboard.html', 
                             stats={'total_bookings': 0, 'upcoming_bookings': 0, 
                                    'past_bookings': 0, 'total_spent': 0}, 
                             bookings=[])
    
    cursor = db.cursor(dictionary=True)
    
    try:
        user_id = session['id']
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_bookings,
                SUM(CASE WHEN check_in > CURDATE() AND status = 'confirmed' THEN 1 ELSE 0 END) as upcoming_bookings,
                SUM(CASE WHEN check_out < CURDATE() THEN 1 ELSE 0 END) as past_bookings,
                COALESCE(SUM(CASE WHEN status = 'confirmed' THEN total_price ELSE 0 END), 0) as total_spent
            FROM bookings 
            WHERE user_id = %s
        """, (user_id,))
        stats = cursor.fetchone() or {}
        
        cursor.execute("""
            SELECT 
                b.booking_id,
                b.hotel_id,
                b.room_type,
                b.check_in,
                b.check_out,
                b.guests,
                b.num_nights,
                b.total_price,
                b.status,
                b.booking_date,
                b.guest_name,
                b.guest_email,
                b.guest_phone,
                b.special_requests,
                h.title as hotel_name,
                h.city,
                h.image as hotel_image,
                DATE_FORMAT(b.check_in, '%d %b %Y') as check_in_formatted,
                DATE_FORMAT(b.check_out, '%d %b %Y') as check_out_formatted,
                DATE_FORMAT(b.booking_date, '%d %b %Y') as booking_date_formatted,
                CASE 
                    WHEN b.check_in > CURDATE() AND b.status = 'confirmed' THEN 1
                    ELSE 0
                END as is_upcoming
            FROM bookings b
            LEFT JOIN hotels h ON b.hotel_id = h.hotel_id
            WHERE b.user_id = %s
            ORDER BY b.booking_date DESC
            LIMIT 20
        """, (user_id,))
        bookings = cursor.fetchall()
        
        cursor.close()
        
        return render_template('user/user_dashboard.html', 
                             stats=stats, 
                             bookings=bookings)
        
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        cursor.close()
        return render_template('user/user_dashboard.html', 
                             stats={'total_bookings': 0, 'upcoming_bookings': 0, 
                                    'past_bookings': 0, 'total_spent': 0}, 
                             bookings=[])

# ==================== USER PROFILE ====================
@app.route('/user/profile')
@user_required
def user_profile():
    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return render_template('user_profile.html', 
                             user={}, 
                             stats={'total_bookings': 0},
                             recent_bookings=[])
    
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username, email, created_at FROM users WHERE id=%s",
        (session['id'],)
    )
    user = cursor.fetchone()
    
    cursor.execute(
        "SELECT COUNT(*) as total_bookings FROM bookings WHERE user_id=%s",
        (session['id'],)
    )
    stats = cursor.fetchone()
    
    cursor.execute("""
        SELECT b.*, h.title as hotel_name, h.city 
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.hotel_id
        WHERE b.user_id = %s
        ORDER BY b.booking_date DESC
        LIMIT 5
    """, (session['id'],))
    recent_bookings = cursor.fetchall()
    
    cursor.close()
    
    return render_template('user_profile.html', 
                         user=user, 
                         stats=stats,
                         recent_bookings=recent_bookings)

# ==================== EDIT PROFILE ====================
@app.route('/user/edit-profile', methods=['GET', 'POST'])
@user_required
def edit_profile():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        db = get_db()
        if not db:
            flash('Database connection error. Please try again.', 'error')
            return redirect(url_for('edit_profile'))
        
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "UPDATE users SET username=%s, email=%s WHERE id=%s",
            (username, email, session['id'])
        )
        db.commit()
        cursor.close()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_dashboard'))

    db = get_db()
    if not db:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('user_dashboard'))
    
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT username, email FROM users WHERE id=%s",
        (session['id'],)
    )
    user = cursor.fetchone()
    cursor.close()

    return render_template('edit_profile.html', user=user)

# ==================== MY BOOKINGS ====================
@app.route('/my_bookings')
@user_required
def my_bookings():
    return redirect(url_for('user_dashboard'))

# ==================== ADMIN SWITCH TO USER VIEW ====================
@app.route('/admin/switch-to-user')
@admin_required
def switch_to_user_view():
    """Allow admin to temporarily switch to user view"""
    return redirect(url_for('user_dashboard'))

# ==================== USER SWITCH TO ADMIN VIEW ====================
@app.route('/user/switch-to-admin')
@user_required
def switch_to_admin_view():
    """Allow users to request admin access"""
    flash('Please login as admin to access admin dashboard.', 'info')
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)