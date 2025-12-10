"""
Configuration file for XAUUSD Market Analysis System
"""

# API Configuration
TWELVE_DATA_API_KEY = "e66f23af924748319c7aea637eb54fac"
FRED_API_KEY = "1a099848d7dc45964df8c7fc342476b6"  # Federal Reserve Economic Data
FOREX_FACTORY_RSS = "https://www.forexfactory.com/rss"

# Market Configuration
# Note: Twelve Data API uses specific symbol formats:
# - Forex pairs: XAU/USD, EUR/USD, etc. (with slash)
# - Indices: DXY, SPX, NDX, etc. (no slash)
# - Crypto: BTC/USD, ETH/USD, etc. (with slash)
# - Bonds: US10Y, US02Y, etc. (no slash)
# Some symbols may require a paid API plan. Free tier has limitations.

SYMBOL = "XAU/USD"  # Gold vs US Dollar

# Timeframes for technical analysis
TIMEFRAMES = ["15min", "1h", "4h"]

# CORRELATION SYMBOLS - Choose one configuration below:

# Option 1: IDEAL CONFIGURATION (requires paid Twelve Data plan)
# Uncomment this for full functionality with all intended correlations
# CORRELATION_SYMBOLS = {
#     "US10Y": "US10Y",      # US 10-Year Treasury Yield
#     "DXY": "DXY",          # US Dollar Index
#     "SPX": "SPX",          # S&P 500
#     "BTC/USD": "BTC/USD"   # Bitcoin
# }

# Option 2: FREE TIER FRIENDLY (currently active)
# These symbols are more likely to work on the free tier
CORRELATION_SYMBOLS = {
    "EUR/USD": "EUR/USD",    # Euro (inverse to USD strength, substitute for DXY)
    "USD/JPY": "USD/JPY",    # Yen (direct to USD strength)
    "GBP/USD": "GBP/USD",    # Pound (risk sentiment, substitute for SPX)
    "BTC/USD": "BTC/USD"     # Bitcoin (alternative asset)
}

# Technical Analysis Settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MA_PERIODS = [50, 200]
LEVEL_PROXIMITY_PERCENT = 0.3  # Alert when within 0.3% of key level
ALERT_PROXIMITY_PERCENT = 0.2  # Critical alert at 0.2%

# Volume Settings
VOLUME_LOOKBACK_DAYS = 20
HIGH_VOLUME_THRESHOLD = 1.5  # 50% above average

# Yield Alert Settings
YIELD_ALERT_BPS = 5  # Alert on 5 basis point moves in 15 minutes

# Update Intervals (in seconds)
UPDATE_INTERVAL = 900  # 15 minutes
FAST_UPDATE_INTERVAL = 60  # 1 minute for critical data

# Trading Sessions (UTC times)
SESSIONS = {
    "ASIAN": {"start": "00:00", "end": "09:00"},
    "LONDON": {"start": "08:00", "end": "17:00"},
    "NY": {"start": "13:00", "end": "22:00"}
}

# News Impact Levels
HIGH_IMPACT_KEYWORDS = [
    "NFP", "Non-Farm Payroll", "CPI", "Consumer Price Index",
    "FOMC", "Federal Reserve", "Fed", "Interest Rate",
    "GDP", "Employment", "Inflation", "Powell"
]

# Cache Settings (in seconds)
CACHE_TTL = {
    "PRICE_DATA": 300,  # 5 minutes for historical candles
    "QUOTE": 30,        # 30 seconds for real-time quotes
    "NEWS": 3600,       # 1 hour for news (doesn't change often)
    "CORRELATION": 60   # 1 minute for correlated assets
}
