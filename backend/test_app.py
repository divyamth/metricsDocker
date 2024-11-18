import pytest
import json
from app import app, redis_client, validate_integer_param  # Import the necessary components
import time
from unittest.mock import patch

@pytest.fixture
def client():
    return app.test_client()

def test_home(client):
    """Test the home endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Welcome to the System Metrics API'

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_livemetrics_invalid_interval(client):
    """Test the livemetrics endpoint with an invalid interval parameter."""
    response = client.get('/realmetrics?interval=invalid')

    # Ensure the status code is 400
    assert response.status_code == 400

    # Ensure the response contains the correct error message
    assert b"Invalid interval: must be a positive integer" in response.data

def test_historical_metrics(client):
    """Test the historical-metrics endpoint."""
    # Ensure the Redis list is cleared before each test
    redis_client.delete('metrics')

    # First, add some dummy data to Redis
    redis_client.lpush('metrics', json.dumps({'cpu_usage': 10}))
    redis_client.lpush('metrics', json.dumps({'cpu_usage': 20}))

    # Check the number of items in Redis
    assert redis_client.llen('metrics') == 2  # Ensure there are 2 items in the Redis list

    # Now fetch the historical metrics
    response = client.get('/historical-metrics')
    assert response.status_code == 200
    data = json.loads(response.data)

    # Assert the data in the correct order (most recent first)
    assert len(data['historical-metrics']) == 2
    assert json.loads(data['historical-metrics'][0])['cpu_usage'] == 20  # Most recent data (last pushed)
    assert json.loads(data['historical-metrics'][1])['cpu_usage'] == 10  # Second most recent data

def test_validate_integer_param():
    """Test the validate_integer_param function."""
    # Valid inputs
    assert validate_integer_param('5', 10) == 5
    assert validate_integer_param('3') == 3
    # Invalid inputs
    assert validate_integer_param('0', 10) == 10
    assert validate_integer_param('-1', 10) == 10
    assert validate_integer_param('invalid', 10) == 10