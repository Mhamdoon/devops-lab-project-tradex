import React, { useState, useEffect, useRef } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  ShieldCheck, 
  Cpu, 
  Star,
  Search,
  Bell,
  Menu,
  ChevronRight,
  Plus
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// --- TradingView Widget Component ---
const TradingViewWidget = ({ symbol = "BINANCE:BTCUSDT" }) => {
  const container = useRef();

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.innerHTML = JSON.stringify({
      "autosize": true,
      "symbol": symbol,
      "interval": "D",
      "timezone": "Etc/UTC",
      "theme": "dark",
      "style": "1",
      "locale": "en",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "calendar": false,
      "support_host": "https://www.tradingview.com"
    });
    container.current.innerHTML = "";
    container.current.appendChild(script);
  }, [symbol]);

  return <div className="chart-container" ref={container} style={{ height: "100%", width: "100%" }}></div>;
};

// --- Main App Component ---
function App() {
  const [prices, setPrices] = useState({});
  const [watchlist, setWatchlist] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState("BINANCE:BTCUSDT");
  const [isHealthOk, setIsHealthOk] = useState(false);

  useEffect(() => {
    fetchPrices();
    fetchWatchlist();
    checkHealth();
    
    const priceInterval = setInterval(fetchPrices, 3000);
    const healthInterval = setInterval(checkHealth, 10000);

    return () => {
      clearInterval(priceInterval);
      clearInterval(healthInterval);
    };
  }, []);

  const checkHealth = async () => {
    try {
      const res = await axios.get(`${API_BASE}/health`);
      setIsHealthOk(res.data.status === 'online');
    } catch (e) { setIsHealthOk(false); }
  };

  const fetchPrices = async () => {
    try {
      const res = await axios.get(`${API_BASE}/prices`);
      setPrices(res.data);
    } catch (e) { console.error("Price fetch failed"); }
  };

  const fetchWatchlist = async () => {
    try {
      const res = await axios.get(`${API_BASE}/watchlist`);
      setWatchlist(res.data);
    } catch (e) { console.error("Watchlist fetch failed"); }
  };

  const addToWatchlist = async (symbol) => {
    try {
      await axios.post(`${API_BASE}/watchlist`, { symbol });
      fetchWatchlist();
    } catch (e) { console.error("Add failed"); }
  };

  const tickerItems = Object.entries(prices).map(([pair, data]) => (
    <div key={pair} className="ticker-item">
      <span style={{ color: 'var(--text-dim)' }}>{pair}</span>
      <span className={data.change.startsWith('+') ? 'price-up' : 'price-down'}>
        {data.price.toLocaleString()}
      </span>
      <span style={{ fontSize: '0.7rem', opacity: 0.6 }}>{data.change}</span>
    </div>
  ));

  return (
    <div className="terminal-layout">
      {/* Header */}
      <header>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ background: 'var(--accent-lime)', padding: '0.4rem', borderRadius: '0.4rem' }}>
            <Activity color="black" size={20} />
          </div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '2px' }} className="glow-text">ZENITH</h1>
          <div style={{ marginLeft: '2rem', display: 'flex', gap: '1.5rem', fontSize: '0.85rem', color: 'var(--text-dim)' }}>
            <span style={{ cursor: 'pointer', color: 'var(--text-main)' }}>Terminal</span>
            <span style={{ cursor: 'pointer' }}>Exchange</span>
            <span style={{ cursor: 'pointer' }}>Portfolio</span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem' }}>
            <ShieldCheck size={14} color={isHealthOk ? "var(--accent-lime)" : "var(--down)"} />
            <span style={{ color: isHealthOk ? "var(--accent-lime)" : "var(--down)" }}>
              {isHealthOk ? "QUANTUM SECURE" : "CONNECTION LOST"}
            </span>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <div className="glass-card" style={{ padding: '0.5rem', borderRadius: '0.5rem' }}><Bell size={18} /></div>
            <div className="glass-card" style={{ padding: '0.5rem', borderRadius: '0.5rem' }}><Search size={18} /></div>
          </div>
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--accent-purple)' }}></div>
        </div>
      </header>

      {/* Ticker Bar */}
      <div className="ticker-bar">
        <div className="animate-ticker">
          {tickerItems}
          {tickerItems} {/* Duplicate for seamless loop */}
        </div>
      </div>

      {/* Main Chart Stage */}
      <main className="main-stage">
        <TradingViewWidget symbol={selectedSymbol} />
      </main>

      {/* Side Panel */}
      <aside className="side-panel">
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '0.9rem', color: 'var(--text-dim)' }}>ACTIVE WATCHLIST</h3>
            <Star size={16} color="var(--accent-lime)" fill="var(--accent-lime)" />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {watchlist.map((item) => (
              <div 
                key={item.id} 
                className="glass-card" 
                style={{ padding: '0.75rem', cursor: 'pointer', borderColor: selectedSymbol.includes(item.symbol) ? 'var(--accent-lime)' : 'var(--border-glass)' }}
                onClick={() => setSelectedSymbol(item.symbol === 'BTC' ? 'BINANCE:BTCUSDT' : item.symbol === 'ETH' ? 'BINANCE:ETHUSDT' : item.symbol)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700 }}>{item.symbol}</span>
                  <ChevronRight size={14} color="var(--text-dim)" />
                </div>
              </div>
            ))}
            <button 
              className="btn-lime" 
              style={{ fontSize: '0.7rem', padding: '0.5rem' }}
              onClick={() => {
                const s = prompt("Enter TradingView Symbol (e.g., BINANCE:BTCUSDT, FX:EURUSD)");
                if (s) addToWatchlist(s);
              }}
            >
              <Plus size={14} style={{ marginRight: '0.5rem' }} /> Add Asset
            </button>
          </div>
        </div>

        <div className="glass-card" style={{ flex: 1, background: 'linear-gradient(180deg, rgba(191,255,0,0.05), transparent)' }}>
          <h3 style={{ fontSize: '0.9rem', marginBottom: '1rem', color: 'var(--text-dim)' }}>AI MARKET SENTIMENT</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem' }}>BULLISH BIAS</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--up)' }}>84%</span>
              </div>
              <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px' }}>
                <motion.div initial={{ width: 0 }} animate={{ width: '84%' }} style={{ height: '100%', background: 'var(--up)', borderRadius: '2px' }} />
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem' }}>VOLATILITY INDEX</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-purple)' }}>MEDIUM</span>
              </div>
              <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px' }}>
                <motion.div initial={{ width: 0 }} animate={{ width: '45%' }} style={{ height: '100%', background: 'var(--accent-purple)', borderRadius: '2px' }} />
              </div>
            </div>
          </div>
          
          <div style={{ marginTop: '2rem' }}>
             <p style={{ fontSize: '0.7rem', color: 'var(--text-dim)', lineHeight: 1.5 }}>
               Quantum AI identifies high-probability liquidity zones in XAU/USD. Suggesting long position above 2345.50.
             </p>
          </div>
        </div>
        
        <button className="btn-lime">Execute Trade</button>
      </aside>
    </div>
  );
}

export default App;
