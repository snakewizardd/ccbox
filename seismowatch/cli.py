import click
from .geo import GeoVisualizer, create_sample_data, demo_visualizations
from .earthquakes import create_earthquake_demo, EarthquakeDataFetcher, EarthquakeVisualizer
from .alerts import create_demo_monitor, EarthquakeMonitor, AlertZone, ConsoleNotificationHandler, FileNotificationHandler
from .dashboard import create_dashboard

@click.group()
@click.version_option()
def main():
    """A versatile Python project CLI."""
    pass

@main.command()
@click.option('--name', default='World', help='Name to greet')
def hello(name):
    """Say hello to someone."""
    click.echo(f'Hello {name}!')

@main.command()
def info():
    """Show project information."""
    click.echo('MyProject - A versatile Python toolkit')
    click.echo('Ready for CLI, web, and data analysis tasks!')

@main.command()
def geo_demo():
    """Create sample geospatial visualizations."""
    click.echo('Creating geospatial demo visualizations...')
    demo_visualizations()
    click.echo('Demo complete! Check the generated HTML files.')

@main.command()
@click.option('--address', required=True, help='Address to geocode')
def geocode(address):
    """Geocode an address to coordinates."""
    geo_viz = GeoVisualizer()
    coords = geo_viz.geocode_address(address)
    if coords:
        click.echo(f'Address: {address}')
        click.echo(f'Coordinates: {coords[0]:.6f}, {coords[1]:.6f}')
    else:
        click.echo(f'Could not geocode address: {address}')

@main.command()
@click.option('--lat', type=float, required=True, help='Latitude')
@click.option('--lon', type=float, required=True, help='Longitude')
@click.option('--output', default='map.html', help='Output HTML file')
def create_map(lat, lon, output):
    """Create a simple map centered at given coordinates."""
    geo_viz = GeoVisualizer()
    map_obj = geo_viz.create_basic_map(lat, lon)
    map_obj.save(output)
    click.echo(f'Map saved to {output}')

@main.command()
def earthquakes():
    """Create real-time earthquake visualizations."""
    click.echo('🌋 Creating earthquake visualizations...')
    create_earthquake_demo()

@main.command()
@click.option('--min-mag', default=4.0, help='Minimum magnitude')
@click.option('--days', default=7, help='Days to look back')
@click.option('--limit', default=50, help='Maximum number of earthquakes')
@click.option('--output', default='custom_earthquakes.html', help='Output HTML file')
def earthquake_map(min_mag, days, limit, output):
    """Create custom earthquake map with filters."""
    click.echo(f'🌋 Fetching earthquakes M{min_mag}+ from last {days} days...')
    
    fetcher = EarthquakeDataFetcher()
    visualizer = EarthquakeVisualizer()
    
    df = fetcher.fetch_earthquakes(min_magnitude=min_mag, days=days, limit=limit)
    
    if df.empty:
        click.echo('❌ No earthquakes found with those criteria')
        return
    
    click.echo(f'📊 Found {len(df)} earthquakes')
    
    eq_map = visualizer.create_earthquake_map(df, f"Earthquakes M{min_mag}+ - Last {days} Days")
    eq_map.save(output)
    
    click.echo(f'🗺️ Map saved to {output}')
    click.echo(f'🏔️ Largest: M{df["magnitude"].max():.1f}')

@main.command()
def alert_demo():
    """Start earthquake alert monitoring demo."""
    click.echo('🚨 Starting Earthquake Alert System Demo...')
    click.echo('This will monitor for earthquakes and alert you in real-time!')
    click.echo('Configured zones: San Francisco, LA, Tokyo, Global M6.5+')
    click.echo('Press Ctrl+C to stop monitoring\n')
    
    monitor = create_demo_monitor()
    monitor.start_monitoring()

@main.command()
@click.option('--name', required=True, help='Zone name')
@click.option('--lat', type=float, required=True, help='Center latitude')
@click.option('--lon', type=float, required=True, help='Center longitude')
@click.option('--radius', type=float, default=100, help='Radius in kilometers')
@click.option('--min-mag', type=float, default=4.0, help='Minimum magnitude')
@click.option('--interval', type=int, default=60, help='Check interval in seconds')
def alert_zone(name, lat, lon, radius, min_mag, interval):
    """Create custom earthquake alert zone."""
    click.echo(f'🎯 Creating alert zone: {name}')
    click.echo(f'📍 Center: {lat:.3f}, {lon:.3f}')
    click.echo(f'📏 Radius: {radius} km')
    click.echo(f'📊 Min magnitude: M{min_mag}')
    click.echo('Press Ctrl+C to stop monitoring\n')
    
    monitor = EarthquakeMonitor(check_interval=interval)
    zone = AlertZone(name, lat, lon, radius, min_mag)
    monitor.add_alert_zone(zone)
    monitor.add_notification_handler(ConsoleNotificationHandler())
    monitor.add_notification_handler(FileNotificationHandler(f"{name.lower().replace(' ', '_')}_alerts.log"))
    
    monitor.start_monitoring()

@main.command()
def alert_test():
    """Test the alert system with recent earthquakes."""
    click.echo('🧪 Testing alert system with recent earthquake data...')
    
    monitor = EarthquakeMonitor()
    
    # Add global zone for testing
    global_zone = AlertZone("Global Test Zone", 0, 0, 50000, 4.0)
    monitor.add_alert_zone(global_zone)
    monitor.add_notification_handler(ConsoleNotificationHandler())
    
    # Clear seen earthquakes for testing
    monitor.seen_earthquakes.clear()
    
    # Run one check
    monitor.check_for_earthquakes()
    
    click.echo('✅ Alert test complete!')

@main.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--debug', is_flag=True, help='Run in debug mode')
def dashboard(host, port, debug):
    """Launch the real-time earthquake dashboard webapp."""
    click.echo('🌐 Launching Real-time Earthquake Dashboard...')
    click.echo(f'🚨 Live monitoring with WebSocket updates!')
    click.echo(f'📡 Access at: http://{host}:{port}')
    click.echo('🔴 LIVE earthquake alerts will appear in real-time!')
    
    dashboard = create_dashboard()
    dashboard.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()