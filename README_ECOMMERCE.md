# Virtual Try-On E-Commerce Platform 🛍️👔

A complete e-commerce platform with real-time virtual try-on capabilities, built for the Virtual Try-On research project.

## 🌟 Features

### Core Features
- ✅ **User Authentication**: Secure registration and login with bcrypt password hashing
- ✅ **Product Catalog**: Browse 6 trained garments with detailed information
- ✅ **Shopping Cart**: Add, update, remove items with real-time total calculation
- ✅ **Checkout System**: Complete order placement with shipping details
- ✅ **Order Management**: Track order history and status

### Virtual Try-On Features
- ✅ **Real-time Try-On**: Live webcam-based virtual garment overlay
- ✅ **Size Estimation**: Automatic size recommendation (S/M/L/XL/XXL) based on body measurements
- ✅ **Body Measurements**: Pose detection for accurate measurements
- ✅ **Virtual Closet**: Save and organize tried-on outfits
- ✅ **Try-On Analytics**: Track try-on sessions and preferences

### Technical Features
- ✅ **MySQL Database**: Robust data storage with connection pooling
- ✅ **WebSocket Communication**: Real-time frame streaming for virtual try-on
- ✅ **Responsive UI**: Bootstrap 5 with modern, mobile-friendly design
- ✅ **Session Management**: Secure user sessions with remember-me functionality
- ✅ **RESTful API**: Clean API endpoints for all operations

## 📋 Problem Statement

This project addresses the need for a smart system that:
1. Uses real-time body pose detection from live camera feed
2. Accurately estimates user's clothing size
3. Provides live virtual try-on feature for garment visualization
4. Allows users to save preferences and outfits in a virtual closet
5. Offers personalized recommendations based on body measurements

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, Flask
- **Database**: MySQL 8.0+ with MySQL Workbench
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, jQuery
- **Real-time**: WebSockets (websockets library)
- **Computer Vision**: OpenCV, NumPy
- **Security**: bcrypt for password hashing
- **Session Management**: Flask sessions

## 🚀 Quick Start

### Prerequisites
```bash
- Python 3.8 or higher
- MySQL 8.0 or higher
- Webcam (for virtual try-on)
- Modern web browser (Chrome, Firefox, Edge)
```

### Installation

1. **Clone the repository**
```bash
cd v-try-on-FP2
```

2. **Install dependencies**
```bash
pip install -r requirements_ecommerce.txt
```

3. **Set up MySQL database**
   - Open MySQL Workbench
   - Connect to your MySQL server
   - Open `database_schema.sql`
   - Execute the entire script

4. **Configure database connection**
   - Edit `database.py`
   - Update lines 11-17 with your MySQL credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',              # Your MySQL username
    'password': 'your_password',  # Your MySQL password
    'database': 'virtual_tryon_db'
}
```

5. **Run the application**
```bash
python ecommerce_app.py
```

6. **Access the website**
   - Open browser: http://localhost:5000
   - Register a new account
   - Start shopping!

## 📁 Project Structure

```
v-try-on-FP2/
├── ecommerce_app.py           # Main Flask application
├── database.py                 # Database operations & models
├── database_schema.sql         # MySQL database schema
├── requirements_ecommerce.txt  # Python dependencies
├── SETUP_GUIDE.md             # Detailed setup instructions
├── QUICKSTART.md              # Quick start guide
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navbar
│   ├── login.html             # User login
│   ├── register.html          # User registration
│   ├── shop.html              # Product catalog
│   ├── product_detail.html    # Product details
│   ├── cart.html              # Shopping cart
│   ├── checkout.html          # Checkout process
│   ├── orders.html            # Order history
│   ├── virtual_tryon.html     # Virtual try-on interface
│   ├── virtual_closet.html    # Saved outfits
│   └── profile.html           # User profile
└── assets/
    └── garment_images/         # Product images
