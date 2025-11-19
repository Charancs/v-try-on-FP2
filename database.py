"""
Database connection and operations module for Virtual Try-On E-Commerce
Handles all database interactions with MySQL
"""
import mysql.connector
from mysql.connector import Error, pooling
import os
from contextlib import contextmanager
import bcrypt
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration - Load from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME', 'virtual_tryon_db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'pool_name': 'tryon_pool',
    'pool_size': 5
}

# Create connection pool
connection_pool = None

def create_tables():
    """Create all required tables if they don't exist"""
    try:
        # Connect without database first to create database if needed
        temp_config = DB_CONFIG.copy()
        database_name = temp_config.pop('database')
        temp_config.pop('pool_name', None)
        temp_config.pop('pool_size', None)
        
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        cursor.execute(f"USE {database_name}")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                phone VARCHAR(20),
                address TEXT,
                city VARCHAR(50),
                state VARCHAR(50),
                postal_code VARCHAR(10),
                country VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_username (username)
            )
        """)
        
        # Create user_measurements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_measurements (
                measurement_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                height_cm DECIMAL(5,2),
                weight_kg DECIMAL(5,2),
                chest_cm DECIMAL(5,2),
                waist_cm DECIMAL(5,2),
                shoulder_cm DECIMAL(5,2),
                arm_length_cm DECIMAL(5,2),
                estimated_size VARCHAR(5),
                measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            )
        """)
        
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INT AUTO_INCREMENT PRIMARY KEY,
                garment_id VARCHAR(50) UNIQUE NOT NULL,
                product_name VARCHAR(100) NOT NULL,
                brand VARCHAR(100),
                category VARCHAR(50),
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                discount_percent DECIMAL(5,2) DEFAULT 0,
                image_path VARCHAR(255),
                model_available BOOLEAN DEFAULT TRUE,
                in_stock BOOLEAN DEFAULT TRUE,
                stock_quantity INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_garment_id (garment_id),
                INDEX idx_category (category)
            )
        """)
        
        # Create product_sizes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_sizes (
                size_id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                size VARCHAR(5) NOT NULL,
                stock_quantity INT DEFAULT 0,
                available BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                UNIQUE KEY unique_product_size (product_id, size),
                INDEX idx_product_id (product_id)
            )
        """)
        
        # Create cart table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                cart_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                size VARCHAR(5) NOT NULL,
                quantity INT DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_product_size (user_id, product_id, size),
                INDEX idx_user_id (user_id)
            )
        """)
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                order_status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
                payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
                payment_method VARCHAR(50),
                shipping_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_order_number (order_number)
            )
        """)
        
        # Create order_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                size VARCHAR(5) NOT NULL,
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                INDEX idx_order_id (order_id)
            )
        """)
        
        # Create virtual_closet table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS virtual_closet (
                closet_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                tried_on BOOLEAN DEFAULT FALSE,
                favorited BOOLEAN DEFAULT FALSE,
                notes TEXT,
                tried_at TIMESTAMP NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_favorited (favorited)
            )
        """)
        
        # Create tryon_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tryon_sessions (
                session_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                estimated_size VARCHAR(5),
                session_duration INT,
                saved_to_closet BOOLEAN DEFAULT FALSE,
                added_to_cart BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            )
        """)
        
        # Check if products table is empty and insert sample data
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        if product_count == 0:
            # Insert sample products
            cursor.execute("""
                INSERT INTO products (garment_id, product_name, brand, category, description, price, discount_percent, image_path, model_available, stock_quantity) VALUES
                ('jin_17', 'Premium Jacket 17', 'JIN Fashion', 'Jacket', 'Stylish premium jacket with modern fit. Perfect for casual and semi-formal occasions. Made with high-quality materials for comfort and durability.', 89.99, 10, 'jin_17_white_bg.jpg', TRUE, 50),
                ('jin_18', 'Classic Jacket 18', 'JIN Fashion', 'Jacket', 'Classic design jacket that never goes out of style. Versatile and comfortable for everyday wear. Available in multiple sizes.', 79.99, 15, 'jin_18_white_bg.jpg', TRUE, 45),
                ('jin_22', 'Sport Jacket 22', 'JIN Fashion', 'Jacket', 'Athletic-inspired jacket with contemporary style. Perfect for active lifestyle and casual outings. Lightweight and breathable fabric.', 94.99, 5, 'jin_22_white_bg.jpg', TRUE, 40),
                ('lab_03', 'Professional Lab Coat 03', 'MediWear Pro', 'Lab Coat', 'Professional lab coat designed for medical professionals and laboratory work. Durable, comfortable, and easy to maintain. Multiple pockets for convenience.', 59.99, 0, 'lab_03_white_bg.jpg', TRUE, 60),
                ('lab_04', 'Comfort Lab Coat 04', 'MediWear Pro', 'Lab Coat', 'Comfort-focused lab coat with ergonomic design. Perfect for long hours of wear. Made with breathable fabric and reinforced stitching.', 64.99, 10, 'lab_04_white_bg.jpg', TRUE, 55),
                ('lab_07', 'Premium Lab Coat 07', 'MediWear Pro', 'Lab Coat', 'Premium quality lab coat with superior fabric and finish. Ideal for healthcare professionals who demand the best. Stain-resistant and easy-care.', 74.99, 0, 'lab_07_white_bg.jpg', TRUE, 50)
            """)
            
            # Insert sizes for all products
            cursor.execute("""
                INSERT INTO product_sizes (product_id, size, stock_quantity, available)
                SELECT product_id, 'S', 10, TRUE FROM products
                UNION ALL
                SELECT product_id, 'M', 15, TRUE FROM products
                UNION ALL
                SELECT product_id, 'L', 20, TRUE FROM products
                UNION ALL
                SELECT product_id, 'XL', 15, TRUE FROM products
                UNION ALL
                SELECT product_id, 'XXL', 10, TRUE FROM products
            """)
            
            print("✓ Sample product data inserted")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✓ All database tables created successfully")
        return True
    except Error as e:
        print(f"✗ Error creating tables: {e}")
        return False

def init_db_pool():
    """Initialize database connection pool"""
    global connection_pool
    try:
        # Create tables first
        create_tables()
        
        connection_pool = pooling.MySQLConnectionPool(**DB_CONFIG)
        print("✓ Database connection pool created successfully")
        return True
    except Error as e:
        print(f"✗ Error creating connection pool: {e}")
        return False

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    connection = None
    try:
        connection = connection_pool.get_connection()
        yield connection
    except Error as e:
        print(f"✗ Database connection error: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()

# ==================== USER MANAGEMENT ====================

def create_user(username, email, password, full_name=None, phone=None):
    """Create a new user account"""
    try:
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO users (username, email, password_hash, full_name, phone)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (username, email, password_hash, full_name, phone))
            conn.commit()
            user_id = cursor.lastrowid
            cursor.close()
            return {'success': True, 'user_id': user_id}
    except Error as e:
        if 'Duplicate entry' in str(e):
            if 'username' in str(e):
                return {'success': False, 'error': 'Username already exists'}
            elif 'email' in str(e):
                return {'success': False, 'error': 'Email already exists'}
        return {'success': False, 'error': str(e)}

def authenticate_user(username, password):
    """Authenticate user login"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT user_id, username, email, password_hash, full_name FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            cursor.close()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                del user['password_hash']  # Don't return password hash
                return {'success': True, 'user': user}
            else:
                return {'success': False, 'error': 'Invalid username or password'}
    except Error as e:
        return {'success': False, 'error': str(e)}

