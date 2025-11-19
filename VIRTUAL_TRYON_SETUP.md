# Virtual Try-On Setup Guide

## Architecture

```
[Your Browser] 
    ↓ WebSocket (port 8765)
[ecommerce_app.py - Flask + WebSocket Server] (Windows/Local)
    ↓ TCP Socket (port 9999)
[network_rtv_server.py - GPU Backend] (AWS/Linux)
    ↓ 
[RTV Model + 6 Trained Garments]
```

## Step 1: Run Backend on AWS

SSH into your AWS server and run:

```bash
cd /path/to/v-try-on-FP2
python network_rtv_server.py
```

You should see:
```
Starting Real-Time Network RTV Server...
Initializing RTV FrameProcessor...
✓ RTV FrameProcessor initialized
Loading first garment to GPU...
✓ Garment 0 loaded
Ready for connections!
🚀 Real-Time RTV Server started on port 9999
Waiting for webcam connection...
```

## Step 2: Configure Firewall (AWS Security Group)

1. Go to AWS EC2 Console
2. Select your instance
3. Click "Security Groups"
4. Add Inbound Rule:
   - Type: Custom TCP
   - Port: 9999
   - Source: Your IP address (or 0.0.0.0/0 for testing)

## Step 3: Update .env File

Edit your `.env` file:

```env
# GPU Server Configuration
GPU_SERVER_IP=<YOUR_AWS_PUBLIC_IP>  # e.g., 54.123.45.67
GPU_SERVER_PORT=9999
```

Get your AWS public IP:
```bash
curl http://checkip.amazonaws.com
```

## Step 4: Test Connection

Run the connection test:

```powershell
python test_gpu_connection.py
```

If successful, you'll see:
```
✓ SUCCESS! Connected to GPU server
✓ Server is running at <IP>:9999
```

## Step 5: Run E-Commerce App

```powershell
python ecommerce_app.py
```

You should see:
```
✓ All database tables created successfully
✓ Database connection pool created successfully
✓ WebSocket server started on ws://0.0.0.0:8765
✓ Flask server starting on http://0.0.0.0:5000
```

## Step 6: Try Virtual Try-On

1. Open browser: http://localhost:5000
2. Register/Login
3. Go to Shop
4. Click any product
5. Click "Virtual Try-On" button
6. Allow webcam access
7. Click "Start Try-On"

## Troubleshooting

### Connection Refused
- Make sure `network_rtv_server.py` is running on AWS
- Check AWS Security Group allows port 9999

### Timeout
- Verify AWS public IP is correct in `.env`
- Check network connectivity
- Ping the AWS server

### No Video Feed
- Check webcam permissions in browser
- Look at browser console (F12) for errors
- Check terminal logs for WebSocket errors

### Garment Not Loading
- Backend must have the 6 trained models:
  - jin_17_vmsdp2ta
  - jin_18_vmsdp2ta
  - jin_22_vmsdp2ta
  - lab_03_vmsdp2ta
  - lab_04_vmsdp2ta
  - lab_07_vmsdp2ta
- Check `rtv_ckpts` folder exists on AWS

## Port Summary

- **5000**: Flask web server (HTTP)
- **8765**: WebSocket server (local)
- **9999**: GPU backend server (AWS)

## Files

- `ecommerce_app.py`: Main Flask + WebSocket server (runs on Windows)
- `network_rtv_server.py`: GPU backend (runs on AWS)
- `test_gpu_connection.py`: Connection test utility
- `.env`: Configuration file

## Backend Requirements (AWS)

The AWS server must have:
- Python 3.8+
- PyTorch
- OpenCV
- RTV model files in `/home/test/Desktop/LLM/RTV/rtv_ckpts/`
- 6 trained garment models

## Frontend (Browser)

Supported browsers:
- Chrome (recommended)
- Firefox
- Edge

Requires:
- Webcam access permission
- WebSocket support (all modern browsers)
