import pytest
import json
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Import the Flask app
from app import app, client, db

# Use mongomock for testing without real MongoDB
import mongomock

@pytest.fixture
def test_client():
    """Create a test client with mocked MongoDB"""
    # Configure app for testing
    app.config['TESTING'] = True
    
    # Create a mock MongoDB client
    mock_client = mongomock.MongoClient()
    mock_db = mock_client.get_database()
    
    # Store original collection and replace with mock
    original_collection = app.watchlist_collection
    app.watchlist_collection = mock_db.watchlist
    
    with app.test_client() as client:
        yield client
    
    # Restore original collection
    app.watchlist_collection = original_collection

@pytest.fixture
def sample_watchlist_item():
    """Create a sample watchlist item for testing"""
    return {
        "symbol": "BTC/USDT",
        "id": "test-id-123",
        "added_at": datetime.utcnow().isoformat()
    }

def test_health_check(test_client):
    """Test the health check endpoint"""
    response = test_client.get('/api/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'online'
    assert data['system'] == 'Zenith Quantum Terminal'
    assert 'timestamp' in data
    assert 'database' in data

def test_get_prices(test_client):
    """Test the prices endpoint returns all expected data"""
    response = test_client.get('/api/prices')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    
    # Check all expected symbols are present
    expected_symbols = ['BTC/USDT', 'ETH/USDT', 'XAU/USD', 'EUR/USD']
    for symbol in expected_symbols:
        assert symbol in data
    
    # Check price structure
    for symbol, price_data in data.items():
        assert 'price' in price_data
        assert 'change' in price_data
        assert isinstance(price_data['price'], (int, float))
        assert isinstance(price_data['change'], str)
        
        # Price should be positive
        assert price_data['price'] > 0

def test_prices_data_types(test_client):
    """Test that prices return correct data types"""
    response = test_client.get('/api/prices')
    data = json.loads(response.data)
    
    # BTC and ETH should be floats (crypto)
    assert isinstance(data['BTC/USDT']['price'], float)
    assert isinstance(data['ETH/USDT']['price'], float)
    
    # XAU and EUR should also be floats
    assert isinstance(data['XAU/USD']['price'], float)
    assert isinstance(data['EUR/USD']['price'], float)

def test_prices_change_format(test_client):
    """Test that price changes are in percentage format"""
    response = test_client.get('/api/prices')
    data = json.loads(response.data)
    
    for symbol, price_data in data.items():
        change = price_data['change']
        # Should contain % sign
        assert '%' in change
        # Should have + or - sign
        assert change[0] in ['+', '-']

def test_create_watchlist_item(test_client):
    """Test adding a new item to watchlist"""
    new_item = {"symbol": "ETH/USDT"}
    
    response = test_client.post('/api/watchlist',
                                data=json.dumps(new_item),
                                content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    
    assert data['symbol'] == "ETH/USDT"
    assert 'id' in data
    assert 'added_at' in data
    
    # Verify ID is a valid UUID format (36 characters including hyphens)
    assert len(data['id']) == 36

def test_create_watchlist_missing_symbol(test_client):
    """Test creating watchlist item without symbol returns error"""
    # Empty data
    response = test_client.post('/api/watchlist',
                                data=json.dumps({}),
                                content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == "Symbol required"
    
    # Missing symbol field
    response = test_client.post('/api/watchlist',
                                data=json.dumps({"wrong_field": "BTC"}),
                                content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_create_watchlist_empty_body(test_client):
    """Test creating watchlist item with empty request body"""
    response = test_client.post('/api/watchlist',
                                data=json.dumps(None),
                                content_type='application/json')
    assert response.status_code == 400

def test_get_watchlist_empty(test_client):
    """Test retrieving watchlist when empty"""
    response = test_client.get('/api/watchlist')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_watchlist_with_items(test_client):
    """Test retrieving watchlist after adding items"""
    # Add two items
    item1 = {"symbol": "BTC/USDT"}
    item2 = {"symbol": "ETH/USDT"}
    
    test_client.post('/api/watchlist',
                     data=json.dumps(item1),
                     content_type='application/json')
    test_client.post('/api/watchlist',
                     data=json.dumps(item2),
                     content_type='application/json')
    
    # Retrieve watchlist
    response = test_client.get('/api/watchlist')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 2
    
    # Verify symbols
    symbols = [item['symbol'] for item in data]
    assert 'BTC/USDT' in symbols
    assert 'ETH/USDT' in symbols

def test_delete_watchlist_item(test_client):
    """Test deleting an item from watchlist"""
    # First create an item
    new_item = {"symbol": "XAU/USD"}
    post_response = test_client.post('/api/watchlist',
                                     data=json.dumps(new_item),
                                     content_type='application/json')
    created_item = json.loads(post_response.data)
    item_id = created_item['id']
    
    # Delete the item
    delete_response = test_client.delete(f'/api/watchlist/{item_id}')
    assert delete_response.status_code == 200
    delete_data = json.loads(delete_response.data)
    assert delete_data['message'] == "Removed"
    
    # Verify item is gone
    get_response = test_client.get('/api/watchlist')
    watchlist = json.loads(get_response.data)
    assert not any(item['id'] == item_id for item in watchlist)

def test_delete_nonexistent_watchlist_item(test_client):
    """Test deleting an item that doesn't exist (should still work)"""
    response = test_client.delete('/api/watchlist/nonexistent-id-123')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['message'] == "Removed"

def test_watchlist_crud_flow(test_client):
    """Test complete CRUD flow for watchlist"""
    # 1. Create
    item = {"symbol": "EUR/USD"}
    create_response = test_client.post('/api/watchlist',
                                       data=json.dumps(item),
                                       content_type='application/json')
    assert create_response.status_code == 201
    created_item = json.loads(create_response.data)
    item_id = created_item['id']
    
    # 2. Read - verify it's in watchlist
    read_response = test_client.get('/api/watchlist')
    watchlist = json.loads(read_response.data)
    found_item = next((i for i in watchlist if i['id'] == item_id), None)
    assert found_item is not None
    assert found_item['symbol'] == "EUR/USD"
    
    # 3. Delete
    delete_response = test_client.delete(f'/api/watchlist/{item_id}')
    assert delete_response.status_code == 200
    
    # 4. Verify deletion
    final_response = test_client.get('/api/watchlist')
    final_watchlist = json.loads(final_response.data)
    assert not any(i['id'] == item_id for i in final_watchlist)

def test_watchlist_item_structure(test_client):
    """Test that watchlist items have correct structure"""
    new_item = {"symbol": "BTC/USDT"}
    response = test_client.post('/api/watchlist',
                                data=json.dumps(new_item),
                                content_type='application/json')
    
    data = json.loads(response.data)
    
    # Check all required fields
    assert 'id' in data
    assert 'symbol' in data
    assert 'added_at' in data
    
    # Check field types
    assert isinstance(data['id'], str)
    assert isinstance(data['symbol'], str)
    assert isinstance(data['added_at'], str)
    
    # Check added_at is ISO format
    try:
        datetime.fromisoformat(data['added_at'].replace('Z', '+00:00'))
        valid_date = True
    except:
        valid_date = False
    assert valid_date

def test_multiple_watchlist_items(test_client):
    """Test adding multiple items to watchlist"""
    symbols = ['BTC/USDT', 'ETH/USDT', 'XAU/USD', 'EUR/USD']
    
    # Add all symbols
    for symbol in symbols:
        response = test_client.post('/api/watchlist',
                                    data=json.dumps({"symbol": symbol}),
                                    content_type='application/json')
        assert response.status_code == 201
    
    # Retrieve and verify all are present
    response = test_client.get('/api/watchlist')
    watchlist = json.loads(response.data)
    
    assert len(watchlist) == len(symbols)
    retrieved_symbols = [item['symbol'] for item in watchlist]
    
    for symbol in symbols:
        assert symbol in retrieved_symbols

def test_watchlist_idempotency(test_client):
    """Test that adding same symbol multiple times creates separate entries"""
    symbol = "BTC/USDT"
    
    # Add same symbol twice
    response1 = test_client.post('/api/watchlist',
                                 data=json.dumps({"symbol": symbol}),
                                 content_type='application/json')
    response2 = test_client.post('/api/watchlist',
                                 data=json.dumps({"symbol": symbol}),
                                 content_type='application/json')
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    
    # Both should be in watchlist
    get_response = test_client.get('/api/watchlist')
    watchlist = json.loads(get_response.data)
    
    symbol_count = sum(1 for item in watchlist if item['symbol'] == symbol)
    assert symbol_count == 2

def test_health_check_database_connection(test_client):
    """Test that health check includes database status"""
    response = test_client.get('/api/health')
    data = json.loads(response.data)
    
    # Database should be 'connected' even with mock (or 'error' if real DB is down)
    assert 'database' in data
    assert data['database'] in ['connected', 'error']

def test_watchlist_returns_no_mongo_id(test_client):
    """Test that watchlist items don't expose MongoDB _id field"""
    # Create an item
    test_client.post('/api/watchlist',
                    data=json.dumps({"symbol": "BTC/USDT"}),
                    content_type='application/json')
    
    # Get watchlist
    response = test_client.get('/api/watchlist')
    watchlist = json.loads(response.data)
    
    # Check that _id is not in any item
    for item in watchlist:
        assert '_id' not in item