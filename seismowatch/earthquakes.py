import requests
import pandas as pd
import folium
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

class EarthquakeDataFetcher:
    """Fetches real-time earthquake data from USGS API."""
    
    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        
    def fetch_earthquakes(self, 
                         min_magnitude: float = 4.0,
                         days: int = 7,
                         limit: int = 100) -> pd.DataFrame:
        """Fetch earthquake data from USGS API."""
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        params = {
            'format': 'geojson',
            'starttime': start_time.strftime('%Y-%m-%d'),
            'endtime': end_time.strftime('%Y-%m-%d'),
            'minmagnitude': min_magnitude,
            'limit': limit,
            'orderby': 'magnitude'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            earthquakes = []
            for feature in data['features']:
                props = feature['properties']
                coords = feature['geometry']['coordinates']
                
                earthquakes.append({
                    'id': feature['id'],
                    'magnitude': props['mag'],
                    'place': props['place'],
                    'time': datetime.fromtimestamp(props['time'] / 1000),
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'depth': coords[2],
                    'url': props['url'],
                    'tsunami': props['tsunami'],
                    'felt': props.get('felt', 0),
                    'significance': props.get('sig', 0)
                })
            
            return pd.DataFrame(earthquakes)
            
        except requests.RequestException as e:
            print(f"Error fetching earthquake data: {e}")
            return pd.DataFrame()

class EarthquakeVisualizer:
    """Creates visualizations for earthquake data."""
    
    def __init__(self):
        self.magnitude_colors = {
            4.0: '#FFD700',  # Gold
            5.0: '#FF8C00',  # Orange
            6.0: '#FF4500',  # Red-Orange
            7.0: '#DC143C',  # Crimson
            8.0: '#8B0000',  # Dark Red
            9.0: '#4B0082'   # Indigo
        }
    
    def get_color_by_magnitude(self, magnitude: float) -> str:
        """Return color based on earthquake magnitude."""
        if magnitude >= 9.0:
            return self.magnitude_colors[9.0]
        elif magnitude >= 8.0:
            return self.magnitude_colors[8.0]
        elif magnitude >= 7.0:
            return self.magnitude_colors[7.0]
        elif magnitude >= 6.0:
            return self.magnitude_colors[6.0]
        elif magnitude >= 5.0:
            return self.magnitude_colors[5.0]
        else:
            return self.magnitude_colors[4.0]
    
    def get_radius_by_magnitude(self, magnitude: float) -> float:
        """Return circle radius based on magnitude."""
        return max(5, magnitude * 3)
    
    def create_earthquake_map(self, 
                            df: pd.DataFrame,
                            title: str = "Recent Earthquakes") -> folium.Map:
        """Create an interactive earthquake map."""
        
        if df.empty:
            print("No earthquake data to visualize")
            return folium.Map()
        
        # Center map on mean coordinates
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=2,
            tiles='OpenStreetMap'
        )
        
        # Add earthquake markers
        for _, quake in df.iterrows():
            color = self.get_color_by_magnitude(quake['magnitude'])
            radius = self.get_radius_by_magnitude(quake['magnitude'])
            
            popup_text = f"""
            <b>Magnitude: {quake['magnitude']}</b><br>
            Location: {quake['place']}<br>
            Time: {quake['time'].strftime('%Y-%m-%d %H:%M:%S')}<br>
            Depth: {quake['depth']:.1f} km<br>
            Significance: {quake['significance']}<br>
            {"🌊 Tsunami Warning" if quake['tsunami'] else ""}
            """
            
            folium.CircleMarker(
                location=[quake['latitude'], quake['longitude']],
                radius=radius,
                popup=folium.Popup(popup_text, max_width=300),
                color='black',
                weight=1,
                fillColor=color,
                fillOpacity=0.7,
                tooltip=f"M{quake['magnitude']} - {quake['place']}"
            ).add_to(m)
        
        # Add legend
        legend_html = self._create_legend()
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def _create_legend(self) -> str:
        """Create HTML legend for the map."""
        return """
        <div style='position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px'>
        <p><b>Earthquake Magnitude</b></p>
        <p><i class="fa fa-circle" style="color:#FFD700"></i> 4.0 - 4.9</p>
        <p><i class="fa fa-circle" style="color:#FF8C00"></i> 5.0 - 5.9</p>
        <p><i class="fa fa-circle" style="color:#FF4500"></i> 6.0 - 6.9</p>
        <p><i class="fa fa-circle" style="color:#DC143C"></i> 7.0 - 7.9</p>
        <p><i class="fa fa-circle" style="color:#8B0000"></i> 8.0 - 8.9</p>
        <p><i class="fa fa-circle" style="color:#4B0082"></i> 9.0+</p>
        </div>
        """
    
    def create_magnitude_timeline(self, df: pd.DataFrame) -> folium.Map:
        """Create a timeline visualization of earthquakes."""
        if df.empty:
            return folium.Map()
        
        # Sort by time
        df_sorted = df.sort_values('time')
        
        # Create map
        m = folium.Map(zoom_start=2)
        
        # Add time-based markers
        for i, (_, quake) in enumerate(df_sorted.iterrows()):
            color = self.get_color_by_magnitude(quake['magnitude'])
            
            # Opacity based on recency (more recent = more opaque)
            opacity = 0.3 + (i / len(df_sorted)) * 0.7
            
            folium.CircleMarker(
                location=[quake['latitude'], quake['longitude']],
                radius=self.get_radius_by_magnitude(quake['magnitude']),
                color=color,
                fillColor=color,
                fillOpacity=opacity,
                popup=f"M{quake['magnitude']} - {quake['time'].strftime('%Y-%m-%d %H:%M')}"
            ).add_to(m)
        
        return m

def create_earthquake_demo():
    """Create demonstration earthquake visualizations."""
    print("🌋 Fetching real-time earthquake data...")
    
    fetcher = EarthquakeDataFetcher()
    visualizer = EarthquakeVisualizer()
    
    # Fetch recent significant earthquakes
    df = fetcher.fetch_earthquakes(min_magnitude=4.5, days=7, limit=50)
    
    if df.empty:
        print("❌ No earthquake data available")
        return
    
    print(f"📊 Found {len(df)} earthquakes")
    print(f"🏔️  Largest: M{df['magnitude'].max():.1f}")
    print(f"📅 Date range: {df['time'].min().date()} to {df['time'].max().date()}")
    
    # Create earthquake map
    print("🗺️  Creating earthquake map...")
    eq_map = visualizer.create_earthquake_map(df, "Recent Significant Earthquakes")
    eq_map.save('earthquake_map.html')
    
    # Create timeline map
    print("⏰ Creating timeline visualization...")
    timeline_map = visualizer.create_magnitude_timeline(df)
    timeline_map.save('earthquake_timeline.html')
    
    # Print some statistics
    print("\n📈 Earthquake Statistics:")
    print(f"Average magnitude: {df['magnitude'].mean():.1f}")
    print(f"Average depth: {df['depth'].mean():.1f} km")
    print(f"Tsunami warnings: {df['tsunami'].sum()}")
    
    print("\n🎯 Files created:")
    print("- earthquake_map.html")
    print("- earthquake_timeline.html")

if __name__ == '__main__':
    create_earthquake_demo()