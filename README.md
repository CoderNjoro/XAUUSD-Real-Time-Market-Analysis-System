# XAUUSD Real-Time Market Analysis System

A professional, real-time market analysis dashboard for XAUUSD (Gold) trading with multi-timeframe technical analysis, correlation tracking, and economic calendar integration.


## Overview

A comprehensive trading analytics platform designed for XAUUSD (Gold/USD) that provides real-time market monitoring, technical analysis, and correlation tracking. The system integrates multiple data sources to deliver actionable insights for traders.

## Features

### Market Intelligence
- **Economic Calendar Integration**: Monitors high-impact USD data releases via Forex Factory RSS feed
- **Real-time Correlation Tracking**: Simultaneous monitoring of Treasury yields, DXY, S&P 500, and Bitcoin
- **Multi-timeframe Analysis**: Technical analysis across 15-minute, 1-hour, and 4-hour timeframes
- **Liquidity Awareness**: Trading session tracking and volume profile analysis

### Technical Analysis
- **Support & Resistance**: Dynamic identification of key price levels
- **Moving Averages**: 50 & 200-period MA alignment monitoring
- **Momentum Indicators**: RSI extremes and trend strength analysis
- **Pivot Points**: Previous day high/low and weekly pivot calculations

### Alert System
- Price proximity alerts (within 0.2% of key levels)
- Yield movement alerts (>5bps in 15 minutes)
- DXY breakout notifications
- Volume spike detection (50% above average)
- Pre-news event warnings

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/xauusd-analysis-system.git
   cd xauusd-analysis-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**
   ```bash
   python app.py
   ```

4. **Access the dashboard**
   Open your browser and navigate to: `http://localhost:5000`

## Dashboard Interface

### Price Overview Section
- Current XAUUSD price with large display
- 1-hour percentage change
- Active trading session indicator
- Next session overlap timer

### Market Drivers
- Primary market driver identification
- Momentum strength and direction indicators
- Real-time sentiment analysis

### Correlation Matrix
- **Yield Watch**: 10-Year Treasury yields with basis point changes
- **USD Watch**: DXY index with percentage movements
- **Risk Gauge**: S&P 500 futures sentiment indicator
- **Bitcoin Monitor**: Alternative asset correlation tracking

### Technical Analysis Panel
- Nearest support and resistance levels
- Moving average alignment status
- RSI(14) reading with overbought/oversold indicators

### Event Tracker
- Upcoming high-impact economic events
- Countdown to next catalyst
- Expected market impact assessment

### Alert Center
- Active trading alerts
- Color-coded priority system
- Real-time notification updates

## System Architecture

### Backend Components
- **Flask**: Lightweight web framework
- **Flask-SocketIO**: Real-time bidirectional communication
- **Pandas**: Data manipulation and analysis
- **Requests**: HTTP library for API calls
- **TA-Lib**: Technical analysis library

### Frontend Components
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Dynamic content updates
- **Socket.IO Client**: WebSocket communication
- **Glassmorphism UI**: Contemporary visual design

### Data Sources
- **Twelve Data API**: Real-time market data
- **Forex Factory RSS**: Economic calendar events
- **Public APIs**: Treasury yields, DXY, S&P 500 futures

## Project Structure

```
xauusd-analysis-system/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── data_fetcher.py            # API data retrieval
├── technical_analysis.py      # Technical indicators
├── market_analysis.py         # Market analysis logic
├── requirements.txt           # Python dependencies
├── templates/
│   └── index.html            # Dashboard template
├── static/
│   ├── css/
│   │   └── styles.css        # Custom styling
│   └── js/
│       └── app.js            # Frontend logic
└── README.md                 # Documentation
```

## Configuration

Customize system behavior by modifying `config.py`:

- **Update Interval**: Adjust data refresh rate (default: 900 seconds)
- **Alert Thresholds**: Modify sensitivity for price and yield alerts
- **Trading Sessions**: Customize session times for different timezones
- **Technical Parameters**: Configure RSI periods, MA settings

## Output Format

The system generates structured market analysis every 15 minutes:

```
[Timestamp]
XAUUSD: $XXXX.XX | Change: +X.XX% (1hr) | Session: [Active Session]

PRIMARY DRIVER: [Technical/Fundamental/Liquidity/Sentiment]
MOMENTUM: [Strength] [Direction]

KEY CORRELATIONS:
• Yield: 10Y @ X.XX% (Change: Xbps) → Gold Pressure: Direction
• USD: DXY @ XX.XX (Change: X%) → Inverse Correlation: Strength
• Risk: SPX futures (Change: X%) → Haven Demand: Level

TECHNICAL LEVELS:
• Nearest Support: $XXXX (Distance: X pips)
• Nearest Resistance: $XXXX (Distance: X pips)
• MA Alignment: [Bullish/Bearish/Neutral]
• RSI(14): XX [Status]

NEXT CATALYST: [Event Name] at [Time] (in X minutes) | Impact: [High/Medium/Low]

ACTIVE ALERTS: [Alert Count] [Alert Details]
```

## Troubleshooting

### Common Issues

**Connection Problems**
- Ensure port 5000 is available
- Check firewall settings
- Verify network connectivity

**API Limitations**
- Twelve Data API free tier: 8 calls/minute
- Implement rate limiting in code
- Consider API plan upgrade for higher usage

**Data Display Issues**
- Wait for initial data fetch (up to 15 minutes)
- Use "Update Now" for manual refresh
- Check browser console for errors (F12)

## Development Roadmap

### Planned Enhancements
- Historical data visualization with charts
- Automated trade signal generation
- Email and SMS notification system
- Multi-asset class support
- Machine learning price prediction models
- Backtesting framework
- Mobile application version

## License

MIT License - See LICENSE file for details.

## Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## Disclaimer

This software is for educational and informational purposes only. It does not constitute financial advice. Trading financial instruments involves substantial risk of loss. Always conduct your own research and consult with qualified financial professionals before making investment decisions.
**
**Screenshots****

<img width="1366" height="495" alt="10 12 2025_15 36 57_REC" src="https://github.com/user-attachments/assets/0ee02aeb-d795-4855-b33e-b3d3b1701676" />
<img width="1366" height="598" alt="10 12 2025_15 37 20_REC" src="https://github.com/user-attachments/assets/f03f3061-35f6-427b-9344-b85c36660780" />
<img width="1356" height="593" alt="10 12 2025_15 37 54_REC" src="https://github.com/user-attachments/assets/0a42d04e-855a-479e-98e2-6cbd1121ac87" />



---

**Professional trading analytics for informed decision making**
