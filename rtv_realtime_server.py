import cv2
import socket
import pickle
import struct
import threading
import time
import sys
import os
import numpy as np

# Add RTV to Python path
sys.path.append('.')

class RealTimeRTVServer:
    def __init__(self, port=9999):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Initialize RTV components
        self.rtv_initialized = False
        self.setup_rtv()
        
    def setup_rtv(self):
        """Initialize RTV components - copy from demo.py"""
        try:
            print("Initializing RTV components...")
            
            # Import all necessary RTV modules
            from SMPL.smpl_np import SMPLModel
            from util import util
            from OffscreenRenderer.off_screen_render import OffscreenRenderer
            
            # Initialize SMPL
            self.smpl = SMPLModel(
                device='cuda',
                model_path='assets/smpl/full_body.npz',
                simplify=True
            )
            
            # Initialize renderer
            self.renderer = OffscreenRenderer()
            
            # Add other RTV initialization from demo.py here
            # You'll need to copy the initialization code from the original demo.py
            
            self.rtv_initialized = True
            print("✓ RTV initialized successfully")
            
        except Exception as e:
            print(f"✗ RTV initialization failed: {e}")
            print("Please ensure all RTV dependencies are installed")
            self.rtv_initialized = False
    
    def process_frame_with_rtv(self, frame):
        """Process frame with RTV - integrate actual RTV processing"""
        if not self.rtv_initialized:
            # Return original frame if RTV not initialized
            return frame
        
        try:
            # This is where you integrate the actual RTV processing
            # Copy the main processing loop from demo.py
            
            # For now, return a placeholder (you need to add actual RTV code)
            # Example processing:
            processed_frame = frame.copy()
            
            # Add text overlay to show it's being processed
            cv2.putText(processed_frame, 
                       f"RTV Processing - {time.strftime('%H:%M:%S')}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            return processed_frame
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame
    
    def start_server(self):
        """Start the real-time RTV server"""
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen(1)
        
        print(f"🚀 RTV Real-Time Server started on port {self.port}")
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
                
                # Process with RTV in real-time
                processed_frame = self.process_frame_with_rtv(frame)
                
                # Send processed frame back
                self.send_frame(client_socket, processed_frame)
                
                # Performance monitoring
                frame_count += 1
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"Server processing FPS: {fps:.2f}")
                    
        except Exception as e:
            print(f"Client handling error: {e}")
        finally:
            client_socket.close()
            print(f"✗ Disconnected from {addr}")
    
    def receive_frame(self, client_socket):
        """Receive frame from client"""
        try:
            # Receive frame size
            size_data = client_socket.recv(4)
            if not size_data:
                return None
            size = struct.unpack("L", size_data)[0]
            
            # Receive frame data
            data = b''
            while len(data) < size:
                packet = client_socket.recv(size - len(data))
                if not packet:
                    return None
                data += packet
            
            return pickle.loads(data)
        except:
            return None
    
    def send_frame(self, client_socket, frame):
        """Send processed frame to client"""
        try:
            data = pickle.dumps(frame)
            size = len(data)
            client_socket.sendall(struct.pack("L", size))
            client_socket.sendall(data)
        except Exception as e:
            print(f"Error sending frame: {e}")
    
    def cleanup(self):
        """Clean up server resources"""
        self.socket.close()

if __name__ == "__main__":
    print("Starting Real-Time RTV Server...")
    print("Make sure RTV is properly installed and models are downloaded")
    
    server = RealTimeRTVServer()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        server.cleanup()