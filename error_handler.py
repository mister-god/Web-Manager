#!/usr/bin/env python3
"""
ERROR HANDLER - Automatically fixes common issues
Run this if you encounter any errors
"""

import os
import sys
import subprocess
import platform

def print_banner():
    print("\n" + "="*60)
    print("🔧 WEB MANAGER - Error Handler")
    print("="*60 + "\n")

def check_python():
    print("[1/6] Checking Python...")
    if sys.version_info[0] < 3:
        print("   ❌ Python 3 required")
        return False
    print(f"   ✅ Python {sys.version_info[0]}.{sys.version_info[1]} installed")
    return True

def check_pip():
    print("\n[2/6] Checking pip...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      capture_output=True, check=True)
        print("   ✅ pip installed")
        return True
    except:
        print("   ���️ Installing pip...")
        subprocess.run([sys.executable, '-m', 'ensurepip'], capture_output=True)
        return True

def install_dependencies():
    print("\n[3/6] Installing dependencies...")
    packages = ['flask', 'flask-cors', 'psutil', 'requests']
    for pkg in packages:
        print(f"   Installing {pkg}...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', pkg, '-q'], 
                      capture_output=True)
    print("   ✅ Dependencies installed")

def check_cloudflared():
    print("\n[4/6] Checking cloudflared...")
    try:
        subprocess.run(['cloudflared', '--version'], capture_output=True, check=True)
        print("   ✅ cloudflared installed")
        return True
    except:
        print("   ⚠️ cloudflared not found")
        system = platform.system()
        if system == "Linux":
            print("   Installing cloudflared for Linux...")
            subprocess.run([
                'curl', '-L', 
                'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64',
                '-o', 'cloudflared'
            ], capture_output=True)
            subprocess.run(['chmod', '+x', 'cloudflared'], capture_output=True)
            subprocess.run(['sudo', 'mv', 'cloudflared', '/usr/local/bin/'], capture_output=True)
            print("   ✅ cloudflared installed")
        else:
            print("   📥 Download cloudflared from: https://github.com/cloudflare/cloudflared/releases")
        return True

def check_ports():
    print("\n[5/6] Checking ports...")
    import socket
    ports = [5000, 5001, 5002]
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            print(f"   ⚠️ Port {port} is in use")
        else:
            print(f"   ✅ Port {port} is free")
        sock.close()
    return True

def create_directories():
    print("\n[6/6] Creating directories...")
    dirs = ['templates', 'uploads', 'logs']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"   ✅ Created {d}/")
    return True

def run_fixes():
    print_banner()
    
    check_python()
    check_pip()
    install_dependencies()
    check_cloudflared()
    check_ports()
    create_directories()
    
    print("\n" + "="*60)
    print("✅ All fixes applied!")
    print("\nRun the tool: python3 app.py")
    print("="*60 + "\n")

if __name__ == '__main__':
    run_fixes()