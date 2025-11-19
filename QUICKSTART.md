# Quick Start Guide - Virtual Try-On E-Commerce

## Step 1: Install MySQL & Create Database
```bash
# Open MySQL Workbench
# Connect to your MySQL server
# Open and execute: database_schema.sql
```

## Step 2: Configure Database
Edit `database.py` line 11-17:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',              # Your MySQL username
    'password': 'your_password',  # Your MySQL password
    'database': 'virtual_tryon_db'
}
```

## Step 3: Install Dependencies
```bash
pip install -r requirements_ecommerce.txt
```

## Step 4: Run the Application
```bash
python ecommerce_app.py
```

## Step 5: Access the Website
Open browser: http://localhost:5000

## First Time Usage
1. Click "Register" to create account
2. Fill in username, email, password
3. Login with your credentials
4. Browse products in Shop
5. Try Virtual Try-On feature
6. Add items to cart
7. Checkout

## Testing Credentials (Create Your Own)
- Username: testuser
- Email: test@example.com
- Password: test123

## Available Products (All with Virtual Try-On)
1. Premium Jacket 17 - $89.99
2. Classic Jacket 18 - $79.99
3. Sport Jacket 22 - $94.99
4. Professional Lab Coat 03 - $59.99
5. Comfort Lab Coat 04 - $64.99
6. Premium Lab Coat 07 - $74.99

## Key Features
✓ User Registration & Login
✓ Product Catalog with Search
✓ Shopping Cart
✓ Real-time Virtual Try-On
✓ Size Estimation (S/M/L/XL/XXL)
✓ Virtual Closet
✓ Order Management
✓ Body Measurements

## Troubleshooting
**Can't connect to database?**
- Check MySQL is running
- Verify credentials in database.py

**Webcam not working?**
- Allow camera permission in browser
- Close other apps using camera

**GPU server error?**
- Check GPU server is running at 172.28.80.80:9999
- Update IP in ecommerce_app.py if different

## Support
See SETUP_GUIDE.md for detailed documentation
