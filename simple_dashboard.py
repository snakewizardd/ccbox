#!/usr/bin/env python3
"""Simple earthquake dashboard without WebSocket complications."""

from flask import Flask, render_template_string, jsonify
from seismowatch.earthquakes import EarthquakeDataFetcher
import json

app = Flask(__name__)

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌍 Earthquake Dashboard</title>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; }
        .header { background: linear-gradient(135deg, #ff6b6b, #ee5a24); padding: 1rem; text-align: center; }
        .header h1 { font-size: 2.5rem; font-weight: bold; }
        .status { background: #27ae60; color: white; padding: 0.3rem 1rem; border-radius: 20px; margin-left: 1rem; }
        .container { display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; padding: 1rem; height: calc(100vh - 80px); }
        .map-container { background: #1a1a1a; border-radius: 10px; overflow: hidden; }
        #map { height: 100%; }
        .sidebar { display: flex; flex-direction: column; gap: 1rem; }
        .panel { background: #1a1a1a; border-radius: 10px; padding: 1rem; }
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .stat-item { text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 8px; }
        .stat-value { font-size: 2rem; font-weight: bold; display: block; }
        .stat-label { font-size: 0.9rem; opacity: 0.8; margin-top: 0.2rem; }
        .refresh-btn { background: #27ae60; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer; }
        .refresh-btn:hover { background: #2ecc71; }
        @media (max-width: 768px) { .container { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 Earthquake Dashboard</h1>
        <span class="status">📊 LIVE DATA</span>
    </div>
    
    <div class="container">
        <div class="map-container">
            <div id="map"></div>
        </div>
        
        <div class="sidebar">
            <div class="panel">
                <h3>📊 Statistics</h3>
                <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
                <div class="stats-grid" style="margin-top: 1rem;">
                    <div class="stat-item">
                        <span class="stat-value" id="totalEarthquakes">{{ count }}</span>
                        <span class="stat-label">Total Found</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value" id="maxMagnitude">M{{ max_mag }}</span>
                        <span class="stat-label">Max Magnitude</span>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <h3>🚨 Recent Earthquakes</h3>
                <div id="earthquakeList">
                    {% for eq in earthquakes[:5] %}
                    <div style="background: #333; margin: 0.5rem 0; padding: 0.5rem; border-radius: 5px;">
                        <strong>M{{ "%.1f"|format(eq.magnitude) }}</strong> - {{ eq.location }}<br>
                        <small>{{ eq.time.strftime('%Y-%m-%d %H:%M UTC') }}</small>
                    </div>
                    {% endfor %}
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

        // Earthquake data
        const earthquakes = {{ earthquakes_json | safe }};
        
        function getMagnitudeColor(magnitude) {
            if (magnitude >= 7) return '#4B0082';
            if (magnitude >= 6) return '#8B0000';
            if (magnitude >= 5) return '#DC143C';
            if (magnitude >= 4) return '#FF4500';
            return '#FFD700';
        }
        
        // Add earthquakes to map
        earthquakes.forEach(eq => {
            const color = getMagnitudeColor(eq.magnitude);
            const marker = L.circleMarker([eq.latitude, eq.longitude], {
                radius: Math.max(5, eq.magnitude * 3),
                fillColor: color,
                color: '#000',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);
            
            marker.bindPopup(`
                <b>M${eq.magnitude} Earthquake</b><br>
                ${eq.location}<br>
                ${eq.time}<br>
                Depth: ${eq.depth.toFixed(1)} km
            `);
        });
        
        function refreshData() {
            location.reload();
        }
        
        console.log(`Loaded ${earthquakes.length} earthquakes`);
    </script>
</body>
</html>'''

@app.route('/')
def dashboard():
    """Main dashboard page."""
    fetcher = EarthquakeDataFetcher()
    
    # Get recent earthquakes
    df = fetcher.fetch_earthquakes(min_magnitude=4.0, days=1, limit=100)
    
    if df.empty:
        earthquakes = []
        count = 0
        max_mag = 0
    else:
        earthquakes = []
        for _, eq in df.iterrows():
            earthquakes.append({
                'magnitude': eq['magnitude'],
                'location': eq['place'],
                'latitude': eq['latitude'],
                'longitude': eq['longitude'],
                'depth': eq['depth'],
                'time': eq['time'].strftime('%Y-%m-%d %H:%M UTC')
            })
        count = len(earthquakes)
        max_mag = f"{df['magnitude'].max():.1f}"
    
    earthquakes_json = json.dumps(earthquakes)
    
    return render_template_string(HTML_TEMPLATE, 
                                earthquakes=earthquakes,
                                earthquakes_json=earthquakes_json,
                                count=count,
                                max_mag=max_mag)

@app.route('/api/earthquakes')
def api_earthquakes():
    """API endpoint for earthquake data."""
    fetcher = EarthquakeDataFetcher()
    df = fetcher.fetch_earthquakes(min_magnitude=4.0, days=1, limit=100)
    
    if df.empty:
        return jsonify({'earthquakes': [], 'count': 0})
    
    earthquakes = []
    for _, eq in df.iterrows():
        earthquakes.append({
            'magnitude': eq['magnitude'],
            'location': eq['place'],
            'latitude': eq['latitude'],
            'longitude': eq['longitude'],
            'depth': eq['depth'],
            'time': eq['time'].isoformat()
        })
    
    return jsonify({'earthquakes': earthquakes, 'count': len(earthquakes)})

if __name__ == '__main__':
    print('🌍 Starting Simple Earthquake Dashboard...')
    print('📡 Go to: http://127.0.0.1:5001')
    print('🚨 Loading real earthquake data from USGS...')
    
    app.run(host='127.0.0.1', port=5001, debug=True)
