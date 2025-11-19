"""
Virtual Try-On E-Commerce Application
Main Flask application with authentication, shopping cart, and virtual try-on
"""
import asyncio
import websockets
import socket
import struct
import cv2
import numpy as np
import json
import pickle
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash, jsonify
import threading
import base64
import os
import glob
from functools import wraps
from datetime import timedelta
import database as db
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=int(os.getenv('SESSION_LIFETIME_DAYS', 7)))

# GPU server connection - Load from environment variables
GPU_SERVER_IP = os.getenv('GPU_SERVER_IP', '172.28.80.80')
GPU_SERVER_PORT = int(os.getenv('GPU_SERVER_PORT', 9999))

# Store active websocket clients
clients = set()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Home page - redirects based on login status"""
    if 'user_id' in session:
        return redirect(url_for('shop'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        # Validation
        if not all([username, email, password]):
            flash('Username, email, and password are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')
        
        # Create user
        result = db.create_user(username, email, password, full_name, phone)
        
        if result['success']:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result['error'], 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        result = db.authenticate_user(username, password)
        
        if result['success']:
            session.permanent = remember
            session['user_id'] = result['user']['user_id']
            session['username'] = result['user']['username']
            session['email'] = result['user']['email']
            session['full_name'] = result['user'].get('full_name', username)
            
            flash(f'Welcome back, {session["full_name"]}!', 'success')
            
            # Redirect to next page or shop
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('shop'))
        else:
            flash(result['error'], 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# ==================== SHOP & PRODUCT ROUTES ====================

@app.route('/shop')
@login_required
def shop():
    """Main shop page with product catalog"""
    result = db.get_all_products()
    
    if result['success']:
        products = result['products']
        
        # Get cart count
        cart_result = db.get_cart_items(session['user_id'])
        cart_count = len(cart_result['items']) if cart_result['success'] else 0
        
        return render_template('shop.html', products=products, cart_count=cart_count)
    else:
        flash('Error loading products', 'danger')
        return render_template('shop.html', products=[])

@app.route('/product/<int:product_id>')
@login_required
def product_detail(product_id):
    """Product detail page"""
    result = db.get_product_by_id(product_id)
    
    if result['success']:
        product = result['product']
        
        # Get user's estimated size if available
        measurements_result = db.get_user_measurements(session['user_id'])
        estimated_size = None
        if measurements_result['success'] and measurements_result['measurements']:
            estimated_size = measurements_result['measurements']['estimated_size']
        
        # Get cart count
        cart_result = db.get_cart_items(session['user_id'])
        cart_count = len(cart_result['items']) if cart_result['success'] else 0
        
        return render_template('product_detail.html', 
                             product=product, 
                             estimated_size=estimated_size,
                             cart_count=cart_count)
    else:
        flash('Product not found', 'danger')
        return redirect(url_for('shop'))

# ==================== SHOPPING CART ROUTES ====================

@app.route('/cart')
@login_required
def cart():
    """Shopping cart page"""
    result = db.get_cart_items(session['user_id'])
    
    if result['success']:
        return render_template('cart.html', 
                             cart_items=result['items'], 
                             total=result['total'])
    else:
        flash('Error loading cart', 'danger')
        return render_template('cart.html', cart_items=[], total=0)

@app.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to cart"""
    product_id = request.form.get('product_id', type=int)
    size = request.form.get('size')
    quantity = request.form.get('quantity', 1, type=int)
    
    if not all([product_id, size]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result = db.add_to_cart(session['user_id'], product_id, size, quantity)
    
    if result['success']:
        # Get updated cart count
        cart_result = db.get_cart_items(session['user_id'])
        cart_count = len(cart_result['items']) if cart_result['success'] else 0
        
        return jsonify({'success': True, 'cart_count': cart_count})
    else:
        return jsonify(result), 400

@app.route('/update-cart', methods=['POST'])
@login_required
def update_cart():
    """Update cart item quantity"""
    cart_id = request.form.get('cart_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    result = db.update_cart_item(cart_id, quantity)
    
    if result['success']:
        # Get updated cart
        cart_result = db.get_cart_items(session['user_id'])
        return jsonify({
            'success': True, 
            'total': cart_result['total'] if cart_result['success'] else 0
        })
    else:
        return jsonify(result), 400

@app.route('/remove-from-cart', methods=['POST'])
@login_required
def remove_from_cart():
    """Remove item from cart"""
    cart_id = request.form.get('cart_id', type=int)
    
    result = db.remove_from_cart(cart_id)
    
    if result['success']:
        cart_result = db.get_cart_items(session['user_id'])
        return jsonify({
            'success': True,
            'total': cart_result['total'] if cart_result['success'] else 0
        })
    else:
        return jsonify(result), 400

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page"""
    if request.method == 'POST':
        # Get cart items
        cart_result = db.get_cart_items(session['user_id'])
        
        if not cart_result['success'] or not cart_result['items']:
            flash('Your cart is empty', 'warning')
            return redirect(url_for('cart'))
        
        # Get shipping address
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        postal_code = request.form.get('postal_code')
        country = request.form.get('country')
        payment_method = request.form.get('payment_method', 'card')
        
        shipping_address = f"{address}, {city}, {state} {postal_code}, {country}"
        
        # Create order
        order_result = db.create_order(
            session['user_id'], 
            cart_result['items'], 
            shipping_address,
            payment_method
        )
        
        if order_result['success']:
            # Clear cart
            db.clear_cart(session['user_id'])
            
            flash(f'Order placed successfully! Order number: {order_result["order_number"]}', 'success')
            return redirect(url_for('orders'))
        else:
            flash('Error placing order', 'danger')
    
    # GET request - show checkout form
    cart_result = db.get_cart_items(session['user_id'])
    
    if not cart_result['success'] or not cart_result['items']:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('cart'))
    
    # Get user details for pre-filling form
    user_result = db.get_user_by_id(session['user_id'])
    user = user_result['user'] if user_result['success'] else {}
    
    return render_template('checkout.html', 
                         cart_items=cart_result['items'],
                         total=cart_result['total'],
                         user=user)

@app.route('/orders')
@login_required
def orders():
    """User orders page"""
    result = db.get_user_orders(session['user_id'])
    
    if result['success']:
        return render_template('orders.html', orders=result['orders'])
    else:
        flash('Error loading orders', 'danger')
        return render_template('orders.html', orders=[])

# ==================== VIRTUAL CLOSET ROUTES ====================

@app.route('/closet')
@login_required
def virtual_closet():
    """Virtual closet page"""
    result = db.get_virtual_closet(session['user_id'])
    
    if result['success']:
        return render_template('virtual_closet.html', items=result['items'])
    else:
        flash('Error loading virtual closet', 'danger')
        return render_template('virtual_closet.html', items=[])

@app.route('/add-to-closet', methods=['POST'])
@login_required
def add_to_closet():
    """Add item to virtual closet"""
    product_id = request.form.get('product_id', type=int)
    tried_on = request.form.get('tried_on') == 'true'
    favorited = request.form.get('favorited') == 'true'
    notes = request.form.get('notes')
    
    result = db.add_to_virtual_closet(session['user_id'], product_id, tried_on, favorited, notes)
    
    return jsonify(result)

# ==================== VIRTUAL TRY-ON ROUTES ====================

@app.route('/tryon/<int:product_id>')
@login_required
def virtual_tryon(product_id):
    """Virtual try-on page"""
    result = db.get_product_by_id(product_id)
    
    if result['success']:
        product = result['product']
        
        # Get user's measurements and estimated size
        measurements_result = db.get_user_measurements(session['user_id'])
        estimated_size = None
        measurements = None
        
        if measurements_result['success'] and measurements_result['measurements']:
            measurements = measurements_result['measurements']
            estimated_size = measurements['estimated_size']
        
        # Create try-on session
        session_result = db.create_tryon_session(session['user_id'], product_id, estimated_size)
        tryon_session_id = session_result['session_id'] if session_result['success'] else None
        
        return render_template('virtual_tryon.html', 
                             product=product, 
                             estimated_size=estimated_size,
                             measurements=measurements,
                             tryon_session_id=tryon_session_id)
    else:
        flash('Product not found', 'danger')
        return redirect(url_for('shop'))

@app.route('/save-measurements', methods=['POST'])
@login_required
def save_measurements():
    """Save body measurements from pose detection"""
    data = request.get_json()
    
    measurements = {
        'height_cm': data.get('height_cm'),
        'chest_cm': data.get('chest_cm'),
        'waist_cm': data.get('waist_cm'),
        'shoulder_cm': data.get('shoulder_cm'),
        'arm_length_cm': data.get('arm_length_cm'),
    }
    
    # Estimate size
    if measurements['chest_cm'] and measurements['height_cm']:
        estimated_size = db.estimate_size(measurements['chest_cm'], measurements['height_cm'])
        measurements['estimated_size'] = estimated_size
    
    result = db.save_user_measurements(session['user_id'], measurements)
    
    return jsonify(result)

# ==================== PROFILE ROUTES ====================

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    if request.method == 'POST':
        updates = {
            'full_name': request.form.get('full_name'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'postal_code': request.form.get('postal_code'),
            'country': request.form.get('country')
        }
        
        result = db.update_user_profile(session['user_id'], **updates)
        
        if result['success']:
            # Update session
            if updates['full_name']:
                session['full_name'] = updates['full_name']
            flash('Profile updated successfully', 'success')
        else:
            flash('Error updating profile', 'danger')
    
    # Get user details
    user_result = db.get_user_by_id(session['user_id'])
    user = user_result['user'] if user_result['success'] else {}
    
    # Get measurements
    measurements_result = db.get_user_measurements(session['user_id'])
    measurements = measurements_result['measurements'] if measurements_result['success'] else None
    
    return render_template('profile.html', user=user, measurements=measurements)

# ==================== STATIC FILE ROUTES ====================

@app.route('/static/garments/<filename>')
def serve_garment_image(filename):
    """Serve garment images from assets folder"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    garment_dir = os.path.join(base_dir, 'assets', 'garment_images')
    return send_from_directory(garment_dir, filename)

@app.route('/test-websocket')
def test_websocket():
    """Test page for WebSocket connection"""
    return render_template('websocket_test.html')

# ==================== WEBSOCKET HANDLER ====================

class GPUServerConnection:
    def __init__(self):
        self.socket = None
        self.connected = False
    
    def connect(self):
        """Connect to GPU server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((GPU_SERVER_IP, GPU_SERVER_PORT))
            self.connected = True
            print(f"✓ Connected to GPU server at {GPU_SERVER_IP}:{GPU_SERVER_PORT}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to GPU server: {e}")
            return False
    
    def send_frame(self, frame_data):
        """Send JPEG frame to GPU server"""
        try:
            size = len(frame_data)
            self.socket.sendall(struct.pack("Q", size))
            self.socket.sendall(frame_data)
            return True
        except Exception as e:
            print(f"Error sending frame: {e}")
            return False
    
    def receive_frame(self):
        """Receive processed frame from GPU server"""
        try:
            size_data = self.socket.recv(8)
            if not size_data or len(size_data) < 8:
                return None
            
            size = struct.unpack("Q", size_data)[0]
            
            if size & (1 << 63):
                return self.receive_frame()
            
            data = b''
            while len(data) < size:
                packet = self.socket.recv(min(4096, size - len(data)))
                if not packet:
                    return None
                data += packet
            
            return data
        except Exception as e:
            print(f"Error receiving frame: {e}")
            return None
    
    def send_garment_change(self, garment_id):
        """Send garment change command"""
        try:
            command = {'type': 'change_garment', 'id': garment_id}
            data = pickle.dumps(command)
            size = len(data)
            self.socket.sendall(struct.pack("Q", size | (1 << 63)))
            self.socket.sendall(data)
            print(f"✓ Sent garment change command: {garment_id}")
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
        self.connected = False

async def handle_websocket(websocket):
    """Handle WebSocket connection from browser"""
    clients.add(websocket)
    print(f"✓ New client connected. Total clients: {len(clients)}")
    
    # Create dedicated GPU connection for this client
    client_gpu = GPUServerConnection()
    
    try:
        # Connect to GPU server
        print("Attempting to connect to GPU server...")
        if not client_gpu.connect():
            print("✗ Failed to connect to GPU server")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Failed to connect to GPU server'
            }))
            return
        
        print("✓ Client connected to GPU server, ready to process frames")
        
        frame_count = 0
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'frame':
                    frame_count += 1
                    if frame_count % 100 == 0:
                        print(f"📹 Processed {frame_count} frames...")
                    
                    # Receive base64 encoded frame from browser
                    frame_b64 = data.get('data')
                    if not frame_b64:
                        continue
                    
                    # Decode base64 to JPEG bytes
                    try:
                        frame_data = base64.b64decode(frame_b64.split(',')[1])
                    except Exception as e:
                        print(f"✗ Error decoding frame: {e}")
                        continue
                    
                    # Send to GPU server
                    if client_gpu.send_frame(frame_data):
                        # Receive processed frame
                        processed_data = client_gpu.receive_frame()
                        
                        if processed_data:
                            # Send back to browser as base64
                            processed_b64 = base64.b64encode(processed_data).decode('utf-8')
                            await websocket.send(json.dumps({
                                'type': 'frame',
                                'data': f'data:image/jpeg;base64,{processed_b64}'
                            }))
                        else:
                            print("⚠ No processed frame received from GPU server")
                    else:
                        print("⚠ Failed to send frame to GPU server")
                
                elif msg_type == 'garment_change':
                    garment_id = data.get('garment_id')
                    print(f"🎨 Changing garment to: {garment_id}")
                    if 0 <= garment_id < 6:  # Only 6 garments available
                        if client_gpu.send_garment_change(garment_id):
                            await websocket.send(json.dumps({
                                'type': 'garment_changed',
                                'garment_id': garment_id
                            }))
                
            except json.JSONDecodeError as e:
                print(f"✗ JSON decode error: {e}")
            except Exception as e:
                print(f"✗ Error processing message: {e}")
                import traceback
                traceback.print_exc()
                try:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))
                except:
                    pass
    
    except websockets.exceptions.ConnectionClosed:
        print("✗ Client WebSocket disconnected")
    except Exception as e:
        print(f"✗ WebSocket handler error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client_gpu.close()
        clients.remove(websocket)
        print(f"✓ Client cleanup complete. Total clients: {len(clients)}")

async def start_websocket_server():
    """Start WebSocket server"""
    # Set max_size to 10MB to handle large frame data (default is 1MB)
    # Set ping_interval and ping_timeout to keep connection alive
    async with websockets.serve(
        handle_websocket, 
        "0.0.0.0", 
        8765, 
        max_size=10*1024*1024,
        ping_interval=None,  # Disable ping to avoid timeout issues
        ping_timeout=None    # Disable ping timeout
    ):
        print("✓ WebSocket server started on ws://0.0.0.0:8765 (max message size: 10MB)")
        await asyncio.Future()

def run_websocket_server():
    """Run WebSocket server in event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(start_websocket_server())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

def run_flask_app():
    """Run Flask app"""
    print("✓ Flask server starting on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    # Initialize database connection pool
    if not db.init_db_pool():
        print("✗ Failed to initialize database. Please check your MySQL configuration.")
        exit(1)
    
    # Start WebSocket server in separate thread
    ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
    ws_thread.start()
    
    # Run Flask app in main thread
    run_flask_app()
