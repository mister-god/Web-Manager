#!/usr/bin/env python3
"""
CLEANUP - Remove temporary files and reset tool
"""

import os
import shutil
import sys

def cleanup():
    print("\n" + "="*60)
    print("🧹 WEB MANAGER - Cleanup Tool")
    print("="*60 + "\n")
    
    # Remove uploads
    if os.path.exists('uploads'):
        shutil.rmtree('uploads')
        print("✅ Removed uploads/ folder")
    
    # Remove logs
    if os.path.exists('logs'):
        shutil.rmtree('logs')
        print("✅ Removed logs/ folder")
    
    # Remove temp files
    temp_files = ['flask_session', 'cache', '*.pyc', '__pycache__']
    for pattern in temp_files:
        os.system(f"rm -rf {pattern} 2>/dev/null")
    print("✅ Removed temp files")
    
    # Remove cloudflared log
    if os.path.exists('cloudflared.log'):
        os.remove('cloudflared.log')
        print("✅ Removed cloudflared.log")
    
    print("\n" + "="*60)
    print("✅ Cleanup complete!")
    print("="*60 + "\n")

def reset():
    print("\n⚠️ This will reset ALL data!")
    confirm = input("Type 'RESET' to confirm: ")
    if confirm == 'RESET':
        cleanup()
        print("✅ Tool reset to initial state")
    else:
        print("❌ Reset cancelled")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        reset()
    else:
        cleanup()