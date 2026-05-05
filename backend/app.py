from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import uuid
import random

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/zenith_db")
client = MongoClient(MONGO_URI)
db = client.get_database()
watchlist_collection = db.watchlist
journal_collection = db.journal

# Price Simulation for non-crypto (real-time crypto from Binance)
def get_crypto_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url, timeout=2)
        data = response.json()
        return float(data['price'])
    except:
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "system": "Zenith Quantum Terminal",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if client.admin.command('ping') else "error"
    }), 200

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Aggregate real-time and simulated market data."""
    # Real data for BTC and ETH
    btc_price = get_crypto_price("BTC") or 65432.10
    eth_price = get_crypto_price("ETH") or 3456.78
    
    # Simulated data for FX/Gold (Realistic ranges)
    xau_price = round(2350.50 + random.uniform(-0.5, 0.5), 2)
    eur_price = round(1.0850 + random.uniform(-0.0001, 0.0001), 4)
    
    return jsonify({
        "BTC/USDT": {"price": btc_price, "change": "+2.4%"},
        "ETH/USDT": {"price": eth_price, "change": "-1.2%"},
        "XAU/USD": {"price": xau_price, "change": "+0.15%"},
        "EUR/USD": {"price": eur_price, "change": "-0.05%"}
    }), 200

@app.route('/api/watchlist', methods=['GET', 'POST'])
def handle_watchlist():
    if request.method == 'POST':
        data = request.json
        if not data or 'symbol' not in data:
            return jsonify({"error": "Symbol required"}), 400
        
        pair = {
            "id": str(uuid.uuid4()),
            "symbol": data.get('symbol'),
            "added_at": datetime.utcnow().isoformat()
        }
        watchlist_collection.insert_one(pair.copy())
        return jsonify(pair), 201
        
    watchlist = list(watchlist_collection.find({}, {'_id': 0}))
    return jsonify(watchlist), 200

@app.route('/api/watchlist/<pair_id>', methods=['DELETE'])
def remove_from_watchlist(pair_id):
    watchlist_collection.delete_one({"id": pair_id})
    return jsonify({"message": "Removed"}), 200

@app.route('/api/journal', methods=['GET', 'POST'])
def handle_journal():
    """Form submission endpoint for market notes."""
    if request.method == 'POST':
        data = request.json
        if not data or 'title' not in data:
            return jsonify({"error": "Title is required"}), 400
        
        note = {
            "id": str(uuid.uuid4()),
            "title": data.get('title'),
            "content": data.get('content', ''),
            "symbol": data.get('symbol', 'Global'),
            "timestamp": datetime.utcnow().isoformat()
        }
        journal_collection.insert_one(note.copy())
        return jsonify(note), 201
        
    notes = list(journal_collection.find({}, {'_id': 0}).sort("timestamp", -1))
    return jsonify(notes), 200

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
