import React, { useState, useEffect } from 'react';
import { 
  Search, Heart, History, BarChart3, Sparkles, TrendingUp, 
  TrendingDown, Truck, Star, ArrowRight, ExternalLink, 
  Bell, Percent, Trash2, RefreshCw, Clock, Tag, X, Check
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const API_BASE = 'http://localhost:5000/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResult, setSearchResult] = useState(null);
  const [historyList, setHistoryList] = useState([]);
  const [savedDeals, setSavedDeals] = useState([]);
  const [stats, setStats] = useState({
    total_searches: 0,
    total_saved_deals: 0,
    average_discount: 0,
    estimated_savings: 0,
    recent_searches: [],
    categories: {}
  });
  const [expandedGroup, setExpandedGroup] = useState(null);
  
  // Alert Modal state
  const [alertModalOpen, setAlertModalOpen] = useState(false);
  const [selectedDealForAlert, setSelectedDealForAlert] = useState(null);
  const [targetPrice, setTargetPrice] = useState('');

  // Toast state
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3000);
  };

  // Fetch initial data
  useEffect(() => {
    fetchStats();
    fetchHistory();
    fetchSavedDeals();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats`);
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error("Error fetching stats:", err);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/history`);
      if (res.ok) {
        const data = await res.json();
        setHistoryList(data);
      }
    } catch (err) {
      console.error("Error fetching history:", err);
    }
  };

  const fetchSavedDeals = async () => {
    try {
      const res = await fetch(`${API_BASE}/saved`);
      if (res.ok) {
        const data = await res.json();
        setSavedDeals(data);
      }
    } catch (err) {
      console.error("Error fetching saved deals:", err);
    }
  };

  const handleSearch = async (queryStr, forceRefresh = false) => {
    const term = queryStr || searchQuery;
    if (!term.strip ? !term.trim() : !term) {
      addToast("Please enter a search term", "error");
      return;
    }
    
    setSearchQuery(term);
    setIsSearching(true);
    setExpandedGroup(null);
    setActiveTab('search');
    
    try {
      const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(term)}&refresh=${forceRefresh}`);
      if (res.ok) {
        const data = await res.json();
        setSearchResult(data);
        if (data && data.groups && data.groups.length > 0) {
          setExpandedGroup(data.groups[0].id);
        }
        fetchStats();
        fetchHistory();
      } else {
        addToast("Error running search. Please try again.", "error");
      }
    } catch (err) {
      console.error("Search error:", err);
      addToast("Failed to connect to backend", "error");
    } finally {
      setIsSearching(false);
    }
  };

  const handleSaveDeal = async (deal, alertPrice = null) => {
    try {
      const res = await fetch(`${API_BASE}/saved`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: deal.title,
          price: deal.price,
          platform: deal.platform,
          image_url: deal.image_url,
          url: deal.url,
          target_price: alertPrice ? parseFloat(alertPrice) : null
        })
      });

      if (res.ok) {
        const result = await res.json();
        addToast(result.message || "Deal saved successfully!");
        fetchSavedDeals();
        fetchStats();
      } else {
        addToast("Failed to save deal", "error");
      }
    } catch (err) {
      console.error("Save deal error:", err);
      addToast("Network error saving deal", "error");
    }
  };

  const handleUnsaveDeal = async (dealId) => {
    try {
      const res = await fetch(`${API_BASE}/saved/${dealId}`, {
        method: 'DELETE'
      });

      if (res.ok) {
        addToast("Deal removed from watch list");
        fetchSavedDeals();
        fetchStats();
      } else {
        addToast("Failed to remove deal", "error");
      }
    } catch (err) {
      console.error("Remove deal error:", err);
      addToast("Network error", "error");
    }
  };

  const openPriceAlertModal = (deal) => {
    setSelectedDealForAlert(deal);
    setTargetPrice(Math.round(deal.price * 0.9).toString()); // Default to 10% off
    setAlertModalOpen(true);
  };

  const savePriceAlert = () => {
    if (!targetPrice || isNaN(targetPrice)) {
      addToast("Please enter a valid target price", "error");
      return;
    }
    handleSaveDeal(selectedDealForAlert, targetPrice);
    setAlertModalOpen(false);
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <nav className="sidebar">
        <a href="#" className="logo" onClick={() => setActiveTab('dashboard')}>
          <div className="logo-icon">
            <Sparkles size={24} />
          </div>
          <div className="logo-text">
            Price <span>Compare</span>
          </div>
        </a>

        <ul className="nav-links">
          <li>
            <a 
              className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              <BarChart3 size={20} />
              Dashboard
            </a>
          </li>
          <li>
            <a 
              className={`nav-item ${activeTab === 'search' ? 'active' : ''}`}
              onClick={() => setActiveTab('search')}
            >
              <Search size={20} />
              Compare Deals
            </a>
          </li>
          <li>
            <a 
              className={`nav-item ${activeTab === 'saved' ? 'active' : ''}`}
              onClick={() => setActiveTab('saved')}
            >
              <Heart size={20} />
              Price Alerts ({savedDeals.length})
            </a>
          </li>
          <li>
            <a 
              className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              <History size={20} />
              Search History
            </a>
          </li>
        </ul>

        <div className="sidebar-footer">
          <p>AI Smart Assistant v1.0</p>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'search' && renderSearchPage()}
        {activeTab === 'saved' && renderSavedDealsPage()}
        {activeTab === 'history' && renderHistoryPage()}
      </main>

      {/* Price Alert Modal */}
      {alertModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel">
            <div className="section-header">
              <h3 className="modal-title">Create Price Alert</h3>
              <button className="btn-outline" style={{padding: '4px'}} onClick={() => setAlertModalOpen(false)}>
                <X size={16} />
              </button>
            </div>
            <p className="heading-desc" style={{fontSize: '13px'}}>
              We will monitor the price for <strong>{selectedDealForAlert?.title}</strong> on <strong>{selectedDealForAlert?.platform}</strong> and notify you when it drops.
            </p>
            <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
              <label style={{fontSize: '12px', fontWeight: '600', color: 'var(--text-secondary)'}}>Current Price</label>
              <div style={{fontSize: '20px', fontWeight: '800'}}>₹{selectedDealForAlert?.price.toLocaleString()}</div>
            </div>
            <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
              <label style={{fontSize: '12px', fontWeight: '600', color: 'var(--text-secondary)'}}>Alert Target Price (₹)</label>
              <input 
                type="number" 
                className="glass-input" 
                value={targetPrice} 
                onChange={(e) => setTargetPrice(e.target.value)} 
                placeholder="e.g. 50000"
              />
            </div>
            <div className="modal-actions">
              <button className="btn-outline" onClick={() => setAlertModalOpen(false)}>Cancel</button>
              <button className="btn-glow" onClick={savePriceAlert}>Set Alert</button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notifications */}
      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className="toast" style={{borderColor: t.type === 'error' ? 'var(--accent-rose)' : 'var(--accent-emerald)'}}>
            {t.type === 'error' ? <X size={16} style={{color: 'var(--accent-rose)'}} /> : <Check size={16} style={{color: 'var(--accent-emerald)'}} />}
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </div>
  );

  function renderDashboard() {
    return (
      <div>
        <div className="dashboard-hero glass-panel">
          <div className="hero-glow-1"></div>
          <div className="hero-glow-2"></div>
          <h1 className="hero-title">Smart Shopping Assistant</h1>
          <p className="hero-subtitle">
            Compare prices, check reviews, and discover optimal AI-driven recommendations across Amazon, Flipkart, Myntra, Ajio, and Meesho with a single search.
          </p>
          <div className="search-box-large">
            <input 
              type="text" 
              className="glass-input" 
              placeholder="Search products (e.g. iPhone 15, Puma sneakers, Jeans)..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button className="btn-glow" onClick={() => handleSearch()}>
              <Search size={18} />
              Compare
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card glass-panel">
            <div className="stat-icon">
              <Search size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-value">{stats.total_searches}</div>
              <div className="stat-label">Total Smart Searches</div>
            </div>
          </div>
          <div className="stat-card glass-panel">
            <div className="stat-icon">
              <Percent size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-value">{stats.average_discount}%</div>
              <div className="stat-label">Average Discount Found</div>
            </div>
          </div>
          <div className="stat-card glass-panel">
            <div className="stat-icon">
              <TrendingDown size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-value">₹{stats.estimated_savings.toLocaleString()}</div>
              <div className="stat-label">Estimated Money Saved</div>
            </div>
          </div>
        </div>

        {/* Dashboard Sections */}
        <div className="dashboard-sections">
          <div className="dashboard-list-card glass-panel">
            <div className="section-header">
              <h2 className="section-title">Popular Product Categories</h2>
              <Clock size={16} style={{color: 'var(--text-muted)'}} />
            </div>
            {Object.keys(stats.categories).length === 0 ? (
              <div className="empty-state">
                <Tag className="empty-icon" size={40} />
                <p>No search history yet. Start by comparing products above!</p>
              </div>
            ) : (
              <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
                {Object.entries(stats.categories).map(([cat, count]) => (
                  <div key={cat} style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
                    <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
                      <Tag size={16} style={{color: 'var(--primary)'}} />
                      <span style={{fontWeight: '600'}}>{cat}</span>
                    </div>
                    <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
                      <span style={{fontSize: '13px', color: 'var(--text-secondary)'}}>{count} search{count > 1 ? 'es' : ''}</span>
                      <div style={{width: '100px', height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden'}}>
                        <div style={{
                          width: `${(count / Math.max(...Object.values(stats.categories))) * 100}%`, 
                          height: '100%', 
                          background: 'linear-gradient(90deg, var(--primary), var(--secondary))'
                        }}></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="dashboard-list-card glass-panel">
            <div className="section-header">
              <h2 className="section-title">Recent Queries</h2>
              <History size={16} style={{color: 'var(--text-muted)'}} />
            </div>
            {stats.recent_searches.length === 0 ? (
              <div className="empty-state">
                <History className="empty-icon" size={40} />
                <p>Your search history is empty.</p>
              </div>
            ) : (
              <div className="recent-list">
                {stats.recent_searches.map((q, idx) => (
                  <div key={idx} className="recent-item" onClick={() => handleSearch(q)}>
                    <div className="recent-query-info">
                      <Search size={14} className="recent-icon" />
                      <span className="recent-query-text">{q}</span>
                    </div>
                    <ArrowRight size={14} style={{color: 'var(--text-muted)'}} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  function renderSearchPage() {
    return (
      <div>
        <div className="search-header-container">
          <div className="heading-container">
            <h1 className="heading-title">Compare Product Deals</h1>
            <p className="heading-desc">Enter a query to cluster products across multiple platforms.</p>
          </div>
          <div className="search-box-small">
            <input 
              type="text" 
              className="glass-input" 
              placeholder="Search..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button className="btn-glow" onClick={() => handleSearch()}>
              <Search size={16} />
              Compare
            </button>
          </div>
        </div>

        {isSearching && (
          <div className="loading-container glass-panel">
            <div className="scanner-ring"></div>
            <div className="loading-text">Scanning Platforms...</div>
            <div className="loading-progress">Checking Amazon, Flipkart, Meesho, Myntra, Ajio...</div>
          </div>
        )}

        {!isSearching && !searchResult && (
          <div className="glass-panel" style={{padding: '80px 20px'}}>
            <div className="empty-state">
              <Search className="empty-icon" size={50} />
              <h3 style={{marginBottom: '8px'}}>Ready to Compare</h3>
              <p>Type a product name in the search bar above to fetch and compare live details.</p>
            </div>
          </div>
        )}

        {!isSearching && searchResult && (
          <div>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px'}}>
              <div style={{fontSize: '14px', color: 'var(--text-secondary)'}}>
                Found <strong>{searchResult.groups.length} matching product groups</strong> across platforms 
                {searchResult.from_cache && <span style={{color: 'var(--accent-emerald)', marginLeft: '8px'}}>(Loaded instantly from database cache)</span>}
              </div>
              <button className="btn-outline" onClick={() => handleSearch(searchQuery, true)}>
                <RefreshCw size={14} />
                Force Refresh
              </button>
            </div>

            {searchResult.groups.length === 0 ? (
              <div className="glass-panel" style={{padding: '80px 20px'}}>
                <div className="empty-state">
                  <X className="empty-icon" size={50} style={{color: 'var(--accent-rose)'}} />
                  <h3 style={{marginBottom: '8px'}}>No Matches Found</h3>
                  <p>We couldn't scrape any matching deals for "{searchQuery}". Try adjusting your keywords.</p>
                </div>
              </div>
            ) : (
              <div className="results-grid">
                {searchResult.groups.map(group => {
                  const isExpanded = expandedGroup === group.id;
                  const priceDiff = group.max_price - group.min_price;
                  const savingsPercentage = group.max_price > 0 ? Math.round((priceDiff / group.max_price) * 100) : 0;
                  
                  return (
                    <div key={group.id} className="product-group-card glass-panel">
                      {/* Summary Row */}
                      <div className="group-summary-bar" onClick={() => setExpandedGroup(isExpanded ? null : group.id)}>
                        <div className="group-img-container">
                          <img src={group.image_url} alt={group.name} className="group-img" />
                        </div>
                        <div className="group-title-info">
                          <span className="group-title">{group.name}</span>
                          <span className="group-count">{group.deals.length} deals compared</span>
                        </div>
                        <div className="group-price-range">
                          ₹{group.min_price.toLocaleString()} {priceDiff > 0 && ` - ₹${group.max_price.toLocaleString()}`}
                        </div>
                        <div className="group-savings">
                          {priceDiff > 0 ? (
                            <span style={{display: 'flex', alignItems: 'center', gap: '4px'}}>
                              <TrendingDown size={14} /> Save up to {savingsPercentage}%
                            </span>
                          ) : (
                            <span style={{color: 'var(--text-muted)', fontSize: '13px'}}>Single Offer</span>
                          )}
                        </div>
                        <div className="group-expand-icon">
                          <ArrowRight size={18} style={{
                            transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
                            transition: 'transform 0.2s ease-out'
                          }} />
                        </div>
                      </div>

                      {/* Detailed Comparison Area */}
                      {isExpanded && (
                        <div className="group-expanded-details">
                          <div className="group-expanded-grid">
                            
                            {/* Table Column */}
                            <div className="deals-table-container">
                              <h3 style={{fontSize: '15px', fontWeight: '700', marginBottom: '14px'}}>Available Deals</h3>
                              <table className="deals-table">
                                <thead>
                                  <tr>
                                    <th>Platform</th>
                                    <th>Product Title</th>
                                    <th>Price</th>
                                    <th>Rating</th>
                                    <th>Shipping</th>
                                    <th>Action</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {group.deals.map(deal => {
                                    return (
                                      <tr key={deal.id} style={{
                                        background: deal.is_best_value ? 'rgba(99, 102, 241, 0.03)' : 'transparent',
                                        cursor: 'pointer'
                                      }} onClick={() => window.open(deal.url, '_blank')} title={`Open ${deal.platform} product page`}>
                                        <td>
                                          <span className={`badge badge-platform ${deal.platform.toLowerCase()}`}>
                                            {deal.platform}
                                          </span>
                                        </td>
                                        <td>
                                          <div className="deal-cell-title" title={deal.title}>
                                            {deal.title}
                                          </div>
                                          <div style={{display: 'flex', gap: '6px', marginTop: '4px'}}>
                                            {deal.is_best_value && <span className="badge badge-recommended">Best Value</span>}
                                            {deal.is_cheapest && <span className="badge badge-cheapest">Cheapest</span>}
                                          </div>
                                        </td>
                                        <td>
                                          <div>
                                            <span className="deal-price">₹{deal.price.toLocaleString()}</span>
                                            {deal.discount > 0 && (
                                              <span className="deal-original-price">₹{deal.original_price?.toLocaleString()}</span>
                                            )}
                                          </div>
                                          {deal.discount > 0 && (
                                            <span style={{fontSize: '11px', color: 'var(--accent-rose)', fontWeight: '600'}}>
                                              ({Math.round(deal.discount)}% OFF)
                                            </span>
                                          )}
                                        </td>
                                        <td>
                                          <div className="deal-rating-box">
                                            <Star size={13} className="deal-rating-star" />
                                            <span>{deal.rating}</span>
                                            <span className="deal-rating-count">({deal.reviews_count.toLocaleString()})</span>
                                          </div>
                                        </td>
                                        <td>
                                          <div className="deal-shipping">
                                            {deal.delivery_fee === 0 ? "Free" : `₹${deal.delivery_fee}`}
                                            <div style={{fontSize: '11px', color: 'var(--text-muted)'}}>{deal.delivery_time}</div>
                                          </div>
                                        </td>
                                        <td>
                                          <div className="deal-action-cell">
                                            <button className="btn-outline" style={{padding: '6px'}} onClick={() => openPriceAlertModal(deal)} title="Create Price Alert">
                                              <Bell size={13} />
                                            </button>
                                            <button className="btn-outline" style={{padding: '6px'}} onClick={() => handleSaveDeal(deal)} title="Save Deal">
                                              <Heart size={13} />
                                            </button>
                                            <a href={deal.url} target="_blank" rel="noopener noreferrer" className="btn-glow" style={{padding: '6px 10px', fontSize: '12px'}}>
                                              <ExternalLink size={12} /> Buy
                                            </a>
                                          </div>
                                        </td>
                                      </tr>
                                    );
                                  })}
                                </tbody>
                              </table>
                            </div>

                            {/* Recommendation and Visualization Column */}
                            <div style={{display: 'flex', flexDirection: 'column', gap: '24px'}}>
                              
                              {/* Recommendation Card */}
                              {renderAIRecommendation(group.deals)}

                              {/* Price Comparison Chart */}
                              {renderPriceChart(group.deals)}
                            </div>

                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  function renderAIRecommendation(deals) {
    const recommended = deals.find(d => d.is_best_value);
    if (!recommended) return null;

    const sentimentText = recommended.sentiment_score > 0.4 ? "Extremely Positive" : recommended.sentiment_score > 0.1 ? "Mostly Positive" : "Neutral/Mixed";
    const sentimentColor = recommended.sentiment_score > 0.1 ? "var(--accent-emerald)" : recommended.sentiment_score < -0.1 ? "var(--accent-rose)" : "var(--text-secondary)";

    return (
      <div className="ai-recommendation-card glass-panel">
        <div className="ai-rec-header">
          <div className="ai-rec-title">
            <Sparkles className="ai-sparkle-icon" size={16} />
            <span>AI Smart Recommendation</span>
          </div>
          <div className="ai-rec-score">
            Deal Score: <span className="ai-rec-score-value">{recommended.recommendation_score}/100</span>
          </div>
        </div>
        <div className="ai-rec-body">
          <div className="ai-rec-deal-info">
            <img src={recommended.image_url} alt="" style={{width: '45px', height: '45px', borderRadius: '6px', background: 'white', objectFit: 'contain'}} />
            <div className="ai-rec-deal-details">
              <span className="ai-rec-deal-name">{recommended.title}</span>
              <span style={{fontSize: '12px', color: 'var(--text-secondary)'}}>
                ₹{recommended.price.toLocaleString()} on <strong>{recommended.platform}</strong>
              </span>
            </div>
          </div>
          
          <ul className="ai-rec-bullet-list">
            {recommended.ai_summary.split(' \n').map((point, index) => (
              <li key={index} className="ai-rec-bullet">
                <ArrowRight size={13} style={{marginTop: '3px', color: 'var(--primary)', flexShrink: 0}} />
                <span>{point}</span>
              </li>
            ))}
            <li className="ai-rec-bullet">
              <ArrowRight size={13} style={{marginTop: '3px', color: 'var(--primary)', flexShrink: 0}} />
              <span>Customer Sentiment: <strong style={{color: sentimentColor}}>{sentimentText}</strong></span>
            </li>
          </ul>
        </div>
      </div>
    );
  }

  function renderPriceChart(deals) {
    const chartData = deals.map(d => ({
      name: d.platform,
      price: d.price,
      isBest: d.is_best_value,
      isCheapest: d.is_cheapest
    }));

    // Sort to show cheapest first
    chartData.sort((a, b) => a.price - b.price);

    const CustomTooltip = ({ active, payload }) => {
      if (active && payload && payload.length) {
        return (
          <div className="glass-panel" style={{padding: '10px 14px', border: '1px solid rgba(255,255,255,0.1)'}}>
            <p style={{fontWeight: '700', fontSize: '13px'}}>{payload[0].payload.name}</p>
            <p style={{color: 'var(--primary)', fontWeight: '600', fontSize: '14px', marginTop: '4px'}}>
              ₹{payload[0].value.toLocaleString()}
            </p>
          </div>
        );
      }
      return null;
    };

    return (
      <div className="chart-box">
        <div className="chart-title">Price Comparison across Platforms</div>
        <div style={{width: '100%', height: 180}}>
          <ResponsiveContainer>
            <BarChart data={chartData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
              <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
              <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
              <Bar dataKey="price" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => {
                  let fill = 'var(--text-muted)';
                  if (entry.isBest) fill = 'var(--primary)';
                  else if (entry.isCheapest) fill = 'var(--secondary)';
                  return <Cell key={`cell-${index}`} fill={fill} opacity={0.8} />;
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{display: 'flex', gap: '16px', justifyContent: 'center', fontSize: '11px'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
            <div style={{width: '12px', height: '12px', background: 'var(--primary)', borderRadius: '2px'}}></div>
            <span>Best Value (AI recommended)</span>
          </div>
          <div style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
            <div style={{width: '12px', height: '12px', background: 'var(--secondary)', borderRadius: '2px'}}></div>
            <span>Cheapest Deal</span>
          </div>
        </div>
      </div>
    );
  }

  function renderSavedDealsPage() {
    return (
      <div>
        <div className="heading-container">
          <h1 className="heading-title">Active Price Alerts</h1>
          <p className="heading-desc">Saved offers and price thresholds you're monitoring.</p>
        </div>

        {savedDeals.length === 0 ? (
          <div className="glass-panel" style={{padding: '80px 20px'}}>
            <div className="empty-state">
              <Heart className="empty-icon" size={50} style={{color: 'var(--text-muted)'}} />
              <h3 style={{marginBottom: '8px'}}>No Active Alerts</h3>
              <p>You haven't saved any deals or created price alerts yet. Try searching for products and save a deal.</p>
              <button className="btn-glow" style={{marginTop: '20px'}} onClick={() => setActiveTab('search')}>
                Start Searching
              </button>
            </div>
          </div>
        ) : (
          <div className="saved-grid">
            {savedDeals.map(deal => (
              <div key={deal.id} className="saved-card glass-panel">
                <div style={{height: '140px', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', borderBottom: '1px solid var(--border-color)', padding: '10px'}}>
                  <img src={deal.image_url} alt="" style={{maxHeight: '100%', maxWidth: '100%', objectFit: 'contain'}} />
                </div>
                <div className="saved-card-body">
                  <div className="saved-card-header">
                    <span className={`badge badge-platform ${deal.platform.toLowerCase()}`}>{deal.platform}</span>
                    <span style={{fontSize: '11px', color: 'var(--text-muted)'}}>
                      Saved {new Date(deal.date_saved).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="saved-card-title" title={deal.title}>{deal.title}</h3>
                  
                  <div className="saved-card-price-info">
                    <div className="saved-price-row">
                      <span className="saved-price-label">Price:</span>
                      <span className="saved-price-val">₹{deal.price.toLocaleString()}</span>
                    </div>
                    {deal.target_price && (
                      <div className="saved-alert-price">
                        <Bell size={13} />
                        Alert at ₹{deal.target_price.toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>

                <div className="saved-card-footer">
                  <button className="btn-outline" style={{color: 'var(--accent-rose)', borderColor: 'rgba(244,63,94,0.1)'}} onClick={() => handleUnsaveDeal(deal.id)}>
                    <Trash2 size={14} />
                    Unsave
                  </button>
                  <a href={deal.url} target="_blank" rel="noopener noreferrer" className="btn-glow" style={{padding: '10px 16px', fontSize: '13px'}}>
                    <ExternalLink size={14} />
                    View Store
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  function renderHistoryPage() {
    return (
      <div>
        <div className="heading-container">
          <h1 className="heading-title">Search History</h1>
          <p className="heading-desc">Review your past comparisons and quickly reload them.</p>
        </div>

        {historyList.length === 0 ? (
          <div className="glass-panel" style={{padding: '80px 20px'}}>
            <div className="empty-state">
              <History className="empty-icon" size={50} />
              <h3 style={{marginBottom: '8px'}}>History is Empty</h3>
              <p>Your search history will appear here once you conduct queries.</p>
            </div>
          </div>
        ) : (
          <div className="glass-panel" style={{padding: '20px 0'}}>
            <div style={{display: 'flex', flexDirection: 'column'}}>
              {historyList.map(h => (
                <div 
                  key={h.id} 
                  style={{
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between',
                    padding: '16px 30px',
                    borderBottom: '1px solid var(--border-color)',
                    cursor: 'pointer',
                    transition: 'var(--transition-smooth)'
                  }}
                  className="history-list-item"
                  onClick={() => handleSearch(h.query)}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '20px'}}>
                    <div style={{background: 'rgba(255,255,255,0.03)', padding: '10px', borderRadius: '10px', color: 'var(--primary)'}}>
                      <Clock size={18} />
                    </div>
                    <div>
                      <div style={{fontWeight: '700', fontSize: '15px'}}>{h.query}</div>
                      <div style={{display: 'flex', gap: '10px', marginTop: '4px', fontSize: '12px', color: 'var(--text-muted)'}}>
                        <span>Category: <strong>{h.category || 'General'}</strong></span>
                        <span>•</span>
                        <span>Deals Found: <strong>{h.results_count}</strong></span>
                      </div>
                    </div>
                  </div>

                  <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
                    <span style={{fontSize: '12px', color: 'var(--text-muted)'}}>
                      {new Date(h.timestamp).toLocaleString()}
                    </span>
                    <button className="btn-outline" style={{padding: '8px'}}>
                      <Search size={13} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }
}
