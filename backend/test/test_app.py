import pytest
import json
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to access globals, and the Flask app instance
import app as app_module
from app import app
import mongomock

@pytest.fixture
def test_client():
    """Create a test client with mocked MongoDB"""
    app.config['TESTING'] = True

    # Create a mock MongoDB client and a named database
    mock_client = mongomock.MongoClient()
    mock_db = mock_client['zenith_db_test']

    # Store original global variables from app_module
    original_watchlist_collection = app_module.watchlist_collection
    original_client = app_module.client
    original_db = app_module.db

    # Replace with mocks
    app_module.watchlist_collection = mock_db.watchlist
    app_module.client = mock_client
    app_module.db = mock_db

    with app.test_client() as client:
        yield client

    # Restore originals after test
    app_module.watchlist_collection = original_watchlist_collection
    app_module.client = original_client
    app_module.db = original_db

@pytest.fixture
def sample_watchlist_item():
    return {
        "symbol": "BTC/USDT",
        "id": "test-id-123",
        "added_at": datetime.utcnow().isoformat()
    }

# ========== All test functions remain exactly as before ==========
def test_health_check(test_client):
    response = test_client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'online'
    assert data['system'] == 'Zenith Quantum Terminal'
    assert 'timestamp' in data
    assert 'database' in data

def test_get_prices(test_client):
    response = test_client.get('/api/prices')
    assert response.status_code == 200
    data = json.loads(response.data)
    expected_symbols = ['BTC/USDT', 'ETH/USDT', 'XAU/USD', 'EUR/USD']
    for symbol in expected_symbols:
        assert symbol in data
    for symbol, price_data in data.items():
        assert 'price' in price_data
        assert 'change' in price_data
        assert isinstance(price_data['price'], (int, float))
        assert isinstance(price_data['change'], str)
        assert price_data['price'] > 0

def test_prices_data_types(test_client):
    response = test_client.get('/api/prices')
    data = json.loads(response.data)
    assert isinstance(data['BTC/USDT']['price'], float)
    assert isinstance(data['ETH/USDT']['price'], float)
    assert isinstance(data['XAU/USD']['price'], float)
    assert isinstance(data['EUR/USD']['price'], float)

def test_prices_change_format(test_client):
    response = test_client.get('/api/prices')
    data = json.loads(response.data)
    for symbol, price_data in data.items():
        change = price_data['change']
        assert '%' in change
        assert change[0] in ['+', '-']