def get_user_by_id(user_id):
    """Get user details by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT user_id, username, email, full_name, phone, address, 
                       city, state, postal_code, country, created_at
                FROM users WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            cursor.close()
            return {'success': True, 'user': user} if user else {'success': False, 'error': 'User not found'}
    except Error as e:
        return {'success': False, 'error': str(e)}

def update_user_profile(user_id, **kwargs):
    """Update user profile information"""
    try:
        allowed_fields = ['full_name', 'phone', 'address', 'city', 'state', 'postal_code', 'country']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
        
        if not updates:
            return {'success': False, 'error': 'No valid fields to update'}
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
            query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
            cursor.execute(query, list(updates.values()) + [user_id])
            conn.commit()
            cursor.close()
            return {'success': True}
    except Error as e:
        return {'success': False, 'error': str(e)}

# ==================== PRODUCT MANAGEMENT ====================

def get_all_products():
    """Get all products from catalog - only the 6 trained garments"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    product_id, garment_id, product_name, brand, category,
                    description, price, discount_percent,
                    ROUND(price * (1 - discount_percent/100), 2) AS discounted_price,
                    image_path, model_available, in_stock, stock_quantity
                FROM products 
                WHERE garment_id IN ('jin_17', 'jin_18', 'jin_22', 'lab_03', 'lab_04', 'lab_07')
                AND in_stock = TRUE
                ORDER BY category, product_name
            """
            cursor.execute(query)
            products = cursor.fetchall()
            cursor.close()
            return {'success': True, 'products': products}
    except Error as e:
        return {'success': False, 'error': str(e)}

def get_product_by_id(product_id):
    """Get product details by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    product_id, garment_id, product_name, brand, category,
                    description, price, discount_percent,
                    ROUND(price * (1 - discount_percent/100), 2) AS discounted_price,
                    image_path, model_available, in_stock, stock_quantity
                FROM products 
                WHERE product_id = %s
            """
            cursor.execute(query, (product_id,))
            product = cursor.fetchone()
            
            # Get available sizes
            if product:
                cursor.execute(
                    "SELECT size, stock_quantity FROM product_sizes WHERE product_id = %s AND available = TRUE",
                    (product_id,)
                )
                product['sizes'] = cursor.fetchall()
            
            cursor.close()
            return {'success': True, 'product': product} if product else {'success': False, 'error': 'Product not found'}
    except Error as e:
        return {'success': False, 'error': str(e)}

def get_product_by_garment_id(garment_id):
    """Get product by garment_id (e.g., 'jin_17')"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    product_id, garment_id, product_name, brand, category,
                    description, price, discount_percent,
                    ROUND(price * (1 - discount_percent/100), 2) AS discounted_price,
                    image_path, model_available, in_stock, stock_quantity
                FROM products 
                WHERE garment_id = %s
            """
            cursor.execute(query, (garment_id,))
            product = cursor.fetchone()
            
            if product:
                cursor.execute(
                    "SELECT size, stock_quantity FROM product_sizes WHERE product_id = %s AND available = TRUE",
                    (product['product_id'],)
                )
                product['sizes'] = cursor.fetchall()
            
            cursor.close()
            return {'success': True, 'product': product} if product else {'success': False, 'error': 'Product not found'}
    except Error as e:
        return {'success': False, 'error': str(e)}

# ==================== SHOPPING CART ====================

def add_to_cart(user_id, product_id, size, quantity=1):
    """Add item to shopping cart"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Check if item already exists
            cursor.execute(
                "SELECT cart_id, quantity FROM cart WHERE user_id = %s AND product_id = %s AND size = %s",
                (user_id, product_id, size)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update quantity
                new_quantity = existing[1] + quantity
                cursor.execute(
                    "UPDATE cart SET quantity = %s WHERE cart_id = %s",
                    (new_quantity, existing[0])
                )
            else:
                # Insert new item
                cursor.execute(
                    "INSERT INTO cart (user_id, product_id, size, quantity) VALUES (%s, %s, %s, %s)",
                    (user_id, product_id, size, quantity)
                )
            
            conn.commit()
            cursor.close()
            return {'success': True}
    except Error as e:
        return {'success': False, 'error': str(e)}

def get_cart_items(user_id):
    """Get all items in user's cart"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    c.cart_id, c.user_id, c.quantity, c.size, c.added_at,
                    p.product_id, p.product_name, p.brand, p.image_path,
                    p.price, p.discount_percent,
                    ROUND(p.price * (1 - p.discount_percent/100), 2) AS unit_price,
                    ROUND(p.price * (1 - p.discount_percent/100) * c.quantity, 2) AS subtotal
                FROM cart c
                JOIN products p ON c.product_id = p.product_id
                WHERE c.user_id = %s
                ORDER BY c.added_at DESC
            """
            cursor.execute(query, (user_id,))
            items = cursor.fetchall()
            
            # Calculate total
            total = sum(item['subtotal'] for item in items)
            
            cursor.close()
            return {'success': True, 'items': items, 'total': total}
    except Error as e:
        return {'success': False, 'error': str(e)}

def update_cart_item(cart_id, quantity):
    """Update cart item quantity"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if quantity > 0:
                cursor.execute("UPDATE cart SET quantity = %s WHERE cart_id = %s", (quantity, cart_id))
            else:
                cursor.execute("DELETE FROM cart WHERE cart_id = %s", (cart_id,))
            conn.commit()
            cursor.close()
            return {'success': True}
    except Error as e:
        return {'success': False, 'error': str(e)}

def remove_from_cart(cart_id):
    """Remove item from cart"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE cart_id = %s", (cart_id,))
            conn.commit()
            cursor.close()
            return {'success': True}
    except Error as e:
        return {'success': False, 'error': str(e)}

