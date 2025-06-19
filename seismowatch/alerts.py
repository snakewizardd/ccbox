import time
import json
import smtplib
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path

from .earthquakes import EarthquakeDataFetcher

@dataclass
class AlertZone:
    """Defines a geographic zone for earthquake alerts."""
    name: str
    center_lat: float
    center_lon: float
    radius_km: float
    min_magnitude: float
    
    def contains_earthquake(self, lat: float, lon: float, magnitude: float) -> bool:
        """Check if earthquake is within this alert zone."""
        if magnitude < self.min_magnitude:
            return False
        
        # Simple distance calculation (good enough for alerts)
        from math import sqrt, pow
        lat_diff = abs(self.center_lat - lat)
        lon_diff = abs(self.center_lon - lon)
        
        # Rough conversion: 1 degree ≈ 111 km
        distance_km = sqrt(pow(lat_diff * 111, 2) + pow(lon_diff * 111, 2))
        
        return distance_km <= self.radius_km

@dataclass
class EarthquakeAlert:
    """Represents an earthquake alert."""
    earthquake_id: str
    magnitude: float
    location: str
    latitude: float
    longitude: float
    depth: float
    time: datetime
    zone_name: str
    alert_time: datetime
    tsunami_warning: bool = False

class NotificationHandler:
    """Base class for alert notifications."""
    
    def send_alert(self, alert: EarthquakeAlert) -> bool:
        """Send alert notification. Return True if successful."""
        raise NotImplementedError

class ConsoleNotificationHandler(NotificationHandler):
    """Prints alerts to console with dramatic formatting."""
    
    def send_alert(self, alert: EarthquakeAlert) -> bool:
        tsunami_warning = "🌊 TSUNAMI WARNING!" if alert.tsunami_warning else ""
        
        print("\n" + "="*80)
        print(f"🚨 EARTHQUAKE ALERT! 🚨")
        print(f"📍 Zone: {alert.zone_name}")
        print(f"📊 Magnitude: {alert.magnitude}")
        print(f"🌍 Location: {alert.location}")
        print(f"⏰ Time: {alert.time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"📏 Depth: {alert.depth:.1f} km")
        print(f"📍 Coordinates: {alert.latitude:.3f}, {alert.longitude:.3f}")
        if tsunami_warning:
            print(f"⚠️  {tsunami_warning}")
        print("="*80 + "\n")
        
        return True

class FileNotificationHandler(NotificationHandler):
    """Saves alerts to a log file."""
    
    def __init__(self, log_file: str = "earthquake_alerts.log"):
        self.log_file = log_file
    
    def send_alert(self, alert: EarthquakeAlert) -> bool:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] M{alert.magnitude} earthquake in {alert.location} " \
                       f"({alert.latitude:.3f}, {alert.longitude:.3f}) - Zone: {alert.zone_name}\n"
            
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
            return True
        except Exception as e:
            print(f"Failed to write alert to file: {e}")
            return False

