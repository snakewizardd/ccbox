"""
SeismoWatch: Real-time Earthquake Monitoring Platform

A comprehensive earthquake monitoring system that provides:
- Real-time earthquake data from USGS
- Interactive visualizations and maps  
- Intelligent alerting system
- RESTful API for earthquake data
- Command-line tools for analysis
"""

__version__ = "1.0.0"
__author__ = "SeismoWatch Contributors"
__license__ = "MIT"

# Main exports
from .earthquakes import EarthquakeDataFetcher, EarthquakeVisualizer
from .alerts import EarthquakeMonitor, AlertZone
from .geo import GeoVisualizer

__all__ = [
    'EarthquakeDataFetcher',
    'EarthquakeVisualizer', 
    'EarthquakeMonitor',
    'AlertZone',
    'GeoVisualizer'
]