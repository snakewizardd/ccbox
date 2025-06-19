import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from myproject.web import create_app

class TestWebApp:
    def setup_method(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_home_route(self):
        response = self.client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Welcome to MyProject!' in data['message']
        assert 'version' in data
        assert data['version'] == '0.1.0'
        assert 'endpoints' in data
        assert isinstance(data['endpoints'], list)
    
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
        assert 'Data Analysis' in data['capabilities']
    
    def test_health_route(self):
        response = self.client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_nonexistent_route(self):
        response = self.client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_response_content_type(self):
        response = self.client.get('/')
        assert response.content_type == 'application/json'
        
        response = self.client.get('/api/info')
        assert response.content_type == 'application/json'
        
        response = self.client.get('/api/health')
        assert response.content_type == 'application/json'