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
@patch('backend.app.client.admin.command')  # Mock the MongoDB client's ping
def test_health_check(mock_ping, client):
    # Mock the database ping to return True without connecting
    mock_ping.return_value = {'ok': 1}
    
    response = client.get('/api/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == "online"
    assert data['database'] == "connected"

# --- 2. Test Prices Endpoint ---
@patch('backend.app.requests.get')
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
@patch('backend.app.watchlist_collection')  # Mock the watchlist collection directly
def test_add_to_watchlist(mock_watchlist, client):
    payload = {"symbol": "TSLA"}
    
    response = client.post('/api/watchlist', json=payload)
    
    assert response.status_code == 201
    assert json.loads(response.data)['symbol'] == "TSLA"
    mock_watchlist.insert_one.assert_called_once()

def test_add_to_watchlist_missing_symbol(client):
    response = client.post('/api/watchlist', json={})
    assert response.status_code == 400

@patch('backend.app.watchlist_collection')  # Mock the watchlist collection directly
def test_get_watchlist(mock_watchlist, client):
    # Fake database return data
    mock_watchlist.find.return_value = [{"id": "123", "symbol": "AAPL", "added_at": "2026-05-05"}]
    
    response = client.get('/api/watchlist')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1
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
@patch('backend.app.client')  # Mock the MongoDB client
def test_health_check(mock_db_client, client):
    # Mock the database ping to return True without connecting
    mock_db_client.admin.command.return_value = {'ok': 1}
    
    response = client.get('/api/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == "online"
    assert data['database'] == "connected"

# --- 2. Test Prices Endpoint ---
@patch('backend.app.requests.get')
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
@patch('backend.app.db')  # Mock the database object
def test_add_to_watchlist(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.watchlist = mock_collection
    
    payload = {"symbol": "TSLA"}
    response = client.post('/api/watchlist', json=payload)
    
    assert response.status_import pytest
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
@patch('backend.app.client')  # Mock the MongoDB client
def test_health_check(mock_db_client, client):
    # Mock the database ping to return True without connecting
    mock_db_client.admin.command.return_value = {'ok': 1}
    
    response = client.get('/api/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == "online"
    assert data['database'] == "connected"

# --- 2. Test Prices Endpoint ---
@patch('backend.app.requests.get')
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
@patch('backend.app.db')  # Mock the database object
def test_add_to_watchlist(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.watchlist = mock_collection
    
    payload = {"symbol": "TSLA"}
    response = client.post('/api/watchlist', json=payload)
    
    assert response.status_code == 201
    assert json.loads(response.data)['symbol'] == "TSLA"
    mock_collection.insert_one.assert_called_once()

def test_add_to_watchlist_missing_symbol(client):
    response = client.post('/api/watchlist', json={})
    assert response.status_code == 400

@patch('backend.app.db')
def test_get_watchlist(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.watchlist = mock_collection
    # Fake database return data
    mock_collection.find.return_value = [{"id": "123", "symbol": "AAPL", "added_at": "2026-05-05"}]
    
    response = client.get('/api/watchlist')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1

@patch('backend.app.db')
def test_remove_from_watchlist(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.watchlist = mock_collection
    
    response = client.delete('/api/watchlist/123')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == "Removed"
    mock_collection.delete_one.assert_called_once_with({"id": "123"})

# --- 4. Test Journal Endpoints ---
@patch('backend.app.db')
def test_add_to_journal(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.journal = mock_collection
    
    payload = {"title": "Good Trade", "content": "Bought the dip"}
    response = client.post('/api/journal', json=payload)
    
    assert response.status_code == 201
    assert json.loads(response.data)['title'] == "Good Trade"
    mock_collection.insert_one.assert_called_once()
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
@patch('backend.app.client')  # Mock the MongoDB client
def test_health_check(mock_db_client, client):
    # Mock the database ping to return True without connecting
    mock_db_client.admin.command.return_value = {'ok': 1}
    
    response = client.get('/api/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == "online"
    assert data['database'] == "connected"

# --- 2. Test Prices Endpoint ---
@patch('backend.app.requests.get')
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
@patch('backend.app.db')  # Mock the database object
def test_add_to_watchlist(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.watchlist = mock_collection
    
    payload = {"symbol": "TSLA"}
    response = client.post('/api/watchlist', json=payload)
    
    assert response.status_code == 201
    assert json.loads(response.data)['symbol'] == "TSLA"
    mock_collection.insert_one.assert_called_once()

def test_add_to_watchlist_missing_symbol(client):
    response = client.post('/api/watchlist', json={})
    assert response.status_code == 400

@patch('backend.app.db')
def test_get_watchlist(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.watchlist = mock_collection
    # Fake database return data
    mock_collection.find.return_value = [{"id": "123", "symbol": "AAPL", "added_at": "2026-05-05"}]
    
    response = client.get('/api/watchlist')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1

@patch('backend.app.db')
def test_remove_from_watchlist(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.watchlist = mock_collection
    
    response = client.delete('/api/watchlist/123')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == "Removed"
    mock_collection.delete_one.assert_called_once_with({"id": "123"})

# --- 4. Test Journal Endpoints ---
@patch('backend.app.db')
def test_add_to_journal(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.journal = mock_collection
    
    payload = {"title": "Good Trade", "content": "Bought the dip"}
    response = client.post('/api/journal', json=payload)
    
    assert response.status_code == 201
    assert json.loads(response.data)['title'] == "Good Trade"
    mock_collection.insert_one.assert_called_once()

@patch('backend.app.db')
def test_get_journal(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.journal = mock_collection
    # We have to mock the .sort() method chained onto .find()
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = [{"id": "abc", "title": "Good Trade", "content": "Bought the dip"}]
    mock_collection.find.return_value = mock_cursor

    response = client.get('/api/journal')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1
@patch('backend.app.db')
def test_get_journal(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.journal = mock_collection
    # We have to mock the .sort() method chained onto .find()
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = [{"id": "abc", "title": "Good Trade", "content": "Bought the dip"}]
    mock_collection.find.return_value = mock_cursor

    response = client.get('/api/journal')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1code == 201
    assert json.loads(response.data)['symbol'] == "TSLA"
    mock_collection.insert_one.assert_called_once()

def test_add_to_watchlist_missing_symbol(client):
    response = client.post('/api/watchlist', json={})
    assert response.status_code == 400

@patch('backend.app.db')
def test_get_watchlist(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.watchlist = mock_collection
    # Fake database return data
    mock_collection.find.return_value = [{"id": "123", "symbol": "AAPL", "added_at": "2026-05-05"}]
    
    response = client.get('/api/watchlist')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1

@patch('backend.app.db')
def test_remove_from_watchlist(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.watchlist = mock_collection
    
    response = client.delete('/api/watchlist/123')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == "Removed"
    mock_collection.delete_one.assert_called_once_with({"id": "123"})

# --- 4. Test Journal Endpoints ---
@patch('backend.app.db')
def test_add_to_journal(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.journal = mock_collection
    
    payload = {"title": "Good Trade", "content": "Bought the dip"}
    response = client.post('/api/journal', json=payload)
    
    assert response.status_code == 201
    assert json.loads(response.data)['title'] == "Good Trade"
    mock_collection.insert_one.assert_called_once()

@patch('backend.app.db')
def test_get_journal(mock_db, client):
    # Create mock collection
    mock_collection = MagicMock()
    mock_db.journal = mock_collection
    # We have to mock the .sort() method chained onto .find()
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = [{"id": "abc", "title": "Good Trade", "content": "Bought the dip"}]
    mock_collection.find.return_value = mock_cursor

    response = client.get('/api/journal')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1
@patch('backend.app.watchlist_collection')  # Mock the watchlist collection directly
def test_remove_from_watchlist(mock_watchlist, client):
    response = client.delete('/api/watchlist/123')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == "Removed"
    mock_watchlist.delete_one.assert_called_once_with({"id": "123"})

# --- 4. Test Journal Endpoints ---
# Check what the actual collection name is in your app.py
# It might be 'journal_collection', 'journals_collection', or 'trade_journal_collection'
@patch('backend.app.journal_collection')  # Try this first
def test_add_to_journal(mock_journal, client):
    payload = {"title": "Good Trade", "content": "Bought the dip"}
    response = client.post('/api/journal', json=payload)
    
    assert response.status_code == 201
    assert json.loads(response.data)['title'] == "Good Trade"
    mock_journal.insert_one.assert_called_once()

@patch('backend.app.journal_collection')  # Try this first
def test_get_journal(mock_journal, client):
    # We have to mock the .sort() method chained onto .find()
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = [{"id": "abc", "title": "Good Trade", "content": "Bought the dip"}]
    mock_journal.find.return_value = mock_cursor

    response = client.get('/api/journal')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == 1