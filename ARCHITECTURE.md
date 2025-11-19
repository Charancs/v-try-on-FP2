# System Architecture - Virtual Try-On E-Commerce

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Browser                           │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────────┐  │
│  │   Shop UI  │  │  Cart UI   │  │  Virtual Try-On UI       │  │
│  │  (HTML/JS) │  │ (HTML/JS)  │  │  (WebSocket + Webcam)    │  │
│  └──────┬─────┘  └──────┬─────┘  └───────────┬──────────────┘  │
└─────────┼────────────────┼─────────────────────┼─────────────────┘
          │                │                     │
          │ HTTP/HTTPS     │ HTTP/HTTPS         │ WebSocket
          │                │                     │
┌─────────▼────────────────▼─────────────────────▼─────────────────┐
│                    Flask Web Server                               │
│                    (ecommerce_app.py)                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Route Handlers & Business Logic             │   │
│  │  • Authentication (login, register)                      │   │
│  │  • Product Management (catalog, details)                 │   │
│  │  • Shopping Cart (add, update, remove)                  │   │
│  │  • Order Processing (checkout, history)                  │   │
│  │  • Virtual Closet (save, retrieve)                      │   │
│  │  • Profile Management                                     │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                           │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │         Database Operations Module (database.py)         │   │
│  │  • Connection Pool Management                            │   │
│  │  • CRUD Operations                                       │   │
│  │  • Password Hashing (bcrypt)                            │   │
│  │  • Size Estimation Logic                                │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────────┘
                          │ MySQL Connection
                          │ (mysql-connector-python)
┌─────────────────────────▼───────────────────────────────────────┐
│                      MySQL Database                              │
│                   (virtual_tryon_db)                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       Tables                              │   │
│  │  • users (accounts, profiles)                            │   │
│  │  • products (catalog, pricing)                           │   │
│  │  • product_sizes (inventory)                             │   │
│  │  • cart (shopping cart items)                            │   │
│  │  • orders & order_items (order management)               │   │
│  │  • virtual_closet (saved outfits)                        │   │
│  │  • user_measurements (body metrics)                      │   │
│  │  • tryon_sessions (analytics)                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   WebSocket Server (Separate Thread)            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Virtual Try-On Frame Processing               │   │
│  │  1. Receive JPEG frames from browser webcam             │   │
│  │  2. Forward to GPU server for processing                │   │
│  │  3. Receive processed frames with garment overlay       │   │
│  │  4. Send back to browser for display                    │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────────┘
                          │ TCP Socket
                          │ (Binary Frame Transfer)
┌─────────────────────────▼───────────────────────────────────────┐
│                      GPU Processing Server                       │
│                   (172.28.80.80:9999)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Virtual Try-On AI Model Processing              │   │
│  │  • Pose Detection (SMPL)                                 │   │
│  │  • Body Segmentation (DensePose)                        │   │
│  │  • Garment Rendering                                     │   │
│  │  • Image Composition                                     │   │
│  │  • Body Measurement Extraction                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. User Registration & Login Flow
```
User → Register Form → Flask App → Validate Input
                                  ↓
                          Hash Password (bcrypt)
                                  ↓
                          Save to MySQL (users table)
                                  ↓
User ← Success Message ← Create Session ← Return user_id
```

### 2. Shopping & Checkout Flow
```
Browse Products → Select Product → View Details
                                      ↓
                              Try Virtual Try-On
                                      ↓
                              Get Size Recommendation
                                      ↓
                              Select Size & Quantity
                                      ↓
                              Add to Cart (MySQL: cart)
                                      ↓
                              View Cart → Update Quantities
                                      ↓
                              Checkout → Enter Shipping Info
                                      ↓
                              Place Order (MySQL: orders, order_items)
                                      ↓
                              Clear Cart → Order Confirmation
```

### 3. Virtual Try-On Flow
```
Product Page → Click "Virtual Try-On" → Request Camera Access
                                              ↓
                                     Start Webcam Capture
                                              ↓
                          Capture Frame (30 FPS) → Convert to JPEG
                                              ↓
                          Send via WebSocket → GPU Server
                                              ↓
                          GPU Processing:
                          • Detect Pose (keypoints)
                          • Segment Body Parts
                          • Apply Garment Texture
                          • Measure Body (chest, height, etc.)
                          • Estimate Size (S/M/L/XL/XXL)
                                              ↓
                          Receive Processed Frame ← GPU Server
                                              ↓
                          Display in Browser ← WebSocket
                                              ↓
                          Save Measurements → MySQL (user_measurements)
                                              ↓
                          Update Size Recommendation
```