def test_create_watchlist_item(test_client):
    new_item = {"symbol": "ETH/USDT"}
    response = test_client.post('/api/watchlist',
                                data=json.dumps(new_item),
                                content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['symbol'] == "ETH/USDT"
    assert 'id' in data
    assert 'added_at' in data
    assert len(data['id']) == 36

def test_create_watchlist_missing_symbol(test_client):
    response = test_client.post('/api/watchlist',
                                data=json.dumps({}),
                                content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == "Symbol required"
    
    response = test_client.post('/api/watchlist',
                                data=json.dumps({"wrong_field": "BTC"}),
                                content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_create_watchlist_empty_body(test_client):
    response = test_client.post('/api/watchlist',
                                data=json.dumps(None),
                                content_type='application/json')
    assert response.status_code == 400

def test_get_watchlist_empty(test_client):
    response = test_client.get('/api/watchlist')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_watchlist_with_items(test_client):
    item1 = {"symbol": "BTC/USDT"}
    item2 = {"symbol": "ETH/USDT"}
    test_client.post('/api/watchlist', data=json.dumps(item1), content_type='application/json')
    test_client.post('/api/watchlist', data=json.dumps(item2), content_type='application/json')
    response = test_client.get('/api/watchlist')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    symbols = [item['symbol'] for item in data]
    assert 'BTC/USDT' in symbols
    assert 'ETH/USDT' in symbols

def test_delete_watchlist_item(test_client):
    new_item = {"symbol": "XAU/USD"}
    post_response = test_client.post('/api/watchlist',
                                     data=json.dumps(new_item),
                                     content_type='application/json')
    created_item = json.loads(post_response.data)
    item_id = created_item['id']
    delete_response = test_client.delete(f'/api/watchlist/{item_id}')
    assert delete_response.status_code == 200
    delete_data = json.loads(delete_response.data)
    assert delete_data['message'] == "Removed"
    get_response = test_client.get('/api/watchlist')
    watchlist = json.loads(get_response.data)
    assert not any(item['id'] == item_id for item in watchlist)

def test_delete_nonexistent_watchlist_item(test_client):
    response = test_client.delete('/api/watchlist/nonexistent-id-123')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "Removed"

def test_watchlist_crud_flow(test_client):
    item = {"symbol": "EUR/USD"}
    create_response = test_client.post('/api/watchlist',
                                       data=json.dumps(item),
                                       content_type='application/json')
    assert create_response.status_code == 201
    created_item = json.loads(create_response.data)
    item_id = created_item['id']
    read_response = test_client.get('/api/watchlist')
    watchlist = json.loads(read_response.data)
    found_item = next((i for i in watchlist if i['id'] == item_id), None)
    assert found_item is not None
    assert found_item['symbol'] == "EUR/USD"
    delete_response = test_client.delete(f'/api/watchlist/{item_id}')
    assert delete_response.status_code == 200
    final_response = test_client.get('/api/watchlist')
    final_watchlist = json.loads(final_response.data)
    assert not any(i['id'] == item_id for i in final_watchlist)

def test_watchlist_item_structure(test_client):
    new_item = {"symbol": "BTC/USDT"}
    response = test_client.post('/api/watchlist',
                                data=json.dumps(new_item),
                                content_type='application/json')
    data = json.loads(response.data)
    assert 'id' in data
    assert 'symbol' in data
    assert 'added_at' in data
    assert isinstance(data['id'], str)
    assert isinstance(data['symbol'], str)
    assert isinstance(data['added_at'], str)
    try:
        datetime.fromisoformat(data['added_at'].replace('Z', '+00:00'))
        valid_date = True
    except:
        valid_date = False
    assert valid_date

def test_multiple_watchlist_items(test_client):
    symbols = ['BTC/USDT', 'ETH/USDT', 'XAU/USD', 'EUR/USD']
    for symbol in symbols:
        response = test_client.post('/api/watchlist',
                                    data=json.dumps({"symbol": symbol}),
                                    content_type='application/json')
        assert response.status_code == 201
    response = test_client.get('/api/watchlist')
    watchlist = json.loads(response.data)
    assert len(watchlist) == len(symbols)
    retrieved_symbols = [item['symbol'] for item in watchlist]
    for symbol in symbols:
        assert symbol in retrieved_symbols

def test_watchlist_idempotency(test_client):
    symbol = "BTC/USDT"
    response1 = test_client.post('/api/watchlist',
                                 data=json.dumps({"symbol": symbol}),
                                 content_type='application/json')
    response2 = test_client.post('/api/watchlist',
                                 data=json.dumps({"symbol": symbol}),
                                 content_type='application/json')
    assert response1.status_code == 201
    assert response2.status_code == 201
    get_response = test_client.get('/api/watchlist')
    watchlist = json.loads(get_response.data)
    symbol_count = sum(1 for item in watchlist if item['symbol'] == symbol)
    assert symbol_count == 2

def test_health_check_database_connection(test_client):
    response = test_client.get('/api/health')
    data = json.loads(response.data)
    assert 'database' in data
    # Mock client passes ping, so it should be 'connected'
    assert data['database'] == 'connected'

def test_watchlist_returns_no_mongo_id(test_client):
    test_client.post('/api/watchlist',
                    data=json.dumps({"symbol": "BTC/USDT"}),
                    content_type='application/json')
    response = test_client.get('/api/watchlist')
    watchlist = json.loads(response.data)
    for item in watchlist:
        assert '_id' not in item