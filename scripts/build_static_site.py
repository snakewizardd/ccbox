#!/usr/bin/env python3
"""Build static site for GitHub Pages deployment."""

import os
import shutil
import json
from pathlib import Path

def create_index_html():
    """Create the main index.html for the static site."""
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SeismoWatch - Real-time Earthquake Monitoring</title>
    <meta name="description" content="Real-time earthquake monitoring platform with live alerts and interactive visualizations">
    <meta name="keywords" content="earthquake, seismic, monitoring, alerts, USGS, real-time">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://seismowatch.github.io/">
    <meta property="og:title" content="SeismoWatch - Real-time Earthquake Monitoring">
    <meta property="og:description" content="Monitor earthquakes worldwide with real-time alerts and beautiful visualizations">
    <meta property="og:image" content="https://seismowatch.github.io/assets/og-image.png">

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://seismowatch.github.io/">
    <meta property="twitter:title" content="SeismoWatch - Real-time Earthquake Monitoring">
    <meta property="twitter:description" content="Monitor earthquakes worldwide with real-time alerts and beautiful visualizations">
    <meta property="twitter:image" content="https://seismowatch.github.io/assets/og-image.png">
    
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-brand">
                <h1>🌍 SeismoWatch</h1>
            </div>
            <div class="nav-links">
                <a href="#features">Features</a>
                <a href="#dashboard">Dashboard</a>
                <a href="https://github.com/seismowatch/seismowatch">GitHub</a>
            </div>
        </div>
    </nav>

    <header class="hero">
        <div class="hero-content">
            <h1 class="hero-title">Real-time Earthquake Monitoring</h1>
            <p class="hero-subtitle">Stay informed about seismic activity worldwide with live alerts, interactive maps, and intelligent monitoring.</p>
            <div class="hero-buttons">
                <a href="#dashboard" class="btn btn-primary">View Live Dashboard</a>
                <a href="https://github.com/seismowatch/seismowatch" class="btn btn-secondary">View on GitHub</a>
            </div>
        </div>
        <div class="hero-stats">
            <div class="stat-card">
                <h3 id="total-earthquakes">Loading...</h3>
                <p>Earthquakes Today</p>
            </div>
            <div class="stat-card">
                <h3 id="max-magnitude">Loading...</h3>
                <p>Maximum Magnitude</p>
            </div>
            <div class="stat-card">
                <h3 id="active-regions">Loading...</h3>
                <p>Active Regions</p>
            </div>
        </div>
    </header>

    <section id="features" class="features">
        <div class="container">
            <h2>Powerful Features</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🔴</div>
                    <h3>Real-time Monitoring</h3>
                    <p>Live earthquake data from USGS with 30-second updates and instant WebSocket alerts.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🗺️</div>
                    <h3>Interactive Maps</h3>
                    <p>Beautiful visualizations with magnitude-based color coding and detailed popup information.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🚨</div>
                    <h3>Smart Alerts</h3>
                    <p>Custom alert zones with configurable thresholds and multiple notification channels.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Analytics</h3>
                    <p>Historical data analysis, trends, and insights into global seismic activity patterns.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🛠️</div>
                    <h3>Developer Tools</h3>
                    <p>CLI interface, REST API, and Python SDK for custom integrations and analysis.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📱</div>
                    <h3>Mobile Ready</h3>
                    <p>Responsive design that works perfectly on desktop, tablet, and mobile devices.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="dashboard" class="dashboard-section">
        <div class="container">
            <h2>Live Earthquake Dashboard</h2>
            <p class="section-subtitle">Real-time seismic activity from around the world</p>
            
            <div class="dashboard-stats">
                <div class="dashboard-stat">
                    <h3 id="live-count">Loading...</h3>
                    <p>Recent Earthquakes (24h)</p>
                </div>
                <div class="dashboard-stat">
                    <h3 id="live-max-mag">Loading...</h3>
                    <p>Maximum Magnitude</p>
                </div>
                <div class="dashboard-stat">
                    <h3 id="live-avg-depth">Loading...</h3>
                    <p>Average Depth</p>
                </div>
            </div>

            <div class="map-container">
                <div id="earthquake-map"></div>
            </div>

            <div class="map-controls">
                <button id="refresh-btn" class="btn btn-primary">🔄 Refresh Data</button>
                <div class="map-info">
                    <p>🔴 Click markers for earthquake details • 🌈 Colors indicate magnitude strength</p>
                </div>
            </div>
        </div>
    </section>

    <section class="installation">
        <div class="container">
            <h2>Get Started</h2>
            <div class="install-grid">
                <div class="install-card">
                    <h3>Quick Install</h3>
                    <pre><code>pip install seismowatch</code></pre>
                </div>
                <div class="install-card">
                    <h3>Start Monitoring</h3>
                    <pre><code>seismowatch alert-demo</code></pre>
                </div>
                <div class="install-card">
                    <h3>Web Dashboard</h3>
                    <pre><code>seismowatch dashboard</code></pre>
                </div>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>SeismoWatch</h3>
                    <p>Real-time earthquake monitoring for everyone.</p>
                </div>
                <div class="footer-section">
                    <h3>Links</h3>
                    <a href="https://github.com/seismowatch/seismowatch">GitHub</a>
                    <a href="https://seismowatch.readthedocs.io/">Documentation</a>
                    <a href="https://github.com/seismowatch/seismowatch/issues">Issues</a>
                </div>
                <div class="footer-section">
                    <h3>Data Sources</h3>
                    <a href="https://earthquake.usgs.gov/">USGS</a>
                    <a href="https://www.openstreetmap.org/">OpenStreetMap</a>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 SeismoWatch. Made with ❤️ for earthquake monitoring.</p>
            </div>
        </div>
    </footer>

    <script src="assets/app.js"></script>
