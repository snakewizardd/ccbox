import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from seismowatch.web import create_app

class TestWebApp:
    def setup_method(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_home_route(self):
        response = self.client.get('/')
        assert response.status_code == 200
        
        # Home route now returns HTML dashboard
        assert 'text/html' in response.content_type
        html_content = response.data.decode('utf-8')
        assert 'Earthquake Dashboard' in html_content
        assert 'SeismoWatch' in html_content or 'earthquake' in html_content.lower()
    
    def test_info_route(self):
        response = self.client.get('/api/info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['project'] == 'MyProject'
        assert 'description' in data
        assert 'capabilities' in data
        assert isinstance(data['capabilities'], list)
        assert 'CLI' in data['capabilities']
        assert 'Web API' in data['capabilities']
        assert 'Earthquake Monitoring' in data['capabilities']
    
    def test_health_route(self):
        response = self.client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_nonexistent_route(self):
        response = self.client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_response_content_type(self):
        # Home route returns HTML
        response = self.client.get('/')
        assert 'text/html' in response.content_type
        
        # API routes return JSON
        response = self.client.get('/api/info')
        assert response.content_type == 'application/json'
        
        response = self.client.get('/api/health')
        assert response.content_type == 'application/json'
    
    def test_earthquakes_api(self):
        response = self.client.get('/api/earthquakes')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'earthquakes' in data
        assert 'count' in data
        assert isinstance(data['earthquakes'], list)