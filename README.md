# XAUUSD Real-Time Market Analysis System

A professional, real-time market analysis dashboard for XAUUSD (Gold) trading with multi-timeframe technical analysis, correlation tracking, and economic calendar integration.

![Dashboard Preview](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

### Core Components

1. **News/Event Tracker**
   - Monitors economic calendars via Forex Factory RSS feed
   - Flags high-impact USD data releases (NFP, CPI, Fed decisions)
   - Alerts for events 15-60 minutes ahead
   - Measures actual vs expected deviations

2. **Correlation Dashboard**
   - Real-time tracking of:
     - US 10-Year Treasury Yield (inverse correlation)
     - DXY (USD Index)
     - S&P 500 futures (risk sentiment)
     - Bitcoin (alternative asset flow)

3. **Technical Level Monitor**
   - Multi-timeframe analysis (15-min, 1-hour, 4-hour)
   - Key support/resistance identification
   - Previous day high/low and weekly pivots
   - 50 & 200-period moving averages
   - RSI extremes monitoring

4. **Time & Liquidity Awareness**
   - Current trading session display
   - Session overlap tracking
   - Volume profile analysis

### Alert Triggers

- Price within 0.2% of major technical levels
- Yield moves >5bps in 15 minutes
- DXY breaks significant levels
- 15-min volume 50% above average
- High-impact news in next 30 minutes

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   - API keys are already configured in `config.py`
   - Twelve Data API: `e66f23af924748319c7aea637eb54fac`
   - Forex Factory RSS: Automatic feed parsing

## 📊 Usage

### Starting the Application

**Windows:**
```bash
python app.py
```

**The server will start on:** `http://localhost:5000`

### Accessing the Dashboard

1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. The dashboard will automatically connect and start receiving real-time updates

### Features

- **Automatic Updates**: Market data refreshes every 15 minutes
- **Manual Refresh**: Click "Update Now" button for immediate data fetch
- **Real-time WebSocket**: Live updates without page refresh
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🎨 Dashboard Sections

### 1. Price Overview
- Current XAUUSD price with large, prominent display
- 1-hour price change percentage
- Active trading session indicator
- Next session overlap countdown

### 2. Market Drivers
- Primary driver identification (Technical/Fundamental/Sentiment/Liquidity)
- Momentum strength and direction

### 3. Correlation Dashboard
Four correlation cards showing:
- **Yield Watch**: 10-Year Treasury with basis point changes
- **USD Watch**: DXY with percentage changes
- **Risk Gauge**: S&P 500 futures sentiment
- **Bitcoin**: Alternative asset tracking

### 4. Technical Analysis
- Nearest support level with pip distance
- Nearest resistance level with pip distance
- Moving average alignment (Bullish/Bearish/Neutral)
- RSI(14) with overbought/oversold status

### 5. Next Catalyst
- Upcoming high-impact economic events
- Time until event
- Event impact level

### 6. Alert Conditions
- Active alerts for trading opportunities
- Color-coded by severity
- Real-time alert updates

## 🛠️ Technical Stack

### Backend
- **Flask**: Web framework
- **Flask-SocketIO**: Real-time WebSocket communication
- **Pandas**: Data manipulation and analysis
- **Requests**: API data fetching
- **Feedparser**: RSS feed parsing
- **TA**: Technical analysis indicators

### Frontend
- **HTML5**: Semantic structure
- **CSS3**: Modern styling with glassmorphism
- **Vanilla JavaScript**: Real-time updates
- **Socket.IO Client**: WebSocket communication
- **Google Fonts**: Inter & JetBrains Mono

### Data Sources
- **Twelve Data API**: Market data and quotes
- **Forex Factory RSS**: Economic calendar events

## 📁 Project Structure

```
Forexpresictionsystem/
├── app.py                      # Flask application & WebSocket server
├── config.py                   # Configuration and API keys
├── data_fetcher.py            # Data retrieval from APIs
├── technical_analysis.py      # Technical indicators & analysis
├── market_analysis.py         # Market analysis engine
├── requirements.txt           # Python dependencies
├── templates/
│   └── index.html            # Main dashboard HTML
├── static/
│   ├── css/
│   │   └── styles.css        # Dashboard styling
│   └── js/
│       └── app.js            # Frontend application logic
└── README.md                 # This file
```

## ⚙️ Configuration

Edit `config.py` to customize:

- **Update intervals**: Change `UPDATE_INTERVAL` (default: 900 seconds / 15 minutes)
- **Technical settings**: Modify RSI periods, MA periods, alert thresholds
- **Trading sessions**: Adjust session times for different timezones
- **Alert sensitivity**: Change proximity percentages for alerts

## 🎯 Output Format

Every 15 minutes, the system generates a comprehensive snapshot:

```
[Timestamp]
XAUUSD: $XXXX.XX | Change: +X.XX% (1hr) | Session: [LONDON/NY/ASIAN]

PRIMARY DRIVER: [Technical/Fundamental/Liquidity/Sentiment]
MOMENTUM: [Strong/Moderate/Weak] [Bullish/Bearish]

KEY MONITORS:
YIELD WATCH: 10Y @ X.XX% (▲▼ Xbps) → Gold Pressure: Up/Down
USD WATCH: DXY @ XX.XX (▲▼ X%) → Inverse Pressure: Strong/Weak
RISK GAUGE: SPX futures ▲▼ X% → Haven Demand: High/Low

TECHNICALS:
• Nearest Support: $XXXX (X pips below)
• Nearest Resistance: $XXXX (X pips above)
• MA Alignment: [Bullish/Bearish/Neutral]
• RSI(14): XX [Overbought/Oversold/Neutral]

NEXT CATALYST: [Event] at [Time] in [X minutes] | Impact: [High/Medium]

ALERT CONDITIONS: [None/Approaching Key Level/High Impact News Due]
```

## 🎨 Design Features

- **Dark Theme**: Professional trading terminal aesthetic
- **Gold Accents**: Premium color scheme matching XAUUSD
- **Glassmorphism**: Modern glass-card effects
- **Smooth Animations**: Micro-interactions for better UX
- **Responsive Layout**: Adapts to all screen sizes
- **Real-time Updates**: Live data without page refresh

## 🔧 Troubleshooting

### Connection Issues
- Ensure port 5000 is not in use
- Check firewall settings
- Verify internet connection for API access

### API Errors
- Twelve Data API has rate limits (free tier: 8 API calls/minute)
- If you see errors, wait a few minutes before retrying
- Consider upgrading API plan for higher limits

### No Data Displayed
- Wait for first update cycle (up to 15 minutes)
- Click "Update Now" to force immediate fetch
- Check browser console for errors (F12)

## 📝 Notes

- **API Rate Limits**: The free Twelve Data API has limitations. The system is optimized to stay within limits.
- **Market Hours**: Data quality is best during active trading sessions
- **News Feed**: Forex Factory RSS may have delays; cross-reference with other sources
- **Educational Purpose**: This tool is for analysis and education, not financial advice

## 🚀 Future Enhancements

Potential improvements:
- [ ] Historical data charting
- [ ] Trade signal generation
- [ ] Email/SMS alert notifications
- [ ] Multiple symbol support
- [ ] Machine learning price predictions
- [ ] Backtesting capabilities
- [ ] Mobile app version

## 📄 License

MIT License - Feel free to use and modify for your needs

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## ⚠️ Disclaimer

This software is for educational and informational purposes only. It does not constitute financial advice. Trading involves risk, and you should never trade with money you cannot afford to lose. Always do your own research and consult with a qualified financial advisor.

---

**Built with ❤️ for traders who demand professional-grade analysis tools**
