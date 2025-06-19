import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from myproject.cli import main

class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()
    
    def test_hello_default(self):
        result = self.runner.invoke(main, ['hello'])
        assert result.exit_code == 0
        assert 'Hello World!' in result.output
    
    def test_hello_with_name(self):
        result = self.runner.invoke(main, ['hello', '--name', 'Alice'])
        assert result.exit_code == 0
        assert 'Hello Alice!' in result.output
    
    def test_info_command(self):
        result = self.runner.invoke(main, ['info'])
        assert result.exit_code == 0
        assert 'MyProject' in result.output
        assert 'versatile Python toolkit' in result.output
    
    @patch('myproject.cli.demo_visualizations')
    def test_geo_demo_command(self, mock_demo):
        result = self.runner.invoke(main, ['geo-demo'])
        assert result.exit_code == 0
        assert 'Creating geospatial demo visualizations' in result.output
        mock_demo.assert_called_once()
    
    @patch('myproject.cli.GeoVisualizer')
    def test_geocode_command_success(self, mock_geo_viz):
        mock_instance = MagicMock()
        mock_instance.geocode_address.return_value = (40.7128, -74.0060)
        mock_geo_viz.return_value = mock_instance
        
        result = self.runner.invoke(main, ['geocode', '--address', 'Times Square'])
        assert result.exit_code == 0
        assert 'Times Square' in result.output
        assert '40.712800' in result.output
        assert '-74.006000' in result.output
    
    @patch('myproject.cli.GeoVisualizer')
    def test_geocode_command_failure(self, mock_geo_viz):
        mock_instance = MagicMock()
        mock_instance.geocode_address.return_value = None
        mock_geo_viz.return_value = mock_instance
        
        result = self.runner.invoke(main, ['geocode', '--address', 'InvalidAddress'])
        assert result.exit_code == 0
        assert 'Could not geocode' in result.output
    
    @patch('myproject.cli.GeoVisualizer')
    def test_create_map_command(self, mock_geo_viz):
        mock_instance = MagicMock()
        mock_map = MagicMock()
        mock_instance.create_basic_map.return_value = mock_map
        mock_geo_viz.return_value = mock_instance
        
        result = self.runner.invoke(main, ['create-map', '--lat', '40.7128', '--lon', '-74.0060'])
        assert result.exit_code == 0
        assert 'Map saved to map.html' in result.output
        mock_instance.create_basic_map.assert_called_once_with(40.7128, -74.0060)
        mock_map.save.assert_called_once_with('map.html')
    
    def test_create_map_custom_output(self):
        with patch('myproject.cli.GeoVisualizer') as mock_geo_viz:
            mock_instance = MagicMock()
            mock_map = MagicMock()
            mock_instance.create_basic_map.return_value = mock_map
            mock_geo_viz.return_value = mock_instance
            
            result = self.runner.invoke(main, ['create-map', '--lat', '40.7128', '--lon', '-74.0060', '--output', 'custom.html'])
            assert result.exit_code == 0
            assert 'Map saved to custom.html' in result.output
            mock_map.save.assert_called_once_with('custom.html')