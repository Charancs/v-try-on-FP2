import sys
import os
import cv2
import socket
import pickle
import struct
import threading
import time
import numpy as np

# Import RTV modules
from util.image_warp import crop2_169, resize_img
from VITON.viton_upperbody import FrameProcessor

class NetworkRTVServer:
    def __init__(self, garment_id_list, port=9999):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Initialize RTV FrameProcessor (same as in rtl_demo.py)
        print("Initializing RTV FrameProcessor...")
        # Set the correct checkpoint directory path
        ckpt_dir = "/home/test/Desktop/LLM/RTV/rtv_ckpts"  # Linux path where checkpoints are located
        self.frame_processor = FrameProcessor(garment_id_list, ckpt_dir=ckpt_dir)
        print("✓ RTV FrameProcessor initialized")
        
        # Load the first garment to GPU
        print("Loading first garment to GPU...")
        self.current_garment_id = 0
        self.frame_processor.set_target_garment(self.current_garment_id)
        print(f"✓ Garment {self.current_garment_id} loaded")
        
        # Wait a moment for the model to fully load
        time.sleep(3)
        print("Ready for connections!")
        
    def set_garment_id(self, garment_id):
        """Change the current garment"""
        self.current_garment_id = garment_id
        self.frame_processor.set_target_garment(garment_id)
        print(f"Switched to garment ID: {garment_id}")
    
    def process_frame_realtime(self, frame):
        """Process frame with RTV (exactly like rtl_demo.py)"""
        try:
            # Apply same preprocessing as rtl_demo.py
            frame = cv2.flip(frame, 1)  # Mirror the image
            frame = resize_img(frame, max_height=1024)
            frame = crop2_169(frame)
            
            # Process with RTV
            processed_frame = self.frame_processor(frame)
            
            return processed_frame
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame
    
    def start_server(self):
        """Start the real-time RTV server"""
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen(1)
        
        print(f"🚀 Real-Time RTV Server started on port {self.port}")
        print("Waiting for webcam connection...")
        
        while True:
            try:
                client_socket, addr = self.socket.accept()
                print(f"✓ Webcam connected from {addr}")
                
                # Handle client in real-time
                self.handle_realtime_client(client_socket, addr)
                
            except KeyboardInterrupt:
                print("Server shutting down...")
                break
            except Exception as e:
                print(f"Server error: {e}")
                
    def handle_realtime_client(self, client_socket, addr):
        """Handle real-time client connection"""
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                # Receive frame
                frame = self.receive_frame(client_socket)
                if frame is None:
                    print("Lost connection to webcam")
                    break
                
                # Skip processing if it was a command
                if isinstance(frame, str) and frame == 'COMMAND':
                    continue
                
                # Process with RTV in real-time
                processed_frame = self.process_frame_realtime(frame)
                
                # Send processed frame back
                self.send_frame(client_socket, processed_frame)
                
                # Performance monitoring
                frame_count += 1
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    # Get garment name dynamically
                    garment_names = [
                        'Jacket 17', 'Jacket 18', 'Jacket 22',
                        'Lab Coat 03', 'Lab Coat 04', 'Lab Coat 07'
                    ]
                    garment_name = garment_names[self.current_garment_id] if self.current_garment_id < len(garment_names) else f"Garment {self.current_garment_id}"
                    print(f"Server FPS: {fps:.2f} | Garment: {garment_name}")
                    
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            client_socket.close()
            print(f"✗ Disconnected from {addr}")
    
    def receive_frame(self, client_socket):
        """Receive frame or command from client"""
        try:
            # Receive frame size (8 bytes for Q format)
            size_data = client_socket.recv(8)
            if not size_data or len(size_data) < 8:
                return None
            size = struct.unpack("Q", size_data)[0]
            
            # Check if this is a command (high bit set)
            is_command = (size & (1 << 63)) != 0
            size = size & ~(1 << 63)  # Clear high bit
            
            # Receive data
            data = b''
            while len(data) < size:
                packet = client_socket.recv(min(4096, size - len(data)))
                if not packet:
                    return None
                data += packet
            
            if is_command:
                # Handle command
                command = pickle.loads(data)
                if command['type'] == 'change_garment':
                    garment_id = command['id']
                    print(f"Switching to garment {garment_id}...")
                    self.set_garment_id(garment_id)
                return 'COMMAND'  # Special marker
            else:
                # Decode JPEG image
                nparr = np.frombuffer(data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return frame
        except Exception as e:
            print(f"Error receiving frame: {e}")
            return None
    
    def send_frame(self, client_socket, frame):
        """Send processed frame to client"""
        try:
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            data = buffer.tobytes()
            size = len(data)
            client_socket.sendall(struct.pack("Q", size))
            client_socket.sendall(data)
        except Exception as e:
            print(f"Error sending frame: {e}")
    
    def cleanup(self):
        """Clean up server resources"""
        self.socket.close()

def main():
    print("Starting Real-Time Network RTV Server...")
    
    # Only garments with trained models available in rtv_ckpts folder
    garment_name_list = [
        'jin_17', 'jin_18', 'jin_22',
        'lab_03', 'lab_04', 'lab_07'
    ]
    
    # Add the suffix as done in rtl_demo.py
    for i in range(len(garment_name_list)):
        garment_name_list[i] = garment_name_list[i] + '_vmsdp2ta'
    
    print(f"Available garments: {garment_name_list}")
    print(f"Total garments: {len(garment_name_list)}")
    
    server = NetworkRTVServer(garment_name_list)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        server.cleanup()

if __name__ == "__main__":
    main()