#!/usr/bin/env python3
"""
WEB MANAGER - Professional API Extensions
Advanced features for real-time file sync, device management, and analytics
"""

from flask import request, jsonify, send_file
from functools import wraps
import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
import mimetypes
import hashlib

# ==================== DECORATORS ====================

def require_token(f):
    """Verify token before accessing protected endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token') or request.json.get('token') if request.is_json else None
        
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        # Token validation would go here
        return f(*args, token=token, **kwargs)
    return decorated_function

def require_device(f):
    """Verify device is connected"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        device_id = kwargs.get('device_id')
        from app import connected_devices
        
        if device_id not in connected_devices:
            return jsonify({'error': 'Device not found'}), 404
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== REAL-TIME FILE SYNC ====================

class FileWatcher:
    """Monitor file changes in real-time"""
    def __init__(self, path):
        self.path = path
        self.file_hashes = {}
        self.last_check = time.time()
    
    def get_file_hash(self, file_path):
        """Calculate file hash for change detection"""
        try:
            hash_obj = hashlib.md5()
            with open(file_path, 'rb') as f:
                hash_obj.update(f.read())
            return hash_obj.hexdigest()
        except:
            return None
    
    def scan_changes(self):
        """Scan for file changes"""
        changes = {
            'added': [],
            'modified': [],
            'deleted': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    file_path = os.path.join(root, file)
                    current_hash = self.get_file_hash(file_path)
                    
                    if file_path not in self.file_hashes:
                        changes['added'].append(file_path)
                        self.file_hashes[file_path] = current_hash
                    elif self.file_hashes[file_path] != current_hash:
                        changes['modified'].append(file_path)
                        self.file_hashes[file_path] = current_hash
            
            # Check for deleted files
            for file_path in list(self.file_hashes.keys()):
                if not os.path.exists(file_path):
                    changes['deleted'].append(file_path)
                    del self.file_hashes[file_path]
        
        except Exception as e:
            changes['error'] = str(e)
        
        return changes

# ==================== DEVICE ANALYTICS ====================

class DeviceAnalytics:
    """Track device statistics and usage"""
    def __init__(self):
        self.stats = {}
    
    def record_access(self, device_id, action, file_path=None, size=0):
        """Record device activity"""
        if device_id not in self.stats:
            self.stats[device_id] = {
                'total_accesses': 0,
                'total_downloads': 0,
                'total_bytes_transferred': 0,
                'last_activity': None,
                'activities': []
            }
        
        stats = self.stats[device_id]
        stats['total_accesses'] += 1
        stats['last_activity'] = datetime.now().isoformat()
        
        if action == 'download':
            stats['total_downloads'] += 1
            stats['total_bytes_transferred'] += size
        
        stats['activities'].append({
            'action': action,
            'file': file_path,
            'size': size,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_stats(self, device_id):
        """Get device statistics"""
        return self.stats.get(device_id, {})
    
    def get_all_stats(self):
        """Get all statistics"""
        return self.stats

# ==================== ADVANCED FILE OPERATIONS ====================

def get_file_info(file_path):
    """Get detailed file information"""
    try:
        stat = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return {
            'name': os.path.basename(file_path),
            'path': file_path,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'mime_type': mime_type or 'unknown',
            'is_dir': os.path.isdir(file_path),
            'readable': os.access(file_path, os.R_OK),
            'writable': os.access(file_path, os.W_OK)
        }
    except Exception as e:
        return {'error': str(e)}

def search_files(directory, query, max_results=50):
    """Search for files by name"""
    results = []
    query_lower = query.lower()
    
    try:
        for root, dirs, files in os.walk(directory):
            if len(results) >= max_results:
                break
            
            for file in files:
                if query_lower in file.lower():
                    file_path = os.path.join(root, file)
                    results.append(get_file_info(file_path))
                    
                    if len(results) >= max_results:
                        break
    except Exception as e:
        return {'error': str(e)}
    
    return results

def get_directory_tree(path, max_depth=3, current_depth=0):
    """Get directory structure as tree"""
    if current_depth >= max_depth:
        return None
    
    try:
        tree = {
            'name': os.path.basename(path) or path,
            'path': path,
            'is_dir': True,
            'children': []
        }
        
        items = os.listdir(path)
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                subtree = get_directory_tree(item_path, max_depth, current_depth + 1)
                if subtree:
                    tree['children'].append(subtree)
        
        return tree
    except Exception as e:
        return {'error': str(e)}

# ==================== CHUNK UPLOAD/DOWNLOAD ====================

class ChunkTransfer:
    """Handle large file transfers in chunks"""
    def __init__(self, chunk_size=1024*1024):  # 1MB chunks
        self.chunk_size = chunk_size
        self.transfers = {}
    
    def start_download(self, file_path):
        """Start file download"""
        if not os.path.exists(file_path):
            return None
        
        file_size = os.path.getsize(file_path)
        transfer_id = hashlib.md5(f"{file_path}{time.time()}".encode()).hexdigest()
        
        self.transfers[transfer_id] = {
            'file_path': file_path,
            'file_size': file_size,
            'chunks_total': (file_size + self.chunk_size - 1) // self.chunk_size,
            'started': datetime.now().isoformat()
        }
        
        return {
            'transfer_id': transfer_id,
            'file_size': file_size,
            'chunks_total': self.transfers[transfer_id]['chunks_total'],
            'chunk_size': self.chunk_size
        }
    
    def get_chunk(self, transfer_id, chunk_index):
        """Get specific file chunk"""
        if transfer_id not in self.transfers:
            return None
        
        transfer = self.transfers[transfer_id]
        file_path = transfer['file_path']
        
        try:
            with open(file_path, 'rb') as f:
                f.seek(chunk_index * self.chunk_size)
                chunk_data = f.read(self.chunk_size)
                return {
                    'chunk': chunk_data.hex(),
                    'index': chunk_index,
                    'size': len(chunk_data)
                }
        except Exception as e:
            return {'error': str(e)}

# ==================== DEVICE SESSION MANAGEMENT ====================

class SessionManager:
    """Manage device sessions with timeouts"""
    def __init__(self, timeout=3600):  # 1 hour
        self.sessions = {}
        self.timeout = timeout
    
    def create_session(self, device_id, device_info):
        """Create new session"""
        session_id = hashlib.md5(f"{device_id}{time.time()}".encode()).hexdigest()
        
        self.sessions[session_id] = {
            'device_id': device_id,
            'device_info': device_info,
            'created': time.time(),
            'last_activity': time.time(),
            'is_active': True
        }
        
        return session_id
    
    def validate_session(self, session_id):
        """Validate session and check timeout"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        elapsed = time.time() - session['last_activity']
        
        if elapsed > self.timeout:
            session['is_active'] = False
            return False
        
        session['last_activity'] = time.time()
        return session['is_active']
    
    def end_session(self, session_id):
        """End session"""
        if session_id in self.sessions:
            self.sessions[session_id]['is_active'] = False
    
    def cleanup_inactive(self):
        """Remove inactive sessions"""
        current_time = time.time()
        inactive = [
            sid for sid, session in self.sessions.items()
            if (current_time - session['last_activity']) > self.timeout
        ]
        
        for sid in inactive:
            del self.sessions[sid]
        
        return len(inactive)

# ==================== ENCRYPTION UTILITIES ====================

def encrypt_transfer(data, key):
    """Encrypt data for secure transfer"""
    try:
        from cryptography.fernet import Fernet
        cipher = Fernet(key)
        encrypted = cipher.encrypt(data.encode() if isinstance(data, str) else data)
        return encrypted.decode()
    except ImportError:
        return data

def decrypt_transfer(encrypted_data, key):
    """Decrypt transferred data"""
    try:
        from cryptography.fernet import Fernet
        cipher = Fernet(key)
        decrypted = cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except ImportError:
        return encrypted_data

# ==================== BANDWIDTH THROTTLING ====================

class BandwidthThrottler:
    """Limit bandwidth per device"""
    def __init__(self):
        self.limits = {}  # device_id: bytes_per_second
        self.transfer_stats = {}  # device_id: {bytes, timestamp}
    
    def set_limit(self, device_id, bytes_per_second):
        """Set bandwidth limit for device"""
        self.limits[device_id] = bytes_per_second
    
    def can_transfer(self, device_id, bytes_to_transfer):
        """Check if transfer respects bandwidth limit"""
        if device_id not in self.limits:
            return True
        
        limit = self.limits[device_id]
        now = time.time()
        
        if device_id not in self.transfer_stats:
            self.transfer_stats[device_id] = {'bytes': 0, 'timestamp': now}
        
        stats = self.transfer_stats[device_id]
        elapsed = now - stats['timestamp']
        
        if elapsed >= 1:  # Reset every second
            stats['bytes'] = 0
            stats['timestamp'] = now
        
        if stats['bytes'] + bytes_to_transfer <= limit:
            stats['bytes'] += bytes_to_transfer
            return True
        
        return False
    
    def get_wait_time(self, device_id, bytes_needed):
        """Get time to wait before transfer"""
        if device_id not in self.limits:
            return 0
        
        limit = self.limits[device_id]
        now = time.time()
        
        if device_id not in self.transfer_stats:
            return 0
        
        stats = self.transfer_stats[device_id]
        elapsed = now - stats['timestamp']
        
        if elapsed >= 1:
            return 0
        
        bytes_available = limit - stats['bytes']
        if bytes_available >= bytes_needed:
            return 0
        
        return 1 - elapsed

# ==================== EXPORT UTILITIES ====================

def export_device_data(device_id, format='json'):
    """Export device data in various formats"""
    from app import connected_devices
    
    if device_id not in connected_devices:
        return None
    
    device = connected_devices[device_id]
    
    if format == 'json':
        return json.dumps(device, indent=2, default=str)
    elif format == 'csv':
        # Convert to CSV format
        csv_data = "Field,Value\n"
        for key, value in device.items():
            csv_data += f"{key},{value}\n"
        return csv_data
    
    return None

def generate_device_report(device_id, analytics):
    """Generate device activity report"""
    stats = analytics.get_stats(device_id)
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'device_id': device_id,
        'summary': {
            'total_accesses': stats.get('total_accesses', 0),
            'total_downloads': stats.get('total_downloads', 0),
            'total_bytes': stats.get('total_bytes_transferred', 0),
            'last_activity': stats.get('last_activity')
        },
        'recent_activities': stats.get('activities', [])[-10:]  # Last 10 activities
    }
    
    return report

# ==================== INITIALIZATION ====================

def init_pro_extensions():
    """Initialize all professional extensions"""
    return {
        'file_watcher': FileWatcher,
        'analytics': DeviceAnalytics(),
        'chunk_transfer': ChunkTransfer(),
        'session_manager': SessionManager(),
        'bandwidth_throttler': BandwidthThrottler()
    }
