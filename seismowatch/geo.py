import folium
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from typing import List, Tuple, Optional
import contextily as ctx
import matplotlib.pyplot as plt

class GeoVisualizer:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="myproject-geo")
    
    def create_basic_map(self, center_lat: float = 40.7128, center_lon: float = -74.0060, zoom: int = 10) -> folium.Map:
        """Create a basic folium map centered at given coordinates."""
        return folium.Map(location=[center_lat, center_lon], zoom_start=zoom)
    
    def add_markers(self, map_obj: folium.Map, locations: List[Tuple[float, float, str]]) -> folium.Map:
        """Add markers to a folium map.
        
        Args:
            map_obj: Folium map object
            locations: List of (lat, lon, popup_text) tuples
        """
        for lat, lon, popup in locations:
            folium.Marker([lat, lon], popup=popup).add_to(map_obj)
        return map_obj
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode an address to lat/lon coordinates."""
        try:
            location = self.geocoder.geocode(address)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            print(f"Geocoding error: {e}")
        return None
    
    def create_scatter_mapbox(self, df: pd.DataFrame, lat_col: str, lon_col: str, 
                             color_col: Optional[str] = None, size_col: Optional[str] = None,
                             title: str = "Scatter Map") -> go.Figure:
        """Create an interactive scatter plot on a map using Plotly."""
        fig = px.scatter_mapbox(
            df, lat=lat_col, lon=lon_col,
            color=color_col, size=size_col,
            hover_data=df.columns,
            mapbox_style="open-street-map",
            title=title,
            zoom=10
        )
        fig.update_layout(mapbox_style="open-street-map")
        return fig
    
    def create_choropleth_map(self, gdf: gpd.GeoDataFrame, value_col: str, 
                             title: str = "Choropleth Map") -> folium.Map:
        """Create a choropleth map from a GeoDataFrame."""
        center_lat = gdf.geometry.centroid.y.mean()
        center_lon = gdf.geometry.centroid.x.mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        folium.Choropleth(
            geo_data=gdf.to_json(),
            data=gdf,
            columns=[gdf.index, value_col],
            key_on="feature.id",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=value_col
        ).add_to(m)
        
        return m
    
    def create_heatmap(self, locations: List[Tuple[float, float]], 
                      center_lat: float = None, center_lon: float = None) -> folium.Map:
        """Create a heatmap from location data."""
        from folium.plugins import HeatMap
        
        if center_lat is None or center_lon is None:
            center_lat = sum(loc[0] for loc in locations) / len(locations)
            center_lon = sum(loc[1] for loc in locations) / len(locations)
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        HeatMap(locations).add_to(m)
        return m

def create_sample_data() -> pd.DataFrame:
    """Create sample geospatial data for testing."""
    data = {
        'name': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
        'lat': [40.7128, 34.0522, 41.8781, 29.7604, 33.4484],
        'lon': [-74.0060, -118.2437, -87.6298, -95.3698, -112.0740],
        'population': [8336817, 3979576, 2693976, 2320268, 1680992],
        'value': [100, 85, 70, 60, 45]
    }
    return pd.DataFrame(data)

def demo_visualizations():
    """Create demonstration visualizations."""
    geo_viz = GeoVisualizer()
    sample_df = create_sample_data()
    
    # Basic map with markers
    basic_map = geo_viz.create_basic_map()
    locations = [(row.lat, row.lon, row['name']) for _, row in sample_df.iterrows()]
    geo_viz.add_markers(basic_map, locations)
    basic_map.save('basic_map.html')
    
    # Interactive scatter map
    scatter_fig = geo_viz.create_scatter_mapbox(
        sample_df, 'lat', 'lon', 
        color_col='population', size_col='value',
        title='US Cities by Population'
    )
    scatter_fig.write_html('scatter_map.html')
    
    # Heatmap
    heat_locations = [(row.lat, row.lon) for _, row in sample_df.iterrows()]
    heatmap = geo_viz.create_heatmap(heat_locations)
    heatmap.save('heatmap.html')
    
    print("Demo visualizations created:")
    print("- basic_map.html")
    print("- scatter_map.html") 
    print("- heatmap.html")

if __name__ == '__main__':
    demo_visualizations()