</body>
</html>'''
    
    return html_content

def create_css():
    """Create the CSS styles for the static site."""
    
    css_content = '''/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}

/* Navigation */
.navbar {
    background: rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 1000;
    padding: 1rem 0;
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand h1 {
    color: white;
    font-size: 1.5rem;
}

.nav-links {
    display: flex;
    gap: 2rem;
}

.nav-links a {
    color: white;
    text-decoration: none;
    transition: opacity 0.3s;
}

.nav-links a:hover {
    opacity: 0.8;
}

/* Hero section */
.hero {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: white;
    padding: 8rem 2rem 4rem;
    background: rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(5px);
}

.hero-title {
    font-size: 4rem;
    font-weight: bold;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
    font-size: 1.5rem;
    margin-bottom: 3rem;
    opacity: 0.9;
    max-width: 600px;
}

.hero-buttons {
    display: flex;
    gap: 1rem;
    margin-bottom: 4rem;
}

.btn {
    display: inline-block;
    padding: 1rem 2rem;
    border-radius: 50px;
    text-decoration: none;
    font-weight: bold;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
    font-size: 1rem;
}

.btn-primary {
    background: #ff4757;
    color: white;
}

.btn-primary:hover {
    background: #ff2f40;
    transform: translateY(-2px);
}

.btn-secondary {
    background: transparent;
    color: white;
    border: 2px solid white;
}

.btn-secondary:hover {
    background: white;
    color: #667eea;
}

.hero-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    max-width: 800px;
    width: 100%;
}

.stat-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    padding: 2rem;
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-card h3 {
    font-size: 2.5rem;
    color: #ffeb3b;
    margin-bottom: 0.5rem;
}

/* Features section */
.features {
    background: white;
    padding: 6rem 0;
}

.features h2 {
    text-align: center;
    font-size: 3rem;
    margin-bottom: 4rem;
    color: #333;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 3rem;
}

.feature-card {
    text-align: center;
    padding: 2rem;
    border-radius: 15px;
    background: #f8f9fa;
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.feature-card h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #333;
}

.feature-card p {
    color: #666;
    line-height: 1.6;
}

/* Dashboard section */
.dashboard-section {
    background: #f8f9fa;
    padding: 6rem 0;
}

.dashboard-section h2 {
    text-align: center;
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #333;
}

.section-subtitle {
    text-align: center;
    font-size: 1.2rem;
    color: #666;
    margin-bottom: 4rem;
}

.dashboard-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
}

.dashboard-stat {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.dashboard-stat h3 {
    font-size: 2rem;
    color: #ff6b6b;
    margin-bottom: 0.5rem;
}

.map-container {
    background: white;
    border-radius: 15px;
    overflow: hidden;
    margin-bottom: 2rem;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

#earthquake-map {
    height: 600px;
    width: 100%;
}

.map-controls {
    text-align: center;
}

.map-info {
    margin-top: 1rem;
    color: #666;
}

/* Installation section */
.installation {
    background: white;
    padding: 6rem 0;
}

.installation h2 {
    text-align: center;
    font-size: 3rem;
    margin-bottom: 4rem;
    color: #333;
}

.install-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.install-card {
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
}

.install-card h3 {
    margin-bottom: 1rem;
    color: #333;
}

.install-card pre {
    background: #333;
    color: #00ff00;
    padding: 1rem;
    border-radius: 10px;
    font-family: 'Courier New', monospace;
    overflow-x: auto;
}

/* Footer */
.footer {
    background: #333;
    color: white;
    padding: 4rem 0 2rem;
}

.footer-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 3rem;
    margin-bottom: 2rem;
}

