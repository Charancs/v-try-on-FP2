import asyncio
import websockets
import socket
import struct
import cv2
import numpy as np
import json
import pickle
from flask import Flask, render_template, send_from_directory
import threading
import base64
import os
import glob

app = Flask(__name__)

# GPU server connection
GPU_SERVER_IP = "172.28.80.80"
GPU_SERVER_PORT = 9999

# Store active websocket clients
clients = set()

# Only show garments with trained models
def get_available_garments():
    """Get only the 6 garments that have trained models on the backend"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    garment_dir = os.path.join(base_dir, 'assets', 'garment_images')
    
    # Only these 6 garments have trained models: jin_17, jin_18, jin_22, lab_03, lab_04, lab_07
    available_garments = [
        {'name': 'Jacket 17', 'image': 'jin_17_white_bg.jpg'},
        {'name': 'Jacket 18', 'image': 'jin_18_white_bg.jpg'},
        {'name': 'Jacket 22', 'image': 'jin_22_white_bg.jpg'},
        {'name': 'Lab Coat 03', 'image': 'lab_03_white_bg.jpg'},
        {'name': 'Lab Coat 04', 'image': 'lab_04_white_bg.jpg'},
        {'name': 'Lab Coat 07', 'image': 'lab_07_white_bg.jpg'},
    ]
    
    return available_garments

GARMENTS = get_available_garments()

current_garment = 0

class GPUServerConnection:
    def __init__(self):
        self.socket = None
        self.connected = False
    
    def connect(self):
        """Connect to GPU server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((GPU_SERVER_IP, GPU_SERVER_PORT))
            self.connected = True
            print(f"✓ Connected to GPU server at {GPU_SERVER_IP}:{GPU_SERVER_PORT}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to GPU server: {e}")
            return False
    
    def send_frame(self, frame_data):
        """Send JPEG frame to GPU server"""
        try:
            size = len(frame_data)
            self.socket.sendall(struct.pack("Q", size))
            self.socket.sendall(frame_data)
            return True
        except Exception as e:
            print(f"Error sending frame: {e}")
            return False
    
    def receive_frame(self):
        """Receive processed frame from GPU server"""
        try:
            # Receive size (8 bytes)
            size_data = self.socket.recv(8)
            if not size_data or len(size_data) < 8:
                return None
            
            size = struct.unpack("Q", size_data)[0]
            
            # Check if it's a command response (high bit set)
            if size & (1 << 63):
                # It's a command acknowledgment, wait for actual frame
                return self.receive_frame()
            
            # Receive frame data
            data = b''
            while len(data) < size:
                packet = self.socket.recv(min(4096, size - len(data)))
                if not packet:
                    return None
                data += packet
            
            return data
        except Exception as e:
            print(f"Error receiving frame: {e}")
            return None
    
    def send_garment_change(self, garment_id):
        """Send garment change command"""
        try:
            # Send command as pickle data (like webcam_streamer.py)
            command = {'type': 'change_garment', 'id': garment_id}
            data = pickle.dumps(command)
            size = len(data)
            # Send command with high bit set
            self.socket.sendall(struct.pack("Q", size | (1 << 63)))
            self.socket.sendall(data)
            print(f"✓ Sent garment change command: {garment_id}")
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
        self.connected = False

# Global GPU connection
gpu_conn = GPUServerConnection()

@app.route('/')
def index():
    """Serve main page"""
    return render_template('rtv_simple.html', garments=GARMENTS)

@app.route('/static/garments/<filename>')
def serve_garment_image(filename):
    """Serve garment images from assets folder"""
    import os
    # Get the absolute path to assets/garment_images
    base_dir = os.path.dirname(os.path.abspath(__file__))
    garment_dir = os.path.join(base_dir, 'assets', 'garment_images')
    return send_from_directory(garment_dir, filename)

async def handle_websocket(websocket):
    """Handle WebSocket connection from browser"""
    clients.add(websocket)
    print(f"✓ New client connected. Total clients: {len(clients)}")
    
    # Create dedicated GPU connection for this client
    client_gpu = GPUServerConnection()
    
    try:
        # Connect to GPU server
        print("Attempting to connect to GPU server...")
        if not client_gpu.connect():
            print("✗ Failed to connect to GPU server")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Failed to connect to GPU server'
            }))
            return
        
        print("✓ Client connected to GPU server, ready to process frames")
        
        frame_count = 0
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'frame':
                    frame_count += 1
                    if frame_count % 100 == 0:
                        print(f"📹 Processed {frame_count} frames...")
                    
                    # Receive base64 encoded frame from browser
                    frame_b64 = data.get('data')
                    if not frame_b64:
                        continue
                    
                    # Decode base64 to JPEG bytes
                    try:
                        frame_data = base64.b64decode(frame_b64.split(',')[1])
                    except Exception as e:
                        print(f"✗ Error decoding frame: {e}")
                        continue
                    
                    # Send to GPU server
                    if client_gpu.send_frame(frame_data):
                        # Receive processed frame
                        processed_data = client_gpu.receive_frame()
                        
                        if processed_data:
                            # Send back to browser as base64
                            processed_b64 = base64.b64encode(processed_data).decode('utf-8')
                            await websocket.send(json.dumps({
                                'type': 'frame',
                                'data': f'data:image/jpeg;base64,{processed_b64}'
                            }))
                        else:
                            print("⚠ No processed frame received from GPU server")
                    else:
                        print("⚠ Failed to send frame to GPU server")
                
                elif msg_type == 'garment_change':
                    garment_id = data.get('garment_id')
                    print(f"🎨 Changing garment to: {garment_id}")
                    if 0 <= garment_id < len(GARMENTS):
                        if client_gpu.send_garment_change(garment_id):
                            await websocket.send(json.dumps({
                                'type': 'garment_changed',
                                'garment_id': garment_id
                            }))
                
            except json.JSONDecodeError as e:
                print(f"✗ JSON decode error: {e}")
            except Exception as e:
                print(f"✗ Error processing message: {e}")
                import traceback
                traceback.print_exc()
                try:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))
                except:
                    pass
    
    except websockets.exceptions.ConnectionClosed:
        print("✗ Client WebSocket disconnected")
    except Exception as e:
        print(f"✗ WebSocket handler error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client_gpu.close()
        clients.remove(websocket)
        print(f"✓ Client cleanup complete. Total clients: {len(clients)}")

async def start_websocket_server():
    """Start WebSocket server"""
    async with websockets.serve(handle_websocket, "0.0.0.0", 8765):
        print("✓ WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

def run_websocket_server():
    """Run WebSocket server in event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(start_websocket_server())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

def run_flask_app():
    """Run Flask app"""
    print("✓ Flask server starting on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    # Start WebSocket server in separate thread
    ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
    ws_thread.start()
    
    # Run Flask app in main thread
    run_flask_app()