class EmailNotificationHandler(NotificationHandler):
    """Sends email alerts (requires SMTP configuration)."""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, 
                 password: str, recipients: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients
    
    def send_alert(self, alert: EarthquakeAlert) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = f"🚨 EARTHQUAKE ALERT: M{alert.magnitude} - {alert.location}"
            
            tsunami_text = "\n⚠️ TSUNAMI WARNING ISSUED!" if alert.tsunami_warning else ""
            
            body = f"""
🚨 EARTHQUAKE DETECTED! 🚨

📊 Magnitude: {alert.magnitude}
🌍 Location: {alert.location}
⏰ Time: {alert.time.strftime('%Y-%m-%d %H:%M:%S UTC')}
📏 Depth: {alert.depth:.1f} km
📍 Coordinates: {alert.latitude:.3f}, {alert.longitude:.3f}
🎯 Alert Zone: {alert.zone_name}{tsunami_text}

This is an automated alert from your Earthquake Monitoring System.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False

class EarthquakeMonitor:
    """Real-time earthquake monitoring and alerting system."""
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval  # seconds
        self.alert_zones: List[AlertZone] = []
        self.notification_handlers: List[NotificationHandler] = []
        self.seen_earthquakes: set = set()
        self.last_check: Optional[datetime] = None
        self.running = False
        self.fetcher = EarthquakeDataFetcher()
        self.data_file = "alert_data.json"
        
        # Load previous state
        self._load_state()
    
    def add_alert_zone(self, zone: AlertZone):
        """Add a new alert zone."""
        self.alert_zones.append(zone)
        self._save_state()
    
    def add_notification_handler(self, handler: NotificationHandler):
        """Add a notification handler."""
        self.notification_handlers.append(handler)
    
    def _load_state(self):
        """Load previous monitoring state."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.seen_earthquakes = set(data.get('seen_earthquakes', []))
                    if data.get('last_check'):
                        self.last_check = datetime.fromisoformat(data['last_check'])
        except Exception as e:
            print(f"Warning: Could not load previous state: {e}")
    
    def _save_state(self):
        """Save current monitoring state."""
        try:
            data = {
                'seen_earthquakes': list(self.seen_earthquakes),
                'last_check': self.last_check.isoformat() if self.last_check else None
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Warning: Could not save state: {e}")
    
    def check_for_earthquakes(self):
        """Check for new earthquakes and send alerts."""
        try:
            # Fetch recent earthquakes
            df = self.fetcher.fetch_earthquakes(
                min_magnitude=3.0,  # Lower threshold for monitoring
                days=1,  # Only check last day
                limit=200
            )
            
            if df.empty:
                return
            
            new_alerts = []
            
            for _, earthquake in df.iterrows():
                eq_id = earthquake['id']
                
                # Skip if we've already processed this earthquake
                if eq_id in self.seen_earthquakes:
                    continue
                
                # Check if earthquake matches any alert zone
                for zone in self.alert_zones:
                    if zone.contains_earthquake(
                        earthquake['latitude'], 
                        earthquake['longitude'], 
                        earthquake['magnitude']
                    ):
                        alert = EarthquakeAlert(
                            earthquake_id=eq_id,
                            magnitude=earthquake['magnitude'],
                            location=earthquake['place'],
                            latitude=earthquake['latitude'],
                            longitude=earthquake['longitude'],
                            depth=earthquake['depth'],
                            time=earthquake['time'],
                            zone_name=zone.name,
                            alert_time=datetime.now(),
                            tsunami_warning=earthquake['tsunami']
                        )
                        new_alerts.append(alert)
                        break  # Only alert once per earthquake
                
                # Mark as seen
                self.seen_earthquakes.add(eq_id)
            
            # Send notifications for new alerts
            for alert in new_alerts:
                for handler in self.notification_handlers:
                    try:
                        handler.send_alert(alert)
                    except Exception as e:
                        print(f"Notification handler failed: {e}")
            
            self.last_check = datetime.now()
            self._save_state()
            
            if new_alerts:
                print(f"🚨 Sent {len(new_alerts)} earthquake alerts!")
            else:
                print(f"✅ Monitoring check complete - no new alerts")
                
        except Exception as e:
            print(f"Error during earthquake check: {e}")
    
    def start_monitoring(self):
        """Start continuous earthquake monitoring."""
        if self.running:
            print("Monitoring is already running!")
            return
        
        if not self.alert_zones:
            print("❌ No alert zones configured! Add zones before starting.")
            return
        
        if not self.notification_handlers:
            print("❌ No notification handlers configured!")
            return
        
        self.running = True
        print(f"🔍 Starting earthquake monitoring...")
        print(f"📊 Monitoring {len(self.alert_zones)} zones")
        print(f"🔔 Check interval: {self.check_interval} seconds")
        print("Press Ctrl+C to stop monitoring\n")
        
        def monitor_loop():
            while self.running:
                try:
                    self.check_for_earthquakes()
                    time.sleep(self.check_interval)
                except KeyboardInterrupt:
                    self.stop_monitoring()
                    break
                except Exception as e:
                    print(f"Error in monitoring loop: {e}")
                    time.sleep(self.check_interval)
        
        # Run in separate thread for CLI responsiveness
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        try:
            monitor_thread.join()
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop earthquake monitoring."""
        self.running = False
        print("\n🛑 Earthquake monitoring stopped.")
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring status."""
        return {
            'running': self.running,
            'zones': len(self.alert_zones),
            'handlers': len(self.notification_handlers),
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'seen_earthquakes': len(self.seen_earthquakes)
        }

def create_demo_monitor():
    """Create a demo earthquake monitor with sample zones."""
    monitor = EarthquakeMonitor(check_interval=30)  # Check every 30 seconds
    
    # Add some interesting alert zones
    zones = [
        AlertZone("San Francisco Bay Area", 37.7749, -122.4194, 100, 4.0),
        AlertZone("Los Angeles Region", 34.0522, -118.2437, 150, 4.5),
        AlertZone("Tokyo Metropolitan", 35.6762, 139.6503, 80, 5.0),
        AlertZone("Global Major Events", 0, 0, 50000, 6.5),  # Worldwide M6.5+
    ]
    
    for zone in zones:
        monitor.add_alert_zone(zone)
    
    # Add notification handlers
    monitor.add_notification_handler(ConsoleNotificationHandler())
    monitor.add_notification_handler(FileNotificationHandler("earthquake_alerts.log"))
    
    return monitor

if __name__ == '__main__':
    # Demo the alert system
    monitor = create_demo_monitor()
    print("🚨 Demo Earthquake Alert System")
    print("This will monitor for earthquakes and alert you!")
    monitor.start_monitoring()