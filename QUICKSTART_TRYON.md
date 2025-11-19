# Quick Start - Virtual Try-On E-Commerce

## 🚀 Quick Commands

### 1. Test GPU Connection
```powershell
python test_gpu_connection.py
```

### 2. Run E-Commerce App
```powershell
python ecommerce_app.py
```

### 3. Access Website
```
http://localhost:5000
```

## 📋 Prerequisites

✅ MySQL running locally
✅ Dependencies installed: `pip install -r requirements_ecommerce.txt`
✅ `.env` file configured (copy from `.env.example`)
✅ GPU backend running on AWS: `python network_rtv_server.py`

## 🔧 Configuration

Edit `.env` file:

```env
# Database
DB_HOST=localhost
DB_PASSWORD=<your_mysql_password>

# GPU Server (AWS)
GPU_SERVER_IP=<your_aws_public_ip>
GPU_SERVER_PORT=9999

# Flask
FLASK_SECRET_KEY=<random_secret_key>
```

Generate secret key:
```powershell
python -c "import os; print(os.urandom(24).hex())"
```

## 📦 What's Included

- ✅ User Registration/Login
- ✅ Product Catalog (6 trained garments)
- ✅ Shopping Cart
- ✅ Checkout & Orders
- ✅ **Virtual Try-On** with real-time video
- ✅ Size Estimation (S/M/L/XL/XXL)
- ✅ Virtual Closet

## 🎯 Virtual Try-On Flow

1. **Login** → Register or sign in
2. **Shop** → Browse 6 trained garments
3. **Product Page** → Click "Virtual Try-On"
4. **Allow Webcam** → Grant browser permission
5. **Start Try-On** → See garment on your body in real-time
6. **Add to Cart** → Purchase if you like it

## 🌐 Ports

| Port | Service |
|------|---------|
| 5000 | Flask Web Server |
| 8765 | WebSocket Server |
| 9999 | GPU Backend (AWS) |

## 📖 Documentation

- `VIRTUAL_TRYON_SETUP.md` - Detailed setup guide
- `ENV_SETUP_GUIDE.md` - Environment variables guide
- `QUICKSTART.md` - Quick start guide
- `ARCHITECTURE.md` - System architecture

## 🐛 Troubleshooting

### Can't connect to GPU server
```powershell
python test_gpu_connection.py
```

### Database errors
1. Check MySQL is running
2. Verify credentials in `.env`
3. Run: `python ecommerce_app.py` (tables auto-create)

### Webcam not working
1. Check browser permissions
2. Try Chrome (recommended)
3. Check browser console (F12)

## 📁 Project Structure

```
ecommerce_app.py          # Main Flask + WebSocket server
network_rtv_server.py     # GPU backend (runs on AWS)
database.py               # Database operations
test_gpu_connection.py    # Connection test utility
templates/                # HTML templates
  ├── base.html
  ├── login.html
  ├── register.html
  ├── shop.html
  ├── product_detail.html
  ├── virtual_tryon.html  # Virtual try-on page
  └── ...
```

## 🎨 Available Garments

1. **Premium Jacket 17** (jin_17) - $89.99
2. **Classic Jacket 18** (jin_18) - $79.99
3. **Sport Jacket 22** (jin_22) - $94.99
4. **Professional Lab Coat 03** (lab_03) - $59.99
5. **Comfort Lab Coat 04** (lab_04) - $64.99
6. **Premium Lab Coat 07** (lab_07) - $74.99

All garments have trained models ready for virtual try-on!

## ⚡ Performance

- **30 FPS** real-time processing
- **GPU accelerated** on AWS backend
- **WebSocket streaming** for low latency
- **Auto size estimation** based on body measurements

## 🔐 Security

- Password hashing with bcrypt
- Session-based authentication
- Environment variables for secrets
- `.gitignore` protects `.env` file

## 📝 License

MIT License - See LICENSE file
