"""
Show Current Configuration
Display all settings from .env file
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def show_config():
    """Display current configuration"""
    print("=" * 70)
    print("CURRENT CONFIGURATION")
    print("=" * 70)
    
    print("\n📊 DATABASE CONFIGURATION")
    print("-" * 70)
    print(f"Host:     {os.getenv('DB_HOST', 'localhost')}")
    print(f"Port:     {os.getenv('DB_PORT', '3306')}")
    print(f"Database: {os.getenv('DB_NAME', 'virtual_tryon_db')}")
    print(f"User:     {os.getenv('DB_USER', 'root')}")
    db_password = os.getenv('DB_PASSWORD', '')
    if db_password:
        print(f"Password: {'*' * len(db_password)} (set)")
    else:
        print(f"Password: (NOT SET - ⚠️ WARNING)")
    
    print("\n🚀 FLASK CONFIGURATION")
    print("-" * 70)
    print(f"Host:           {os.getenv('FLASK_HOST', '0.0.0.0')}")
    print(f"Port:           {os.getenv('FLASK_PORT', '5000')}")
    print(f"Debug:          {os.getenv('FLASK_DEBUG', 'False')}")
    flask_secret = os.getenv('FLASK_SECRET_KEY', '')
    if flask_secret and flask_secret != 'your_secret_key_here_change_in_production':
        print(f"Secret Key:     {'*' * 20} (set)")
    else:
        print(f"Secret Key:     (NOT SET or DEFAULT - ⚠️ WARNING)")
    print(f"Session Days:   {os.getenv('SESSION_LIFETIME_DAYS', '7')}")
    
    print("\n🖥️ GPU SERVER CONFIGURATION (AWS)")
    print("-" * 70)
    gpu_ip = os.getenv('GPU_SERVER_IP', '172.28.80.80')
    gpu_port = os.getenv('GPU_SERVER_PORT', '9999')
    print(f"IP Address:     {gpu_ip}")
    print(f"Port:           {gpu_port}")
    print(f"Full Address:   {gpu_ip}:{gpu_port}")
    
    print("\n🎯 APPLICATION SETTINGS")
    print("-" * 70)
    print(f"App Name:                {os.getenv('APP_NAME', 'Virtual Try-On E-Commerce')}")
    print(f"Max Cart Items:          {os.getenv('MAX_CART_ITEMS', '20')}")
    print(f"Free Shipping Threshold: ${os.getenv('FREE_SHIPPING_THRESHOLD', '50.00')}")
    print(f"Shipping Cost:           ${os.getenv('SHIPPING_COST', '5.00')}")
    
    print("\n🔍 CONFIGURATION STATUS")
    print("-" * 70)
    
    issues = []
    
    # Check database password
    if not os.getenv('DB_PASSWORD'):
        issues.append("❌ Database password is not set")
    else:
        print("✓ Database password is set")
    
    # Check Flask secret key
    flask_secret = os.getenv('FLASK_SECRET_KEY', '')
    if not flask_secret or flask_secret == 'your_secret_key_here_change_in_production':
        issues.append("❌ Flask secret key needs to be changed")
    else:
        print("✓ Flask secret key is set")
    
    # Check GPU server
    if gpu_ip == '172.28.80.80':
        issues.append("⚠️  GPU server IP is default (verify if correct)")
    else:
        print(f"✓ GPU server IP configured: {gpu_ip}")
    
    if issues:
        print("\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print("\nEdit your .env file to fix these issues.")
    else:
        print("\n✅ All required settings are configured!")
    
    print("\n" + "=" * 70)
    print("\n📝 TO UPDATE CONFIGURATION:")
    print("   1. Edit the .env file")
    print("   2. Restart the application")
    print("   3. Run: python show_config.py")
    print("\n🧪 TO TEST GPU CONNECTION:")
    print("   Run: python test_gpu_connection.py")
    print("\n🚀 TO START APPLICATION:")
    print("   Run: python ecommerce_app.py")
    print("=" * 70)

if __name__ == "__main__":
    show_config()