.footer-section h3 {
    margin-bottom: 1rem;
    color: #ff6b6b;
}

.footer-section a {
    display: block;
    color: #ccc;
    text-decoration: none;
    margin-bottom: 0.5rem;
    transition: color 0.3s;
}

.footer-section a:hover {
    color: white;
}

.footer-bottom {
    text-align: center;
    padding-top: 2rem;
    border-top: 1px solid #555;
    color: #ccc;
}

/* Responsive design */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
    }
    
    .hero-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .nav-links {
        display: none;
    }
    
    .features h2, .dashboard-section h2, .installation h2 {
        font-size: 2rem;
    }
    
    #earthquake-map {
        height: 400px;
    }
}

/* Loading animation */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.loading {
    animation: pulse 2s infinite;
}'''
    
    return css_content

def create_javascript():
    """Create the JavaScript for the static site."""
    
    js_content = '''// Earthquake monitoring application
class EarthquakeMonitor {
    constructor() {
        this.map = null;
        this.earthquakeLayer = null;
        this.earthquakes = [];
        this.init();
    }

    init() {
        this.loadInitialStats();
        this.initMap();
        this.loadEarthquakeData();
        this.setupEventListeners();
        
        // Auto-refresh every 5 minutes
        setInterval(() => this.loadEarthquakeData(), 5 * 60 * 1000);
    }

    async loadInitialStats() {
        try {
            const response = await fetch('https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=' +
                new Date(Date.now() - 24*60*60*1000).toISOString() + '&minmagnitude=4.0');
            const data = await response.json();
            
            if (data.features) {
                const earthquakes = data.features;
                const magnitudes = earthquakes.map(eq => eq.properties.mag).filter(m => m !== null);
                
                document.getElementById('total-earthquakes').textContent = earthquakes.length;
                document.getElementById('max-magnitude').textContent = magnitudes.length > 0 ? 
                    'M' + Math.max(...magnitudes).toFixed(1) : 'N/A';
                
                // Count active regions (rough estimate)
                const regions = new Set(earthquakes.map(eq => 
                    Math.floor(eq.geometry.coordinates[1] / 10) + ',' + Math.floor(eq.geometry.coordinates[0] / 10)
                ));
                document.getElementById('active-regions').textContent = regions.size;
            }
        } catch (error) {
            console.error('Error loading initial stats:', error);
        }
    }

