# Environment Variables Setup Guide

## Quick Setup

1. **Copy the example file:**
   ```bash
   copy .env.example .env
   ```
   Or on Mac/Linux:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your actual values:**
   - Update `DB_PASSWORD` with your MySQL password
   - Update `FLASK_SECRET_KEY` with a random secret key
   - Update `GPU_SERVER_IP` if your GPU server is at a different address

3. **Generate a secure Flask secret key:**
   ```bash
   python -c "import os; print(os.urandom(24).hex())"
   ```
   Copy the output and use it as your `FLASK_SECRET_KEY`

## Environment Variables Explained

### Database Configuration
```
DB_HOST=localhost          # MySQL server host
DB_PORT=3306              # MySQL server port
DB_NAME=virtual_tryon_db  # Database name
DB_USER=root              # MySQL username
DB_PASSWORD=your_password # MySQL password (CHANGE THIS!)
```

### Flask Configuration
```
FLASK_SECRET_KEY=xxx      # Secret key for session encryption (CHANGE THIS!)
FLASK_HOST=0.0.0.0       # Server host (0.0.0.0 = all interfaces)
FLASK_PORT=5000          # Server port
FLASK_DEBUG=False        # Debug mode (set to True for development)
```

### GPU Server Configuration
```
GPU_SERVER_IP=172.28.80.80  # GPU server IP address
GPU_SERVER_PORT=9999         # GPU server port
```

### Session Configuration
```
SESSION_LIFETIME_DAYS=7   # How many days sessions last
```

## Security Notes

⚠️ **IMPORTANT:** 
- **NEVER** commit the `.env` file to version control
- The `.env` file is already in `.gitignore`
- Only commit `.env.example` with dummy values
- Each developer/server should have their own `.env` file
- Keep your database password secure
- Generate a unique `FLASK_SECRET_KEY` for production

## Example .env File

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=virtual_tryon_db
DB_USER=root
DB_PASSWORD=MySecurePassword123

# Flask
FLASK_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# GPU Server
GPU_SERVER_IP=172.28.80.80
GPU_SERVER_PORT=9999

# Session
SESSION_LIFETIME_DAYS=7
```

## Troubleshooting

### "Module 'dotenv' not found"
Install python-dotenv:
```bash
pip install python-dotenv
```

### "Database connection failed"
1. Check `DB_PASSWORD` is correct
2. Verify MySQL is running
3. Ensure database `virtual_tryon_db` exists
4. Test connection with MySQL Workbench

### "Secret key not set"
Make sure you have:
1. Created `.env` file from `.env.example`
2. Set `FLASK_SECRET_KEY` to a random value
3. Restarted the application

## Production Deployment

For production:
1. Use strong, unique passwords
2. Generate a secure random `FLASK_SECRET_KEY`
3. Set `FLASK_DEBUG=False`
4. Use environment-specific `.env` files
5. Consider using a secrets manager for sensitive data
6. Enable HTTPS/SSL
7. Use a production-grade database server
