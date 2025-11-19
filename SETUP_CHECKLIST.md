# 📋 Setup Checklist - Virtual Try-On E-Commerce

Use this checklist to ensure everything is set up correctly.

## ✅ Pre-Installation Checklist

### Software Requirements
- [ ] Python 3.8 or higher installed
  - Check: `python --version` or `python3 --version`
- [ ] MySQL 8.0 or higher installed
  - Download: https://dev.mysql.com/downloads/installer/
- [ ] MySQL Workbench installed (optional but recommended)
- [ ] Modern web browser (Chrome/Firefox/Edge)
- [ ] Webcam connected (for virtual try-on)
- [ ] GPU server running at 172.28.80.80:9999 (or update IP)

---

## 🗄️ Database Setup Checklist

### Step 1: MySQL Service
- [ ] MySQL service is running
  - Windows: Check Services app
  - Mac/Linux: `sudo systemctl status mysql`
- [ ] Can connect to MySQL
  - Test: Open MySQL Workbench and connect

### Step 2: Create Database
- [ ] Open MySQL Workbench
- [ ] Connect to your MySQL server
- [ ] Open file: `database_schema.sql`
- [ ] Click "Execute" or press Ctrl+Shift+Enter
- [ ] Wait for execution to complete (should see success messages)

### Step 3: Verify Database
Run these queries in MySQL Workbench:
```sql
-- Check database exists
SHOW DATABASES LIKE 'virtual_tryon_db';

-- Use the database
USE virtual_tryon_db;

-- Check tables created (should see 8 tables)
SHOW TABLES;

-- Verify products loaded (should see 6 products)
SELECT product_id, product_name, price, garment_id FROM products;

-- Check product sizes (should see 30 rows: 6 products × 5 sizes)
SELECT COUNT(*) FROM product_sizes;
```

Expected Results:
- [ ] Database 'virtual_tryon_db' exists
- [ ] 8 tables present: users, products, product_sizes, cart, orders, order_items, virtual_closet, user_measurements, tryon_sessions
- [ ] 6 products in products table
- [ ] 30 size records in product_sizes table

---

## ⚙️ Configuration Checklist

### Step 1: Database Configuration
- [ ] Open `database.py` in text editor
- [ ] Locate lines 11-17 (DB_CONFIG section)
- [ ] Update with your MySQL credentials:

```python
DB_CONFIG = {
    'host': 'localhost',          # Usually localhost
    'port': 3306,                 # Default MySQL port
    'database': 'virtual_tryon_db',
    'user': 'root',               # YOUR MySQL username
    'password': 'YOUR_PASSWORD',  # YOUR MySQL password
    'pool_name': 'tryon_pool',
    'pool_size': 5
}
```

- [ ] Save the file

### Step 2: GPU Server Configuration (Optional)
If your GPU server is at a different IP/port:
- [ ] Open `ecommerce_app.py`
- [ ] Locate lines 17-18
- [ ] Update:
```python
GPU_SERVER_IP = "172.28.80.80"  # Change to your GPU server IP
GPU_SERVER_PORT = 9999          # Change to your GPU server port
```
- [ ] Save the file

---

## 📦 Python Dependencies Checklist

### Install Required Packages
- [ ] Navigate to project directory in terminal:
```bash
cd c:\Users\charanc\v-try-on-FP2
```

- [ ] Install dependencies:
```bash
pip install -r requirements_ecommerce.txt
```

### Verify Installation
Check each package:
```bash
pip list | grep Flask
pip list | grep mysql-connector-python
pip list | grep bcrypt
pip list | grep websockets
pip list | grep opencv-python
pip list | grep numpy
```

Expected versions:
- [ ] Flask >= 2.3.0
- [ ] mysql-connector-python >= 8.1.0
- [ ] bcrypt >= 4.0.1
- [ ] websockets >= 11.0
- [ ] opencv-python >= 4.8.0
- [ ] numpy >= 1.24.0

---

## 🚀 Application Launch Checklist

### Step 1: Pre-Launch Verification
- [ ] Database is running
- [ ] Database credentials configured correctly
- [ ] All Python packages installed
- [ ] Terminal/Command Prompt open in project directory

### Step 2: Start Application
- [ ] Run command:
```bash
python ecommerce_app.py
```

### Step 3: Verify Startup
You should see these messages:
- [ ] `✓ Database connection pool created successfully`
- [ ] `✓ WebSocket server started on ws://0.0.0.0:8765`
- [ ] `✓ Flask server starting on http://0.0.0.0:5000`
- [ ] No error messages

If you see errors, check:
- [ ] Database credentials correct
- [ ] MySQL service running
- [ ] Port 5000 not in use by another app
- [ ] Port 8765 not in use by another app

---

## 🌐 Browser Access Checklist

### Step 1: Open Application
- [ ] Open web browser
- [ ] Navigate to: `http://localhost:5000`
- [ ] Page loads without errors

### Step 2: Test Registration
- [ ] Click "Register" button
- [ ] Fill in registration form:
  - [ ] Username (unique)
  - [ ] Email (valid format)
  - [ ] Password (min 6 characters)
  - [ ] Confirm password (matches)
- [ ] Click "Register"
- [ ] See success message: "Registration successful! Please login."
- [ ] Redirected to login page

### Step 3: Test Login
- [ ] Enter username and password
- [ ] Click "Login"
- [ ] Successfully logged in
- [ ] Redirected to Shop page
- [ ] See welcome message with your name

---

## 🛍️ Feature Testing Checklist

