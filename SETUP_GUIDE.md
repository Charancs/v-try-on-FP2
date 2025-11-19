# Virtual Try-On E-Commerce Platform - Setup Guide

## Overview
This is a complete e-commerce platform with virtual try-on capabilities, user authentication, shopping cart, order management, and personalized size recommendations.

## Features
✅ User Registration & Authentication  
✅ Product Catalog with 6 Trained Garments  
✅ Shopping Cart & Checkout  
✅ Real-time Virtual Try-On with Size Estimation  
✅ Virtual Closet for Saved Outfits  
✅ Order Management & Tracking  
✅ Body Measurement Detection  
✅ Personalized Size Recommendations (S, M, L, XL, XXL)

## Requirements

### Software Requirements
- Python 3.8+
- MySQL 8.0+ / MySQL Workbench
- Web Browser (Chrome, Firefox, Edge)
- Webcam (for virtual try-on)

### Python Dependencies
```
Flask>=2.3.0
mysql-connector-python>=8.1.0
bcrypt>=4.0.1
websockets>=11.0
opencv-python>=4.8.0
numpy>=1.24.0
pickle5 (for Python < 3.8)
```

## Installation Steps

### 1. Install MySQL and Create Database

1. **Install MySQL Server** (if not already installed)
   - Download from: https://dev.mysql.com/downloads/installer/
   - Install MySQL Workbench for easy management

2. **Create the Database**
   - Open MySQL Workbench
   - Connect to your MySQL server
   - Open the `database_schema.sql` file
   - Execute the entire script (this will create database, tables, and sample data)

3. **Verify Database Creation**
   ```sql
   USE virtual_tryon_db;
   SHOW TABLES;
   SELECT * FROM products;
   ```

### 2. Configure Database Connection

Edit `database.py` and update the database configuration:

```python
DB_CONFIG = {
    'host': 'localhost',          # Your MySQL host
    'port': 3306,                 # Your MySQL port
    'database': 'virtual_tryon_db',
    'user': 'root',               # Your MySQL username
    'password': 'your_password',  # Your MySQL password
    'pool_name': 'tryon_pool',
    'pool_size': 5
}
```

### 3. Install Python Dependencies

