from flask import Flask, render_template, Response, jsonify, request
from flask_socketio import SocketIO, emit
import cv2
import base64
import numpy as np
import socket
import pickle
import struct
import threading
import time
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rtv_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

class RTVWebInterface:
    def __init__(self, gpu_server_ip, gpu_server_port=9999):
        self.gpu_server_ip = gpu_server_ip
        self.gpu_server_port = gpu_server_port
        self.socket = None
        self.connected = False
        self.current_garment = 0
        self.fps = 0
        
        # Load available garments from assets
        self.garments = self.load_garments()
        
    def load_garments(self):
        """Load available garment images - same as network_rtv_server.py"""
        garment_dir = './assets/garment_images'
        garments = []
        
        # Use the SAME garment list as network_rtv_server.py
        garment_base_list = ['lab_03','lab_04','lab_07','jin_17','jin_18','jin_22']
        
        for i, garment_base in enumerate(garment_base_list):
            # Match the naming convention
            model_name = garment_base + '_vmsdp2ta'
            img_file = garment_base + '_white_bg.jpg'
            img_path = os.path.join(garment_dir, img_file)
            
            if os.path.exists(img_path):
                # Generate display name
                parts = garment_base.split('_')
                if parts[0] == 'lab':
                    display_name = f'Lab Coat {parts[1]}'
                elif parts[0] == 'jin':
                    display_name = f'Jacket {parts[1]}'
                else:
                    display_name = garment_base.replace('_', ' ').title()
                
                garments.append({
                    'id': i,  # Use index as ID to match server
                    'image': img_file,
                    'model': model_name,
                    'name': display_name
                })
            else:
                print(f"Warning: Garment image not found: {img_path}")
        
        return garments
    
    def connect_to_gpu_server(self):
        """Connect to the GPU processing server"""
        try:
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout
            self.socket.connect((self.gpu_server_ip, self.gpu_server_port))
            self.connected = True
            print(f"✓ Connected to GPU server at {self.gpu_server_ip}:{self.gpu_server_port}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            self.connected = False
            return False
    
    def send_frame(self, frame):
        """Send frame to GPU server for processing"""
        try:
            if not self.connected:
                if not self.connect_to_gpu_server():
                    return None
            
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            data = buffer.tobytes()
            size = len(data)
            
            try:
                self.socket.sendall(struct.pack("Q", size))
                self.socket.sendall(data)
                
                # Receive processed frame
                return self.receive_frame()
            except (socket.error, ConnectionResetError, BrokenPipeError) as e:
                print(f"Connection lost, reconnecting... {e}")
                self.connected = False
                self.socket.close()
                return None
        except Exception as e:
            print(f"Error sending frame: {e}")
            return None
    
    def receive_frame(self):
        """Receive processed frame from GPU server"""
        try:
            size_data = self.socket.recv(8)
            if not size_data or len(size_data) < 8:
                return None
            size = struct.unpack("Q", size_data)[0]
            
            data = b''
            while len(data) < size:
                packet = self.socket.recv(min(4096, size - len(data)))
                if not packet:
                    return None
                data += packet
            
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except:
            return None
    
    def change_garment(self, garment_id):
        """Send garment change command to GPU server"""
        try:
            command = {'type': 'change_garment', 'id': garment_id}
            data = pickle.dumps(command)
            size = len(data)
            self.socket.sendall(struct.pack("Q", size | (1 << 63)))
            self.socket.sendall(data)
            self.current_garment = garment_id
            return True
        except Exception as e:
            print(f"Error changing garment: {e}")
            return False

# Global instance
rtv_interface = RTVWebInterface("172.28.80.80")

@app.route('/')
def index():
    return render_template('index.html', garments=rtv_interface.garments)

@app.route('/api/garments')
def get_garments():
    return jsonify(rtv_interface.garments)

@app.route('/api/change_garment/<int:garment_id>')
def change_garment(garment_id):
    success = rtv_interface.change_garment(garment_id)
    return jsonify({'success': success, 'garment_id': garment_id})

@socketio.on('connect')
def handle_connect():
    print('Client connected to web interface')
    # Don't connect to GPU server here, wait for first frame

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from web interface')
    if rtv_interface.connected:
        try:
            rtv_interface.socket.close()
        except:
            pass
        rtv_interface.connected = False

@socketio.on('video_frame')
def handle_video_frame(data):
    try:
        # Decode base64 image
        img_data = base64.b64decode(data.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            print("Failed to decode frame")
            return
        
        # Process with RTV
        processed_frame = rtv_interface.send_frame(frame)
        
        if processed_frame is not None:
            # Encode back to base64
            _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            emit('processed_frame', {'image': f'data:image/jpeg;base64,{img_base64}'})
    except Exception as e:
        print(f"Error processing frame: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("Starting RTV Web Interface...")
    print("Open http://localhost:5000 in your browser")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