### Shop Page
- [ ] All 6 products visible
- [ ] Product images loading
- [ ] Prices displayed correctly
- [ ] Brand names shown
- [ ] "View Details" button works
- [ ] "Virtual Try-On" button visible

### Product Detail Page
- [ ] Product information complete
- [ ] Size selector works
- [ ] Quantity controls functional
- [ ] "Add to Cart" button works
- [ ] Success message shown
- [ ] Cart badge updates

### Shopping Cart
- [ ] Cart page accessible
- [ ] Items displayed correctly
- [ ] Quantity update works
- [ ] Remove item works
- [ ] Total calculates correctly
- [ ] Free shipping message (if total > $50)
- [ ] "Proceed to Checkout" button works

### Virtual Try-On
- [ ] Camera access requested
- [ ] Camera permission granted
- [ ] Webcam feed visible
- [ ] Start button works
- [ ] Frame streaming active
- [ ] GPU server connected (if available)
- [ ] Size recommendation shown (if measurements detected)
- [ ] "Save to Closet" button works
- [ ] "Add to Cart" button works

### Checkout
- [ ] Shipping form displayed
- [ ] Form validation works
- [ ] Payment method selection works
- [ ] "Place Order" button functional
- [ ] Order created successfully
- [ ] Order number displayed
- [ ] Cart cleared after order
- [ ] Redirected to orders page

### Virtual Closet
- [ ] Closet page accessible
- [ ] Saved items displayed
- [ ] "Try Again" button works
- [ ] Favorite items marked

### Profile
- [ ] Profile page loads
- [ ] User information displayed
- [ ] Edit profile works
- [ ] Measurements shown (if available)

### Orders
- [ ] Order history loads
- [ ] Recent order visible
- [ ] Order details correct
- [ ] Status badges displayed

---

## 🔍 Troubleshooting Checklist

### Database Connection Issues
If you see: `Failed to initialize database`
- [ ] MySQL service is running
- [ ] Database name is correct: `virtual_tryon_db`
- [ ] Username is correct in `database.py`
- [ ] Password is correct in `database.py`
- [ ] Port 3306 is accessible
- [ ] No firewall blocking connection

### Import Errors
If you see: `ModuleNotFoundError`
- [ ] All packages installed: `pip install -r requirements_ecommerce.txt`
- [ ] Using correct Python version (3.8+)
- [ ] Virtual environment activated (if using one)

### Webcam Issues
If camera not working:
- [ ] Browser permissions granted for camera
- [ ] No other app using camera
- [ ] Try different browser
- [ ] Check camera device in Windows Settings

### GPU Server Issues
If virtual try-on not working:
- [ ] GPU server is running
- [ ] IP address is correct in `ecommerce_app.py`
- [ ] Port 9999 is accessible
- [ ] No firewall blocking connection
- [ ] Check WebSocket connection in browser console

### Port Already in Use
If you see: `Address already in use`
- [ ] Close other applications using port 5000
- [ ] Or change port in `ecommerce_app.py` (line 635)
- [ ] Kill existing Python processes

---

## 📊 Verification Queries

Run these in MySQL Workbench to verify setup:

```sql
-- Check tables exist
USE virtual_tryon_db;
SHOW TABLES;

-- Verify products
SELECT COUNT(*) as total_products FROM products;
-- Should return: 6

-- Check product details
SELECT garment_id, product_name, brand, price 
FROM products 
ORDER BY product_name;

-- Verify sizes
SELECT p.product_name, ps.size, ps.stock_quantity
FROM products p
JOIN product_sizes ps ON p.product_id = ps.product_id
ORDER BY p.product_name, ps.size;
-- Should return: 30 rows (6 products × 5 sizes)

-- Check if users can be created (after registration)
SELECT COUNT(*) as total_users FROM users;

-- View all tables structure
DESCRIBE users;
DESCRIBE products;
DESCRIBE cart;
DESCRIBE orders;
```

---

## ✅ Final Verification

### All Systems Go!
Check all these before declaring success:

**Database**
- [ ] ✅ MySQL running
- [ ] ✅ Database created with all tables
- [ ] ✅ Sample products loaded
- [ ] ✅ Connection working

**Application**
- [ ] ✅ Flask server running
- [ ] ✅ WebSocket server running
- [ ] ✅ No error messages in console
- [ ] ✅ Web page accessible

**Features**
- [ ] ✅ Registration works
- [ ] ✅ Login works
- [ ] ✅ Products display
- [ ] ✅ Shopping cart works
- [ ] ✅ Checkout works
- [ ] ✅ Virtual try-on accessible
- [ ] ✅ Profile accessible

**Optional**
- [ ] ✅ GPU server connected
- [ ] ✅ Webcam working
- [ ] ✅ Size estimation active

---

## 🎉 Success!

If all checkboxes are marked, congratulations! Your Virtual Try-On E-Commerce platform is fully operational.

### Quick Test Scenario:
1. Register new user → ✅
2. Login → ✅
3. Browse products → ✅
4. Try virtual try-on → ✅
5. Get size recommendation → ✅
6. Add to cart → ✅
7. Checkout → ✅
8. View order → ✅

---

## 📞 Need Help?

Refer to these documents:
- **QUICKSTART.md** - Quick start guide
- **SETUP_GUIDE.md** - Detailed setup instructions
- **README_ECOMMERCE.md** - Full documentation
- **ARCHITECTURE.md** - System architecture
- **PROJECT_SUMMARY.md** - Project overview

---

**Ready to Start Shopping! 🛍️**