### 4. Size Estimation Algorithm
```
Pose Detection → Extract Keypoints
                        ↓
                Calculate Distances:
                • Shoulder to Shoulder = Shoulder Width
                • Chest Left to Right = Chest Width
                • Head to Foot = Height
                        ↓
                Apply Size Rules:
                IF chest < 86cm → Size S
                ELSE IF chest < 96cm → Size M
                ELSE IF chest < 106cm → Size L
                ELSE IF chest < 116cm → Size XL
                ELSE → Size XXL
                        ↓
                Adjust for Height:
                IF height < 165cm → Size Down
                IF height > 185cm → Size Up
                        ↓
                Return Estimated Size
```

## Technology Stack Details

### Backend Technologies
```
Python 3.8+
├── Flask 2.3.0+ (Web Framework)
├── MySQL Connector 8.1.0+ (Database Driver)
├── bcrypt 4.0.1+ (Password Hashing)
├── websockets 11.0+ (WebSocket Server)
├── OpenCV 4.8.0+ (Image Processing)
└── NumPy 1.24.0+ (Numerical Computing)
```

### Frontend Technologies
```
HTML5
├── Semantic Markup
└── Video/Canvas API for Webcam

CSS3
├── Bootstrap 5.3.0 (UI Framework)
├── Bootstrap Icons (Icon Library)
└── Custom Gradients & Animations

JavaScript (ES6+)
├── jQuery 3.7.0 (DOM Manipulation)
├── WebSocket API (Real-time Communication)
└── MediaDevices API (Webcam Access)
```

### Database
```
MySQL 8.0+
├── InnoDB Engine (ACID Transactions)
├── Connection Pooling (5 connections)
├── Views (product_catalog, cart_details)
└── Foreign Key Constraints
```

## Security Architecture

### Authentication Layer
```
User Login
    ↓
Validate Credentials
    ↓
bcrypt.checkpw(input_password, stored_hash)
    ↓
Create Session (Flask session)
    ↓
Set Cookie (HttpOnly, Secure in production)
    ↓
Redirect to Protected Routes
```

### Authorization
```
Protected Routes (@login_required decorator)
    ↓
Check session['user_id'] exists
    ↓
If YES → Allow Access
If NO → Redirect to Login
```

### Database Security
```
SQL Injection Prevention:
• Parameterized Queries
• No String Concatenation
• mysql-connector escaping

Example:
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (username,)  # Safely escaped
)
```

## Performance Optimizations

### Database
- **Connection Pooling**: 5 persistent connections
- **Indexed Columns**: email, username, garment_id
- **Views**: Pre-computed joins for faster queries
- **Prepared Statements**: Query plan caching

### Frontend
- **Lazy Loading**: Images loaded on demand
- **CDN**: Bootstrap and jQuery from CDN
- **Minification**: Production builds should minify JS/CSS
- **Caching**: Static assets cached by browser

### WebSocket
- **Binary Transfer**: JPEG compression (quality 0.8)
- **Frame Rate**: 30 FPS for smooth experience
- **Async Processing**: Non-blocking I/O

## Deployment Architecture (Production)

```
Internet
    ↓
HTTPS (SSL/TLS)
    ↓
Load Balancer (Nginx/Apache)
    ↓
┌─────────────┬─────────────┬─────────────┐
│  Flask App  │  Flask App  │  Flask App  │
│  Instance 1 │  Instance 2 │  Instance 3 │
└──────┬──────┴──────┬──────┴──────┬───────┘
       │             │             │
       └─────────────┼─────────────┘
                     ↓
              MySQL Master
                     ↓
              MySQL Replicas
```

## Monitoring & Analytics

### Session Tracking
```
tryon_sessions table:
• session_id
• user_id
• product_id
• estimated_size
• session_duration (seconds)
• saved_to_closet (boolean)
• added_to_cart (boolean)
• created_at (timestamp)
```

### Metrics to Track
- User registrations per day
- Products viewed vs tried on
- Try-on to purchase conversion rate
- Average session duration
- Most popular products
- Size distribution
- Cart abandonment rate

## Scalability Considerations

### Horizontal Scaling
- Multiple Flask app instances behind load balancer
- Session storage in Redis/Memcached
- Static file serving via CDN
- Database read replicas

### Vertical Scaling
- Increase database connection pool
- More CPU cores for Flask workers
- GPU server cluster for try-on processing

### Caching Strategy
- Redis for session data
- Product catalog in memory cache
- CDN for images and static files

---

**System Designed For:**
- 1000+ concurrent users
- 10,000+ products
- Real-time virtual try-on
- Sub-second response times
- 99.9% uptime
