"""
Test GPU Server Connection
Quick utility to test if the network_rtv_server.py is reachable on AWS
"""
import socket
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GPU server configuration
GPU_SERVER_IP = os.getenv('GPU_SERVER_IP', '172.28.80.80')
GPU_SERVER_PORT = int(os.getenv('GPU_SERVER_PORT', 9999))

def test_connection():
    """Test connection to GPU server"""
    print("=" * 60)
    print("GPU SERVER CONNECTION TEST")
    print("=" * 60)
    print(f"Testing connection to: {GPU_SERVER_IP}:{GPU_SERVER_PORT}")
    print("-" * 60)
    
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        
        # Try to connect
        print("Attempting connection...")
        sock.connect((GPU_SERVER_IP, GPU_SERVER_PORT))
        
        print("✓ SUCCESS! Connected to GPU server")
        print(f"✓ Server is running at {GPU_SERVER_IP}:{GPU_SERVER_PORT}")
        
        sock.close()
        print("\nYour virtual try-on should work now!")
        print("Run: python ecommerce_app.py")
        return True
        
    except socket.timeout:
        print("✗ TIMEOUT - Server did not respond within 5 seconds")
        print("\nPossible issues:")
        print("1. network_rtv_server.py is not running on AWS")
        print("2. Firewall is blocking port 9999")
        print("3. Wrong IP address in .env file")
        return False
        
    except ConnectionRefusedError:
        print("✗ CONNECTION REFUSED - Server is not listening")
        print("\nPossible issues:")
        print("1. network_rtv_server.py is not running on AWS")
        print("2. Server is running on a different port")
        return False
        
    except socket.gaierror:
        print("✗ DNS ERROR - Cannot resolve hostname")
        print(f"\nCheck if '{GPU_SERVER_IP}' is the correct address")
        return False
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    
    finally:
        print("=" * 60)

def show_setup_instructions():
    """Show setup instructions"""
    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS")
    print("=" * 60)
    print("\n1. ON AWS SERVER:")
    print("   Run the RTV backend server:")
    print("   $ cd /path/to/v-try-on-FP2")
    print("   $ python network_rtv_server.py")
    print("")
    print("2. IN YOUR .env FILE:")
    print(f"   GPU_SERVER_IP={GPU_SERVER_IP}")
    print(f"   GPU_SERVER_PORT={GPU_SERVER_PORT}")
    print("")
    print("3. FIREWALL:")
    print("   Make sure port 9999 is open on AWS:")
    print("   - Check AWS Security Group rules")
    print("   - Allow inbound TCP traffic on port 9999")
    print("")
    print("4. TEST CONNECTION:")
    print("   $ python test_gpu_connection.py")
    print("=" * 60)

if __name__ == "__main__":
    success = test_connection()
    
    if not success:
        show_setup_instructions()
