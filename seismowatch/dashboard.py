import json
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import eventlet

from .earthquakes import EarthquakeDataFetcher, EarthquakeVisualizer
from .alerts import EarthquakeMonitor, AlertZone, ConsoleNotificationHandler

# Monkey patch for eventlet
eventlet.monkey_patch()

class DashboardNotificationHandler:
    """Notification handler that sends alerts via WebSocket."""
    
    def __init__(self, socketio):
        self.socketio = socketio
    
    def send_alert(self, alert):
        """Send alert via WebSocket to all connected clients."""
        alert_data = {
            'id': alert.earthquake_id,
            'magnitude': alert.magnitude,
            'location': alert.location,
            'latitude': alert.latitude,
            'longitude': alert.longitude,
            'depth': alert.depth,
            'time': alert.time.isoformat(),
            'zone_name': alert.zone_name,
            'alert_time': alert.alert_time.isoformat(),
            'tsunami_warning': alert.tsunami_warning
        }
        
        # Emit to all connected clients
        self.socketio.emit('earthquake_alert', alert_data)
        print(f"📡 Broadcasted alert: M{alert.magnitude} - {alert.location}")
        return True

class EarthquakeDashboard:
    """Real-time earthquake monitoring dashboard."""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'earthquake_dashboard_secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='eventlet')
        
        self.fetcher = EarthquakeDataFetcher()
        self.visualizer = EarthquakeVisualizer()
        self.monitor = EarthquakeMonitor(check_interval=30)  # Check every 30 seconds
        
        # Add notification handler for WebSocket alerts
        self.dashboard_handler = DashboardNotificationHandler(self.socketio)
        self.monitor.add_notification_handler(self.dashboard_handler)
        
        # Setup default alert zones
        self._setup_default_zones()
        
        # Setup routes and WebSocket handlers
        self._setup_routes()
        self._setup_websocket_handlers()
        
        # Start monitoring in background
        self.monitoring_thread = None
    
    def _setup_default_zones(self):
        """Setup default earthquake monitoring zones."""
        default_zones = [
            AlertZone("Global Major Events", 0, 0, 50000, 6.0),
            AlertZone("Pacific Ring of Fire", 0, -160, 15000, 5.0),
            AlertZone("California", 36.7783, -119.4179, 500, 4.0),
            AlertZone("Japan", 36.2048, 138.2529, 1000, 4.5),
        ]
        
        for zone in default_zones:
            self.monitor.add_alert_zone(zone)
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/api/recent_earthquakes')
        def recent_earthquakes():
            """Get recent earthquake data."""
            try:
                days = request.args.get('days', 1, type=int)
                min_mag = request.args.get('min_mag', 4.0, type=float)
                limit = request.args.get('limit', 100, type=int)
                
                df = self.fetcher.fetch_earthquakes(
                    min_magnitude=min_mag,
                    days=days,
                    limit=limit
                )
                
                if df.empty:
                    return jsonify({'earthquakes': [], 'count': 0})
                
                earthquakes = []
                for _, eq in df.iterrows():
                    earthquakes.append({
                        'id': eq['id'],
                        'magnitude': eq['magnitude'],
                        'location': eq['place'],
                        'latitude': eq['latitude'],
                        'longitude': eq['longitude'],
                        'depth': eq['depth'],
                        'time': eq['time'].isoformat(),
                        'tsunami': eq['tsunami'],
                        'significance': eq['significance']
                    })
                
                return jsonify({
                    'earthquakes': earthquakes,
                    'count': len(earthquakes),
                    'max_magnitude': float(df['magnitude'].max()),
                    'avg_magnitude': float(df['magnitude'].mean())
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stats')
        def earthquake_stats():
            """Get earthquake statistics."""
            try:
                df = self.fetcher.fetch_earthquakes(min_magnitude=2.0, days=7, limit=1000)
                
                if df.empty:
                    return jsonify({'error': 'No data available'})
                
                stats = {
                    'total_earthquakes': len(df),
                    'avg_magnitude': float(df['magnitude'].mean()),
                    'max_magnitude': float(df['magnitude'].max()),
                    'recent_24h': len(df[df['time'] > datetime.now() - timedelta(hours=24)]),
                    'magnitude_distribution': {
                        '2.0-2.9': len(df[(df['magnitude'] >= 2.0) & (df['magnitude'] < 3.0)]),
                        '3.0-3.9': len(df[(df['magnitude'] >= 3.0) & (df['magnitude'] < 4.0)]),
                        '4.0-4.9': len(df[(df['magnitude'] >= 4.0) & (df['magnitude'] < 5.0)]),
                        '5.0-5.9': len(df[(df['magnitude'] >= 5.0) & (df['magnitude'] < 6.0)]),
                        '6.0+': len(df[df['magnitude'] >= 6.0])
                    }
                }
                
                return jsonify(stats)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/alert_zones')
        def get_alert_zones():
            """Get configured alert zones."""
            zones = []
            for zone in self.monitor.alert_zones:
                zones.append({
                    'name': zone.name,
                    'center_lat': zone.center_lat,
                    'center_lon': zone.center_lon,
                    'radius_km': zone.radius_km,
                    'min_magnitude': zone.min_magnitude
                })
            return jsonify({'zones': zones})
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            print(f"🔌 Client connected: {request.sid}")
            emit('connected', {'message': 'Connected to earthquake dashboard'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            print(f"🔌 Client disconnected: {request.sid}")
        
        @self.socketio.on('request_recent_data')
        def handle_recent_data_request():
            """Send recent earthquake data to client."""
            try:
                df = self.fetcher.fetch_earthquakes(min_magnitude=4.0, days=1, limit=50)
                earthquakes = []
                
                for _, eq in df.iterrows():
                    earthquakes.append({
                        'magnitude': eq['magnitude'],
                        'location': eq['place'],
                        'latitude': eq['latitude'],
                        'longitude': eq['longitude'],
                        'time': eq['time'].isoformat()
                    })
                
                emit('recent_earthquakes', {'earthquakes': earthquakes})
                
            except Exception as e:
                emit('error', {'message': str(e)})
    
    def start_monitoring(self):
        """Start earthquake monitoring in background thread."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            print("Monitoring already running!")
            return
        
        def monitor_loop():
            """Background monitoring loop."""
            print("🔍 Starting background earthquake monitoring...")
            while True:
                try:
                    self.monitor.check_for_earthquakes()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    print(f"Error in monitoring loop: {e}")
                    time.sleep(30)
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Run the dashboard application."""
        # Start monitoring
        self.start_monitoring()
        
        print(f"🌐 Starting Earthquake Dashboard on http://{host}:{port}")
        print("🚨 Real-time earthquake monitoring active!")
        print("📡 WebSocket live updates enabled")
        
        # Run with eventlet for WebSocket support
        self.socketio.run(self.app, host=host, port=port, debug=debug)

# Create HTML template
DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌍 Live Earthquake Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.6.1/socket.io.js"></script>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a0a; color: #fff; overflow-x: hidden; }
        .header { background: linear-gradient(135deg, #ff6b6b, #ee5a24); padding: 1rem; text-align: center; box-shadow: 0 4px 20px rgba(255,107,107,0.3); }
        .header h1 { font-size: 2.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .status { display: inline-block; background: #27ae60; color: white; padding: 0.3rem 1rem; border-radius: 20px; margin-left: 1rem; font-size: 0.9rem; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        .container { display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; padding: 1rem; height: calc(100vh - 80px); }
        .map-container { background: #1a1a1a; border-radius: 10px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
        #map { height: 100%; }
        .sidebar { display: flex; flex-direction: column; gap: 1rem; }
        .panel { background: #1a1a1a; border-radius: 10px; padding: 1rem; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
        .alert-feed { flex: 1; max-height: 300px; overflow-y: auto; }
        .alert-item { background: linear-gradient(135deg, #ff6b6b, #ee5a24); margin: 0.5rem 0; padding: 1rem; border-radius: 8px; animation: slideIn 0.5s ease-out; border-left: 4px solid #fff; }
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        .alert-magnitude { font-size: 1.5rem; font-weight: bold; color: #fff; }
        .alert-location { font-size: 0.9rem; opacity: 0.9; margin-top: 0.2rem; }
        .alert-time { font-size: 0.8rem; opacity: 0.7; margin-top: 0.3rem; }
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .stat-item { text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 8px; }
        .stat-value { font-size: 2rem; font-weight: bold; display: block; }
        .stat-label { font-size: 0.9rem; opacity: 0.8; margin-top: 0.2rem; }
        .connection-status { position: fixed; top: 20px; right: 20px; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; z-index: 1000; }
        .connected { background: #27ae60; }
        .disconnected { background: #e74c3c; }
        @media (max-width: 768px) { .container { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 Live Earthquake Dashboard</h1>
        <span class="status">🔴 LIVE MONITORING</span>
    </div>
    
    <div class="connection-status connected" id="connectionStatus">🔌 Connected</div>
    
    <div class="container">
        <div class="map-container">
            <div id="map"></div>
        </div>
        
        <div class="sidebar">
            <div class="panel">
                <h3>📊 Live Statistics</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-value" id="totalEarthquakes">-</span>
                        <span class="stat-label">Total Today</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value" id="maxMagnitude">-</span>
                        <span class="stat-label">Max Magnitude</span>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <h3>🚨 Live Alert Feed</h3>
                <div class="alert-feed" id="alertFeed">
                    <div style="text-align: center; opacity: 0.7; padding: 2rem;">
                        Waiting for earthquake alerts...
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Initialize map
        const map = L.map('map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Initialize WebSocket
        const socket = io();
        
        // Connection status
        const statusEl = document.getElementById('connectionStatus');
        
        socket.on('connect', () => {
            statusEl.textContent = '🔌 Connected';
            statusEl.className = 'connection-status connected';
            console.log('Connected to earthquake dashboard');
        });
        
        socket.on('disconnect', () => {
            statusEl.textContent = '❌ Disconnected';
            statusEl.className = 'connection-status disconnected';
        });
        
        // Handle earthquake alerts
        socket.on('earthquake_alert', (alert) => {
            console.log('New earthquake alert:', alert);
            
            // Add to map
            const color = getMagnitudeColor(alert.magnitude);
            const marker = L.circleMarker([alert.latitude, alert.longitude], {
                radius: Math.max(5, alert.magnitude * 3),
                fillColor: color,
                color: '#000',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);
            
            marker.bindPopup(`
                <b>M${alert.magnitude} Earthquake</b><br>
                ${alert.location}<br>
                ${new Date(alert.time).toLocaleString()}<br>
                Depth: ${alert.depth.toFixed(1)} km
            `);
            
            // Add to alert feed
            addAlertToFeed(alert);
            
            // Play alert sound (optional)
            playAlertSound();
        });
        
        function getMagnitudeColor(magnitude) {
            if (magnitude >= 7) return '#4B0082';
            if (magnitude >= 6) return '#8B0000';
            if (magnitude >= 5) return '#DC143C';
            if (magnitude >= 4) return '#FF4500';
            return '#FFD700';
        }
        
        function addAlertToFeed(alert) {
            const feed = document.getElementById('alertFeed');
            
            // Clear "waiting" message
            if (feed.children.length === 1 && feed.children[0].textContent.includes('Waiting')) {
                feed.innerHTML = '';
            }
            
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert-item';
            alertDiv.innerHTML = `
                <div class="alert-magnitude">M${alert.magnitude}</div>
                <div class="alert-location">${alert.location}</div>
                <div class="alert-time">${new Date(alert.time).toLocaleString()}</div>
            `;
            
            feed.insertBefore(alertDiv, feed.firstChild);
            
            // Keep only last 10 alerts
            while (feed.children.length > 10) {
                feed.removeChild(feed.lastChild);
            }
        }
        
        function playAlertSound() {
            // Create audio context for alert sound
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        }
        
        // Load initial data
        fetch('/api/recent_earthquakes?days=1&min_mag=4.0')
            .then(response => response.json())
            .then(data => {
                if (data.earthquakes) {
                    data.earthquakes.forEach(eq => {
                        const color = getMagnitudeColor(eq.magnitude);
                        const marker = L.circleMarker([eq.latitude, eq.longitude], {
                            radius: Math.max(5, eq.magnitude * 3),
                            fillColor: color,
                            color: '#000',
                            weight: 1,
                            opacity: 0.7,
                            fillOpacity: 0.6
                        }).addTo(map);
                        
                        marker.bindPopup(`
                            <b>M${eq.magnitude} Earthquake</b><br>
                            ${eq.location}<br>
                            ${new Date(eq.time).toLocaleString()}<br>
                            Depth: ${eq.depth.toFixed(1)} km
                        `);
                    });
                    
                    // Update stats
                    document.getElementById('totalEarthquakes').textContent = data.count;
                    document.getElementById('maxMagnitude').textContent = 'M' + data.max_magnitude.toFixed(1);
                }
            })
            .catch(error => console.error('Error loading earthquake data:', error));
    </script>
</body>
</html>'''

def create_dashboard():
    """Create and return the earthquake dashboard."""
    return EarthquakeDashboard()

if __name__ == '__main__':
    # Create templates directory
    import os
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Write template file
    with open(os.path.join(templates_dir, 'dashboard.html'), 'w') as f:
        f.write(DASHBOARD_HTML)
    
    # Run dashboard
    dashboard = create_dashboard()
    dashboard.run(debug=True)