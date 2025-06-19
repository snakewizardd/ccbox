import pytest
import pandas as pd
import folium
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from seismowatch.geo import GeoVisualizer, create_sample_data

class TestGeoVisualizer:
    def setup_method(self):
        self.geo_viz = GeoVisualizer()
    
    def test_create_basic_map(self):
        map_obj = self.geo_viz.create_basic_map(40.7128, -74.0060, 12)
        assert isinstance(map_obj, folium.Map)
        assert map_obj.location == [40.7128, -74.0060]
        assert map_obj.options['zoom'] == 12
    
    def test_create_basic_map_defaults(self):
        map_obj = self.geo_viz.create_basic_map()
        assert isinstance(map_obj, folium.Map)
        assert map_obj.location == [40.7128, -74.0060]
        assert map_obj.options['zoom'] == 10
    
    def test_add_markers(self):
        map_obj = folium.Map()
        locations = [
            (40.7128, -74.0060, "New York"),
            (34.0522, -118.2437, "Los Angeles")
        ]
        
        result_map = self.geo_viz.add_markers(map_obj, locations)
        assert result_map is map_obj
        # Map has default tile layer + 2 markers = 3 children
        assert len(result_map._children) == 3
    
    @patch('seismowatch.geo.Nominatim')
    def test_geocode_address_success(self, mock_nominatim):
        mock_geocoder = MagicMock()
        mock_location = MagicMock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060
        mock_geocoder.geocode.return_value = mock_location
        mock_nominatim.return_value = mock_geocoder
        
        geo_viz = GeoVisualizer()
        result = geo_viz.geocode_address("Times Square")
        
        assert result == (40.7128, -74.0060)
        mock_geocoder.geocode.assert_called_once_with("Times Square")
    
    @patch('seismowatch.geo.Nominatim')
    def test_geocode_address_failure(self, mock_nominatim):
        mock_geocoder = MagicMock()
        mock_geocoder.geocode.return_value = None
        mock_nominatim.return_value = mock_geocoder
        
        geo_viz = GeoVisualizer()
        result = geo_viz.geocode_address("InvalidAddress")
        
        assert result is None
    
    @patch('seismowatch.geo.Nominatim')
    def test_geocode_address_exception(self, mock_nominatim):
        mock_geocoder = MagicMock()
        mock_geocoder.geocode.side_effect = Exception("Network error")
        mock_nominatim.return_value = mock_geocoder
        
        geo_viz = GeoVisualizer()
        result = geo_viz.geocode_address("Address")
        
        assert result is None
    
    def test_create_scatter_mapbox(self):
        df = pd.DataFrame({
            'lat': [40.7128, 34.0522],
            'lon': [-74.0060, -118.2437],
            'city': ['NYC', 'LA'],
            'population': [8000000, 4000000]
        })
        
        fig = self.geo_viz.create_scatter_mapbox(
            df, 'lat', 'lon', 
            color_col='population', 
            title='Test Map'
        )
        
        assert fig.layout.title.text == 'Test Map'
        assert len(fig.data) == 1
    
    def test_create_heatmap_with_center(self):
        locations = [(40.7128, -74.0060), (40.7589, -73.9851)]
        
        with patch('folium.plugins.HeatMap') as mock_heatmap:
            map_obj = self.geo_viz.create_heatmap(locations, 40.7, -74.0)
            
            assert isinstance(map_obj, folium.Map)
            assert map_obj.location == [40.7, -74.0]
            mock_heatmap.assert_called_once_with(locations)
    
    def test_create_heatmap_auto_center(self):
        locations = [(40.0, -74.0), (41.0, -75.0)]
        
        with patch('folium.plugins.HeatMap') as mock_heatmap:
            map_obj = self.geo_viz.create_heatmap(locations)
            
            assert isinstance(map_obj, folium.Map)
            assert map_obj.location == [40.5, -74.5]

class TestSampleData:
    def test_create_sample_data(self):
        df = create_sample_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert 'name' in df.columns
        assert 'lat' in df.columns
        assert 'lon' in df.columns
        assert 'population' in df.columns
        assert 'value' in df.columns
        
        assert df.loc[0, 'name'] == 'New York'
        assert df.loc[0, 'lat'] == 40.7128
        assert df.loc[0, 'lon'] == -74.0060