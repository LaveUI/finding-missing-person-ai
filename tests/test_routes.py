from flask import Flask, jsonify
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the Missing Person AI' in response.data

def test_api_endpoint(client):
    response = client.get('/api/v1/missing-persons')
    assert response.status_code == 200
    assert isinstance(response.json, list)  # Assuming the endpoint returns a list of missing persons

def test_non_existent_route(client):
    response = client.get('/non-existent-route')
    assert response.status_code == 404