```

## 🎯 Available Products

All products include virtual try-on capability:

1. **Premium Jacket 17** - $89.99 (10% off) - JIN Fashion
2. **Classic Jacket 18** - $79.99 (15% off) - JIN Fashion
3. **Sport Jacket 22** - $94.99 (5% off) - JIN Fashion
4. **Professional Lab Coat 03** - $59.99 - MediWear Pro
5. **Comfort Lab Coat 04** - $64.99 (10% off) - MediWear Pro
6. **Premium Lab Coat 07** - $74.99 - MediWear Pro

## 📊 Database Schema

### Main Tables
- `users` - User accounts and authentication
- `products` - Product catalog with pricing
- `product_sizes` - Size availability (S/M/L/XL/XXL)
- `cart` - Shopping cart items
- `orders` - Order records
- `order_items` - Order line items
- `virtual_closet` - Saved outfits and favorites
- `user_measurements` - Body measurements from pose detection
- `tryon_sessions` - Virtual try-on analytics

## 🔐 Security Features

- **Password Hashing**: bcrypt with salt rounds
- **Session Security**: Secure session management
- **SQL Injection Prevention**: Parameterized queries
- **Input Validation**: Server-side validation
- **HTTPS Ready**: Prepared for SSL/TLS deployment

## 🎨 Size Estimation Algorithm

The system estimates clothing size based on:

```python
Size Chart:
- S (Small):    Chest < 86 cm
- M (Medium):   Chest 86-95 cm
- L (Large):    Chest 96-105 cm
- XL (X-Large): Chest 106-115 cm
- XXL (2X-Large): Chest > 115 cm

Adjustments based on height for better accuracy
```

## 🌐 API Endpoints

### Authentication
- `POST /register` - Create new user account
- `POST /login` - User authentication
- `GET /logout` - End user session

### Shopping
- `GET /shop` - Browse product catalog
- `GET /product/<id>` - View product details
- `POST /add-to-cart` - Add item to cart
- `GET /cart` - View shopping cart
- `POST /checkout` - Place order

### Virtual Try-On
- `GET /tryon/<id>` - Launch virtual try-on
- `POST /save-measurements` - Save body measurements
- `POST /add-to-closet` - Save outfit to virtual closet
- `GET /closet` - View virtual closet

### User Management
- `GET /profile` - View user profile
- `POST /profile` - Update profile
- `GET /orders` - View order history

## 🔧 Configuration

### GPU Server Settings
Edit `ecommerce_app.py`:
```python
GPU_SERVER_IP = "172.28.80.80"  # Your GPU server IP
GPU_SERVER_PORT = 9999          # Your GPU server port
```

### Database Settings
Edit `database.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'virtual_tryon_db',
    'user': 'your_username',
    'password': 'your_password'
}
```

## 🐛 Troubleshooting

### Database Connection Issues
```bash
Error: Failed to initialize database
Solution: 
1. Check MySQL service is running
2. Verify credentials in database.py
3. Ensure database 'virtual_tryon_db' exists
```

### Webcam Access Issues
```bash
Error: Camera not accessible
Solution:
1. Check browser permissions (allow camera)
2. Close other applications using camera
3. Try different browser
```

### GPU Server Connection
```bash
Error: Failed to connect to GPU server
Solution:
1. Verify GPU server is running
2. Check IP address and port
3. Check firewall settings
```

## 📚 Documentation

- **SETUP_GUIDE.md** - Comprehensive setup instructions
- **QUICKSTART.md** - Quick start guide
- **database_schema.sql** - Database documentation

## 🎓 User Guide

### For Shoppers
1. Register and create an account
2. Browse products in the Shop
3. Try virtual try-on to see how garments look
4. Get personalized size recommendations
5. Add items to cart
6. Complete checkout with shipping details
7. Track orders in Order History

### For Developers
- See SETUP_GUIDE.md for development setup
- Database schema in database_schema.sql
- API documentation in this README

## 🚀 Future Enhancements

- [ ] Payment gateway integration (Stripe/PayPal)
- [ ] Email notifications for orders
- [ ] Product reviews and ratings
- [ ] Wishlist feature
- [ ] Social media sharing
- [ ] Admin dashboard
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] AR try-on (mobile)
- [ ] Multi-language support

## 📄 License

This project is part of the Virtual Try-On research initiative.

## 🤝 Contributing

This is a research project. For questions or contributions, please contact the development team.

## 📞 Support

For issues:
1. Check SETUP_GUIDE.md
2. Review troubleshooting section
3. Contact project team

---

**Built with ❤️ for the Virtual Try-On Project**

*Bringing the future of online shopping to reality through computer vision and AI*
