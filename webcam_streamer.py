import cv2
import socket
import pickle
import struct
import threading
import time
import numpy as np

class RealTimeWebcamStreamer:
    def __init__(self, server_ip, port=9999):
        self.server_ip = server_ip
        self.port = port
        self.cap = cv2.VideoCapture(0)
        
        # Optimize camera settings for real-time performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for lower latency
        
        self.socket = None
        self.connected = False
        
        # Garment info
        self.garment_names = [
            'Lab Coat 03',
            'Lab Coat 04',
            'Lab Coat 07',
            'Jacket 17',
            'Jacket 18',
            'Jacket 22'
        ]
        self.current_garment = 0
        self.fps = 0
        
    def send_garment_change(self, garment_id):
        """Send garment change command to server"""
        try:
            # Send special command (negative size indicates command)
            command = {'type': 'change_garment', 'id': garment_id}
            data = pickle.dumps(command)
            size = len(data)
            self.socket.sendall(struct.pack("Q", size | (1 << 63)))  # Set high bit for command
            self.socket.sendall(data)
            self.current_garment = garment_id
            print(f"Switched to garment: {self.garment_names[garment_id]}")
        except Exception as e:
            print(f"Error sending garment change: {e}")
    
    def draw_ui(self, frame):
        """Draw clean, professional UI overlay on frame"""
        h, w = frame.shape[:2]
        overlay = frame.copy()
        
        # ===== CLEAN TOP BAR =====
        # Slim dark top bar
        cv2.rectangle(overlay, (0, 0), (w, 60), (30, 30, 30), -1)
        frame = cv2.addWeighted(overlay, 0.75, frame, 0.25, 0)
        
        # Title - clean and simple
        cv2.putText(frame, 'Virtual Try-On Studio', (30, 38), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # LIVE indicator
        cv2.circle(frame, (w - 120, 30), 6, (46, 204, 113), -1)
        cv2.putText(frame, 'LIVE', (w - 105, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (46, 204, 113), 2)
        
        # FPS
        cv2.putText(frame, f'{self.fps:.0f} FPS', (w - 180, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # ===== BOTTOM CONTROL PANEL =====
        panel_height = 120
        panel_y = h - panel_height
        
        # Dark semi-transparent background
        cv2.rectangle(overlay, (0, panel_y), (w, h), (20, 20, 20), -1)
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)
        
        # Accent line
        cv2.rectangle(frame, (0, panel_y), (w, panel_y + 2), (66, 135, 245), -1)
        
        # Current selection info
        current_text = f'CURRENT: {self.garment_names[self.current_garment].upper()}'
        cv2.putText(frame, current_text, (30, panel_y + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (66, 135, 245), 2)
        
        # Garment selection buttons - modern cards
        card_spacing = 15
        card_width = (w - (card_spacing * 8)) // 6
        card_height = 60
        card_y = panel_y + 45
        
        for i, name in enumerate(self.garment_names):
            x = card_spacing + i * (card_width + card_spacing)
            
            if i == self.current_garment:
                # Active - bright blue
                cv2.rectangle(frame, (x, card_y), 
                            (x + card_width, card_y + card_height), 
                            (66, 135, 245), -1)
                cv2.rectangle(frame, (x, card_y), 
                            (x + card_width, card_y + card_height), 
                            (100, 165, 255), 3)
                text_color = (255, 255, 255)
                num_bg = (255, 255, 255)
                num_text = (66, 135, 245)
            else:
                # Inactive - dark gray
                cv2.rectangle(frame, (x, card_y), 
                            (x + card_width, card_y + card_height), 
                            (50, 50, 50), -1)
                cv2.rectangle(frame, (x, card_y), 
                            (x + card_width, card_y + card_height), 
                            (80, 80, 80), 2)
                text_color = (180, 180, 180)
                num_bg = (80, 80, 80)
                num_text = (180, 180, 180)
            
            # Number circle
            cv2.circle(frame, (x + 20, card_y + 20), 14, num_bg, -1)
            cv2.putText(frame, str(i + 1), (x + 14, card_y + 26), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, num_text, 2)
            
            # Garment name
            parts = name.split()
            y_offset = card_y + 25 if len(parts) == 1 else card_y + 18
            
            for idx, part in enumerate(parts[:2]):  # Max 2 lines
                text_size = cv2.getTextSize(part, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
                text_x = x + (card_width - text_size[0]) // 2
                cv2.putText(frame, part, (text_x, y_offset + idx * 18), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)
        
        # Instructions - bottom right
        cv2.putText(frame, 'Press 1-6 to change | ESC to exit', 
                   (w - 320, h - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
        
        return frame
    
    def connect_to_server(self):
        """Connect to the Linux GPU server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.port))
            self.connected = True
            print(f"✓ Connected to RTV server at {self.server_ip}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def stream_frames(self):
        """Stream frames in real-time"""
        if not self.connect_to_server():
            return
        
        # Create fullscreen window
        cv2.namedWindow('Virtual Try-On Studio', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Virtual Try-On Studio', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to capture frame")
                    break
                
                # Encode frame as JPEG to avoid NumPy pickle issues
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                data = buffer.tobytes()
                size = len(data)
                
                # Send frame size first (8 bytes for Q format), then frame data
                try:
                    self.socket.sendall(struct.pack("Q", size))
                    self.socket.sendall(data)
                    
                    # Receive processed frame back
                    processed_frame = self.receive_processed_frame()
                    
                    if processed_frame is not None:
                        # Add UI overlay
                        processed_frame = self.draw_ui(processed_frame)
                        
                        # Display the result locally
                        cv2.imshow('Virtual Try-On Studio', processed_frame)
                        
                        # Calculate and display FPS
                        frame_count += 1
                        if frame_count % 30 == 0:
                            elapsed = time.time() - start_time
                            self.fps = frame_count / elapsed
                    
                    # Handle keyboard input
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:  # q or ESC
                        break
                    elif key >= ord('1') and key <= ord('6'):
                        garment_id = key - ord('1')
                        if garment_id < len(self.garment_names):
                            self.send_garment_change(garment_id)
                        
                except socket.error as e:
                    print(f"Socket error: {e}")
                    break
                    
        except KeyboardInterrupt:
            print("Stopping stream...")
        finally:
            self.cleanup()
    
    def receive_processed_frame(self):
        """Receive processed frame from server"""
        try:
            # Receive size (8 bytes for Q format)
            size_data = self.socket.recv(8)
            if not size_data or len(size_data) < 8:
                return None
            size = struct.unpack("Q", size_data)[0]
            
            # Receive frame data
            data = b''
            while len(data) < size:
                packet = self.socket.recv(min(4096, size - len(data)))
                if not packet:
                    return None
                data += packet
            
            # Decode JPEG image
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            print(f"Error receiving frame: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources"""
        self.cap.release()
        cv2.destroyAllWindows()
        if self.socket:
            self.socket.close()
        print("Cleanup completed")

if __name__ == "__main__":
    # Replace with your Linux machine IP
    LINUX_GPU_IP = "172.28.80.80"  # Your Linux GPU machine IP
    
    streamer = RealTimeWebcamStreamer(LINUX_GPU_IP)
    print("Starting real-time webcam streaming to RTV...")
    print("Press 'q' in the video window to stop")
    streamer.stream_frames()