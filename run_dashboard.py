#!/usr/bin/env python3
"""
Standalone script to run the earthquake dashboard.
This fixes the eventlet import order issue.
"""

# IMPORTANT: monkey patch MUST be first
import eventlet
eventlet.monkey_patch()

from seismowatch.dashboard import create_dashboard

if __name__ == '__main__':
    print('🌐 Launching Real-time Earthquake Dashboard...')
    print('🚨 Live monitoring with WebSocket updates!')
    print('📡 Access at: http://127.0.0.1:5000')
    print('🔴 LIVE earthquake alerts will appear in real-time!')
    print('Press Ctrl+C to stop\n')
    
    dashboard = create_dashboard()
    dashboard.run(host='127.0.0.1', port=5000, debug=False)
