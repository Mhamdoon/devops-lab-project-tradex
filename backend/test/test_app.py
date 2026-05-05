import pytest
from unittest.mock import patch, MagicMock
import json

# Import the Flask app from your backend folder
from backend.app import app

@pytest.fixture
def client():
    """Sets up a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# --- 1. Test Health Endpoint ---
@patch('backend.app.client.admin.command')  # Changed from 'app.client.admin.command'
def test_health_check(mock_ping, client):
    # Mock the database ping to return True
    mock_ping.return_value = True 
    response = client.get('/api/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == "online"
    assert data['database'] == "connected"

# --- 2. Test Prices Endpoint ---
@patch('backend.app.requests.get')  # Changed from 'app.requests.get'
def test_get_prices(mock_get, client):
    # Mock the Binance API response so we don't need real internet
    mock_response = MagicMock()
    mock_response.json.return_value = {'price': '50000.00'}
    mock_get.return_value = mock_response

    response = client.get('/api/prices')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'BTC/USDT' in data
    assert 'ETH/USDT' in data
    assert 'XAU/USD' in data

# --- 3. Test Watchlist Endpoints ---
@patch('backend.app.watchlist_collection.insert_one')  # Changed from 'app.watchlist_collection.insert_one'
def test_add_to_watchlist(mock_insert, client):
    payload = {"symbol": "TSLA"}
    response = client.post('/api/watchlist', json=payload)
    
    assert response.status_code == 201
    assert json.loads(response.data)['symbol'] == "TSLA"
    mock_insert.assert_called_once() # Verify it tried to save to DB

def test_add_to_watchlist_missing_symbol(client):
    response = client.post('/api/watchlist', json={})
    assert response.status_code == 400

@patch('backend.app.watchlist_collection.find')  # Changed from 'app.watchlist_collection.find'
def test_get_watchlist(mock_find, client):
    # Fake database return data
    mock_find.return_value = [{"id": "123", "symbol": "AAPL", "added_at": "2026-05-05"}]
    
    response = client.get('/api/watchlist')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1

@patch('backend.app.watchlist_collection.delete_one')  # Changed from 'app.watchlist_collection.delete_one'
def test_remove_from_watchlist(mock_delete, client):
    response = client.delete('/api/watchlist/123')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == "Removed"
    mock_delete.assert_called_once_with({"id": "123"})

# --- 4. Test Journal Endpoints ---
@patch('backend.app.journal_collection.insert_one')  # Changed from 'app.journal_collection.insert_one'
def test_add_to_journal(mock_insert, client):
    payload = {"title": "Good Trade", "content": "Bought the dip"}
    response = client.post('/api/journal', json=payload)
    
    assert response.status_code == 201
    assert json.loads(response.data)['title'] == "Good Trade"
    mock_insert.assert_called_once()

@patch('backend.app.journal_collection.find')  # Changed from 'app.journal_collection.find'
def test_get_journal(mock_find, client):
    # We have to mock the .sort() method chained onto .find()
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = [{"id": "abc", "title": "Good Trade", "content": "Bought the dip"}]
    mock_find.return_value = mock_cursor

    response = client.get('/api/journal')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1