```bash
pip install Flask mysql-connector-python bcrypt websockets opencv-python numpy
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### 4. Verify GPU Server

Make sure your GPU server for virtual try-on processing is running at:
- IP: 172.28.80.80 (or update in `ecommerce_app.py`)
- Port: 9999

Update the GPU server settings in `ecommerce_app.py` if needed:
```python
GPU_SERVER_IP = "172.28.80.80"  # Change to your GPU server IP
GPU_SERVER_PORT = 9999          # Change to your GPU server port
```

## Running the Application

### Start the Application

```bash
python ecommerce_app.py
```

The application will start:
- **Web Server**: http://localhost:5000
- **WebSocket Server**: ws://localhost:8765

### Access the Application

1. Open your browser and go to: http://localhost:5000
2. You'll be redirected to the login page
3. Click "Register" to create a new account
4. Fill in the registration form
5. Login with your credentials
6. Start shopping!

## User Guide

### Registration & Login
1. Click "Register" on the homepage
2. Fill in:
   - Username (unique)
   - Email (unique)
   - Password (min 6 characters)
   - Full Name (optional)
   - Phone (optional)
3. Click "Register"
4. Login with your credentials

### Shopping
1. Browse products in the **Shop** page
2. Click "View Details" to see product information
3. Select size (or get recommendation from virtual try-on)
4. Click "Add to Cart"
5. View cart by clicking the cart icon in navigation
6. Proceed to checkout

### Virtual Try-On
1. On any product page, click "Virtual Try-On"
2. Allow camera access when prompted
3. Click the play button to start
4. Stand in front of the camera (upper body visible)
5. The system will:
   - Detect your pose
   - Apply the garment virtually
   - Estimate your size (S/M/L/XL/XXL)
6. Save to closet or add to cart

### Size Estimation
The system automatically estimates your size based on:
- **Chest measurement** (detected from pose)
- **Height** (detected from pose)
- **Shoulder width**

Size Chart:
- **S**: Chest < 86 cm
- **M**: Chest 86-95 cm  
- **L**: Chest 96-105 cm
- **XL**: Chest 106-115 cm
- **XXL**: Chest > 115 cm

### Virtual Closet
1. Click "My Closet" in navigation
2. View all saved and tried-on items
3. Click "Try Again" to retry virtual try-on
4. Click "View Details" to see product page

### Checkout & Orders
1. Add items to cart
2. Click cart icon → "Proceed to Checkout"
3. Fill in shipping address
4. Select payment method
5. Click "Place Order"
6. View orders in "Orders" page

## Database Schema

### Main Tables
- **users**: User accounts and profiles
- **products**: Product catalog with pricing
- **product_sizes**: Size availability per product
- **cart**: Shopping cart items
- **orders**: Order records
- **order_items**: Order line items
- **virtual_closet**: Saved outfits and favorites
- **user_measurements**: Body measurements
- **tryon_sessions**: Virtual try-on analytics

## Trained Garments

The system includes 6 garments with trained models:

1. **Premium Jacket 17** (jin_17) - $89.99 (10% off)
2. **Classic Jacket 18** (jin_18) - $79.99 (15% off)
3. **Sport Jacket 22** (jin_22) - $94.99 (5% off)
4. **Professional Lab Coat 03** (lab_03) - $59.99
5. **Comfort Lab Coat 04** (lab_04) - $64.99 (10% off)
6. **Premium Lab Coat 07** (lab_07) - $74.99

## Security Features
- ✅ Password hashing with bcrypt
- ✅ Session-based authentication
- ✅ SQL injection prevention
- ✅ CSRF protection (session management)
- ✅ Secure WebSocket connections

## Troubleshooting

### Database Connection Error
**Problem**: `Failed to initialize database`
**Solution**: 
1. Check MySQL is running
2. Verify credentials in `database.py`
3. Ensure database exists: `virtual_tryon_db`

### Webcam Not Working
**Problem**: Camera not accessible
**Solution**:
1. Check browser permissions (allow camera)
2. Ensure no other app is using the camera
3. Try different browser

### GPU Server Connection Failed
**Problem**: `Failed to connect to GPU server`
**Solution**:
1. Check GPU server is running
2. Verify IP and port in `ecommerce_app.py`
3. Check firewall settings

### Products Not Showing
**Problem**: Empty shop page
**Solution**:
1. Check database has products: `SELECT * FROM products;`
2. Re-run `database_schema.sql` to insert sample data

## Project Structure

```
v-try-on-FP2/
├── ecommerce_app.py          # Main Flask application
├── database.py                # Database operations module
├── database_schema.sql        # MySQL database schema
├── simple_web_server.py       # Original simple server (legacy)
├── requirements.txt           # Python dependencies
├── SETUP_GUIDE.md            # This file
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── shop.html             # Product catalog
│   ├── product_detail.html   # Product details
│   ├── cart.html             # Shopping cart
│   ├── checkout.html         # Checkout page
│   ├── orders.html           # Order history
│   ├── virtual_tryon.html    # Virtual try-on interface
│   ├── virtual_closet.html   # Saved outfits
│   └── profile.html          # User profile
└── assets/
    └── garment_images/        # Product images
        ├── jin_17_white_bg.jpg
        ├── jin_18_white_bg.jpg
        ├── jin_22_white_bg.jpg
        ├── lab_03_white_bg.jpg
        ├── lab_04_white_bg.jpg
        └── lab_07_white_bg.jpg
```

## API Endpoints

### Authentication
- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Shop & Products
- `GET /shop` - Product catalog
- `GET /product/<id>` - Product details

### Shopping Cart
- `GET /cart` - View cart
- `POST /add-to-cart` - Add item to cart
- `POST /update-cart` - Update cart item
- `POST /remove-from-cart` - Remove cart item

### Orders
- `GET/POST /checkout` - Checkout process
- `GET /orders` - Order history

### Virtual Try-On
- `GET /tryon/<product_id>` - Virtual try-on page
- `POST /save-measurements` - Save body measurements

### Virtual Closet
- `GET /closet` - View virtual closet
- `POST /add-to-closet` - Add to closet

### Profile
- `GET/POST /profile` - User profile

## Future Enhancements
- Payment gateway integration (Stripe, PayPal)
- Email notifications
- Product reviews and ratings
- Wishlist feature
- Social sharing
- Admin dashboard
- Inventory management
- Analytics and reporting

## Support
For issues or questions, please refer to the project documentation or contact the development team.

## License
This project is part of the Virtual Try-On research initiative.
