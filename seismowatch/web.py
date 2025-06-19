from flask import Flask, jsonify, render_template_string
from .earthquakes import EarthquakeDataFetcher
import json

def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>🌍 Earthquake Dashboard</title>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <style>
                body { font-family: Arial, sans-serif; margin: 0; background: #000; color: #fff; }
                .header { background: #ff6b6b; padding: 1rem; text-align: center; }
                #map { height: 600px; margin: 1rem; border-radius: 10px; }
                .info { padding: 1rem; text-align: center; }
                .stats { display: flex; justify-content: center; gap: 2rem; margin: 1rem; }
                .stat { background: #333; padding: 1rem; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌍 Live Earthquake Dashboard</h1>
                <p>Real-time earthquake data from USGS</p>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <h3 id="count">Loading...</h3>
                    <p>Total Earthquakes</p>
                </div>
                <div class="stat">
                    <h3 id="maxMag">Loading...</h3>
                    <p>Max Magnitude</p>
                </div>
            </div>
            
            <div id="map"></div>
            
            <div class="info">
                <p>🔴 Click markers for earthquake details</p>
                <p>🌈 Colors: Gold (M4-5) → Orange (M5-6) → Red (M6-7) → Purple (M7+)</p>
                <button onclick="location.reload()" style="padding: 1rem; font-size: 1rem; margin: 1rem;">🔄 Refresh Data</button>
            </div>

            <script>
                // Initialize map
                const map = L.map('map').setView([20, 0], 2);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map);

                // Load earthquake data
                fetch('/api/earthquakes')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Loaded earthquake data:', data);
                        
                        if (data.earthquakes && data.earthquakes.length > 0) {
                            // Update stats
                            document.getElementById('count').textContent = data.earthquakes.length;
                            const maxMag = Math.max(...data.earthquakes.map(eq => eq.magnitude));
                            document.getElementById('maxMag').textContent = 'M' + maxMag.toFixed(1);
                            
                            // Add earthquakes to map
                            data.earthquakes.forEach(eq => {
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
                                    ${new Date(eq.time).toLocaleString()}<br>
                                    Depth: ${eq.depth.toFixed(1)} km
                                `);
                            });
                        } else {
                            document.getElementById('count').textContent = '0';
                            document.getElementById('maxMag').textContent = 'N/A';
                        }
                    })
                    .catch(error => {
                        console.error('Error loading earthquake data:', error);
                        document.getElementById('count').textContent = 'Error';
                        document.getElementById('maxMag').textContent = 'Error';
                    });
                
                function getMagnitudeColor(magnitude) {
                    if (magnitude >= 7) return '#4B0082';  // Purple
                    if (magnitude >= 6) return '#8B0000';  // Dark Red
                    if (magnitude >= 5) return '#DC143C';  // Red
                    if (magnitude >= 4) return '#FF4500';  // Orange
                    return '#FFD700';  // Gold
                }
            </script>
        </body>
        </html>
        ''')
    
    @app.route('/api/earthquakes')
    def earthquakes():
        try:
            fetcher = EarthquakeDataFetcher()
            df = fetcher.fetch_earthquakes(min_magnitude=4.0, days=1, limit=100)
            
            if df.empty:
                return jsonify({'earthquakes': [], 'count': 0})
            
            earthquakes_list = []
            for _, eq in df.iterrows():
                earthquakes_list.append({
                    'magnitude': float(eq['magnitude']),
                    'location': str(eq['place']),
                    'latitude': float(eq['latitude']),
                    'longitude': float(eq['longitude']),
                    'depth': float(eq['depth']),
                    'time': eq['time'].isoformat()
                })
            
            return jsonify({'earthquakes': earthquakes_list, 'count': len(earthquakes_list)})
        
        except Exception as e:
            return jsonify({'error': str(e), 'earthquakes': [], 'count': 0})
    
    @app.route('/api/info')
    def info():
        return jsonify({
            'project': 'MyProject',
            'description': 'A versatile Python toolkit with earthquake monitoring',
            'capabilities': ['CLI', 'Web API', 'Earthquake Monitoring', 'Geospatial Analysis']
        })
    
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)