def clear_cart(user_id):
    """Clear all items from user's cart"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
            conn.commit()
            cursor.close()
            return {'success': True}
    except Error as e:
        return {'success': False, 'error': str(e)}

# ==================== ORDERS ====================

def create_order(user_id, cart_items, shipping_address, payment_method='card'):
    """Create order from cart items"""
    try:
        import random
        order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate total
            total = sum(item['subtotal'] for item in cart_items)
            
            # Create order
            cursor.execute(
                """INSERT INTO orders (user_id, order_number, total_amount, shipping_address, payment_method)
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, order_number, total, shipping_address, payment_method)
            )
            order_id = cursor.lastrowid
            
            # Create order items
            for item in cart_items:
                cursor.execute(
                    """INSERT INTO order_items (order_id, product_id, size, quantity, unit_price, subtotal)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (order_id, item['product_id'], item['size'], item['quantity'], 
                     item['unit_price'], item['subtotal'])
                )
            
            conn.commit()
            cursor.close()
            return {'success': True, 'order_id': order_id, 'order_number': order_number}
    except Error as e:
        return {'success': False, 'error': str(e)}

def get_user_orders(user_id):
    """Get all orders for a user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT order_id, order_number, total_amount, order_status, 
                       payment_status, created_at 
                FROM orders 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """
            cursor.execute(query, (user_id,))
            orders = cursor.fetchall()
            cursor.close()
            return {'success': True, 'orders': orders}
    except Error as e:
        return {'success': False, 'error': str(e)}

# ==================== VIRTUAL CLOSET ====================

def add_to_virtual_closet(user_id, product_id, tried_on=False, favorited=False, notes=None):
    """Add item to virtual closet"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            tried_at = datetime.now() if tried_on else None
            cursor.execute(
                """INSERT INTO virtual_closet (user_id, product_id, tried_on, favorited, notes, tried_at)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE tried_on = %s, favorited = %s, tried_at = %s""",
                (user_id, product_id, tried_on, favorited, notes, tried_at, tried_on, favorited, tried_at)
            )
            conn.commit()
            cursor.close()
            return {'success': True}
    except Error as e:
        return {'success': False, 'error': str(e)}

def get_virtual_closet(user_id, favorited_only=False):
    """Get user's virtual closet items"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT vc.*, p.product_name, p.brand, p.image_path, p.price, p.category
                FROM virtual_closet vc
                JOIN products p ON vc.product_id = p.product_id
                WHERE vc.user_id = %s
            """
            if favorited_only:
                query += " AND vc.favorited = TRUE"
            query += " ORDER BY vc.added_at DESC"
            
            cursor.execute(query, (user_id,))
            items = cursor.fetchall()
            cursor.close()
            return {'success': True, 'items': items}
    except Error as e:
        return {'success': False, 'error': str(e)}

# ==================== BODY MEASUREMENTS & SIZE ESTIMATION ====================

def save_user_measurements(user_id, measurements):
    """Save user body measurements"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO user_measurements 
                (user_id, height_cm, weight_kg, chest_cm, waist_cm, shoulder_cm, arm_length_cm, estimated_size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                user_id,
                measurements.get('height_cm'),
                measurements.get('weight_kg'),
                measurements.get('chest_cm'),
                measurements.get('waist_cm'),
                measurements.get('shoulder_cm'),
                measurements.get('arm_length_cm'),
                measurements.get('estimated_size')
            ))
            conn.commit()
            cursor.close()
            return {'success': True}
    except Error as e:
        return {'success': False, 'error': str(e)}

def get_user_measurements(user_id):
    """Get latest user measurements"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT * FROM user_measurements 
                WHERE user_id = %s 
                ORDER BY measured_at DESC 
                LIMIT 1
            """
            cursor.execute(query, (user_id,))
            measurements = cursor.fetchone()
            cursor.close()
            return {'success': True, 'measurements': measurements}
    except Error as e:
        return {'success': False, 'error': str(e)}

def estimate_size(chest_cm, height_cm):
    """Estimate clothing size based on measurements"""
    # Simple size estimation logic
    if chest_cm < 86:
        size = 'S'
    elif chest_cm < 96:
        size = 'M'
    elif chest_cm < 106:
        size = 'L'
    elif chest_cm < 116:
        size = 'XL'
    else:
        size = 'XXL'
    
    # Adjust based on height
    if height_cm < 165 and size in ['L', 'XL', 'XXL']:
        sizes = ['S', 'M', 'L', 'XL', 'XXL']
        size = sizes[max(0, sizes.index(size) - 1)]
    elif height_cm > 185 and size in ['S', 'M']:
        sizes = ['S', 'M', 'L', 'XL', 'XXL']
        size = sizes[min(4, sizes.index(size) + 1)]
    
    return size

# ==================== TRY-ON SESSIONS ====================

def create_tryon_session(user_id, product_id, estimated_size=None):
    """Create a virtual try-on session record"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO tryon_sessions (user_id, product_id, estimated_size)
                   VALUES (%s, %s, %s)""",
                (user_id, product_id, estimated_size)
            )
            conn.commit()
            session_id = cursor.lastrowid
            cursor.close()
            return {'success': True, 'session_id': session_id}
    except Error as e:
        return {'success': False, 'error': str(e)}

def update_tryon_session(session_id, duration=None, saved_to_closet=False, added_to_cart=False):
    """Update try-on session details"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            updates = []
            values = []
            
            if duration is not None:
                updates.append("session_duration = %s")
                values.append(duration)
            if saved_to_closet:
                updates.append("saved_to_closet = TRUE")
            if added_to_cart:
                updates.append("added_to_cart = TRUE")
            
            if updates:
                query = f"UPDATE tryon_sessions SET {', '.join(updates)} WHERE session_id = %s"
                values.append(session_id)
                cursor.execute(query, values)
                conn.commit()
            
            cursor.close()
            return {'success': True}
    except Error as e:
        return {'success': False, 'error': str(e)}

# Initialize connection pool when module is imported
if __name__ != '__main__':
    init_db_pool()