    initMap() {
        if (!document.getElementById('earthquake-map')) return;
        
        this.map = L.map('earthquake-map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        
        this.earthquakeLayer = L.layerGroup().addTo(this.map);
    }

    getMagnitudeColor(magnitude) {
        if (magnitude >= 8) return '#4B0082';  // Purple
        if (magnitude >= 7) return '#8B0000';  // Dark Red  
        if (magnitude >= 6) return '#DC143C';  // Red
        if (magnitude >= 5) return '#FF4500';  // Orange
        return '#FFD700';  // Gold
    }

    async loadEarthquakeData() {
        try {
            this.updateLoadingState(true);
            
            // Clear existing markers
            if (this.earthquakeLayer) {
                this.earthquakeLayer.clearLayers();
            }
            
            const yesterday = new Date(Date.now() - 24*60*60*1000).toISOString();
            const response = await fetch(
                `https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=${yesterday}&minmagnitude=4.0&limit=100`
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.features || data.features.length === 0) {
                this.updateStats(0, 'N/A', 'N/A');
                return;
            }
            
            this.earthquakes = data.features;
            this.updateStats();
            this.updateMap();
            
        } catch (error) {
            console.error('Error loading earthquake data:', error);
            this.updateStats('Error', 'Error', 'Error');
        } finally {
            this.updateLoadingState(false);
        }
    }

    updateStats(count = null, maxMag = null, avgDepth = null) {
        if (count === null) {
            count = this.earthquakes.length;
        }
        
        if (maxMag === null) {
            const magnitudes = this.earthquakes.map(eq => eq.properties.mag).filter(m => m !== null);
            maxMag = magnitudes.length > 0 ? 'M' + Math.max(...magnitudes).toFixed(1) : 'N/A';
        }
        
        if (avgDepth === null) {
            const depths = this.earthquakes.map(eq => eq.geometry.coordinates[2]).filter(d => d !== null);
            avgDepth = depths.length > 0 ? (depths.reduce((a, b) => a + b, 0) / depths.length).toFixed(1) + ' km' : 'N/A';
        }
        
        const countEl = document.getElementById('live-count');
        const maxMagEl = document.getElementById('live-max-mag');
        const avgDepthEl = document.getElementById('live-avg-depth');
        
        if (countEl) countEl.textContent = count;
        if (maxMagEl) maxMagEl.textContent = maxMag;
        if (avgDepthEl) avgDepthEl.textContent = avgDepth;
    }

    updateMap() {
        if (!this.map || !this.earthquakeLayer) return;
        
        this.earthquakes.forEach(eq => {
            const coords = eq.geometry.coordinates;
            const props = eq.properties;
            
            if (coords[1] && coords[0] && props.mag) {
                const color = this.getMagnitudeColor(props.mag);
                const marker = L.circleMarker([coords[1], coords[0]], {
                    radius: Math.max(5, props.mag * 3),
                    fillColor: color,
                    color: '#000',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
                
                const time = new Date(props.time);
                marker.bindPopup(`
                    <div style="color: #000; font-weight: bold; min-width: 200px;">
                        <h3 style="margin: 0; color: ${color};">M${props.mag} Earthquake</h3>
                        <p style="margin: 0.5rem 0;"><strong>Location:</strong> ${props.place}</p>
                        <p style="margin: 0.5rem 0;"><strong>Time:</strong> ${time.toLocaleString()}</p>
                        <p style="margin: 0.5rem 0;"><strong>Depth:</strong> ${coords[2].toFixed(1)} km</p>
                        <p style="margin: 0.5rem 0;"><strong>Significance:</strong> ${props.sig || 'N/A'}</p>
                        ${props.tsunami ? '<p style="color: red; font-weight: bold;">🌊 TSUNAMI WARNING</p>' : ''}
                    </div>
                `);
                
                this.earthquakeLayer.addLayer(marker);
            }
        });
        
        console.log(`Added ${this.earthquakes.length} earthquakes to map`);
    }

    updateLoadingState(isLoading) {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.disabled = isLoading;
            refreshBtn.textContent = isLoading ? '⏳ Loading...' : '🔄 Refresh Data';
        }
        
        // Add loading class to stats
        const stats = ['live-count', 'live-max-mag', 'live-avg-depth'];
        stats.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                if (isLoading) {
                    el.classList.add('loading');
                    el.textContent = 'Loading...';
                } else {
                    el.classList.remove('loading');
                }
            }
        });
    }

    setupEventListeners() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadEarthquakeData();
            });
        }

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EarthquakeMonitor();
});

// Add some visual enhancements
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(0, 0, 0, 0.9)';
    } else {
        navbar.style.background = 'rgba(0, 0, 0, 0.1)';
    }
});'''
    
    return js_content

def build_site():
    """Build the complete static site."""
    
    # Create directories
    dist_dir = Path("dist")
    assets_dir = dist_dir / "assets"
    
    # Clean and create directories
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    assets_dir.mkdir()
    
    # Create main files
    with open(dist_dir / "index.html", "w") as f:
        f.write(create_index_html())
    
    with open(assets_dir / "styles.css", "w") as f:
        f.write(create_css())
    
    with open(assets_dir / "app.js", "w") as f:
        f.write(create_javascript())
    
    # Copy the working earthquake dashboard
    earthquake_dashboard = Path("earthquake_map.html")
    if earthquake_dashboard.exists():
        shutil.copy2(earthquake_dashboard, dist_dir / "dashboard.html")
    
    # Create a simple favicon
    with open(dist_dir / "favicon.ico", "wb") as f:
        # Simple ICO file header for a 16x16 favicon
        f.write(b'\\x00\\x00\\x01\\x00\\x01\\x00\\x10\\x10\\x00\\x00\\x01\\x00\\x20\\x00\\x68\\x04\\x00\\x00\\x16\\x00\\x00\\x00')
    
    # Create CNAME file for custom domain
    with open(dist_dir / "CNAME", "w") as f:
        f.write("seismowatch.dev")
    
    # Create 404 page
    with open(dist_dir / "404.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>404 - Page Not Found | SeismoWatch</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 4rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; display: flex; flex-direction: column; justify-content: center; }
        h1 { font-size: 4rem; margin-bottom: 1rem; }
        p { font-size: 1.2rem; margin-bottom: 2rem; }
        a { color: #ffeb3b; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <h1>404</h1>
    <p>Oops! This page seems to have shifted like tectonic plates.</p>
    <p><a href="/">← Return to SeismoWatch Home</a></p>
</body>
</html>""")
    
    print("✅ Static site built successfully!")
    print(f"📁 Output directory: {dist_dir.absolute()}")
    print("🌐 Ready for GitHub Pages deployment")

if __name__ == "__main__":
    build_site()