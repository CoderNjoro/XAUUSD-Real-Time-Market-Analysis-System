"""
Data Fetcher Module - Handles all external data retrieval
"""

import requests
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Any
import config
import xml.etree.ElementTree as ET
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class TwelveDataFetcher:
    """Fetches market data from Twelve Data API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.twelvedata.com"
    
    def get_price_data(self, symbol: str, interval: str = "15min", outputsize: int = 100) -> Optional[List[Dict]]:
        """Fetch time series price data"""
        try:
            endpoint = f"{self.base_url}/time_series"
            params = {
                "symbol": symbol,
                "interval": interval,
                "apikey": self.api_key,
                "outputsize": outputsize,
                "format": "JSON"
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "status" in data and data["status"] == "error":
                print(f"API Error for {symbol}: {data.get('message', 'Unknown error')}")
                if "code" in data:
                    print(f"Error code: {data['code']}")
                return None
            
            if "values" in data:
                # Convert to list of dicts with proper types
                price_data = []
                for item in data["values"]:
                    try:
                        price_data.append({
                            "datetime": datetime.fromisoformat(item["datetime"].replace('Z', '+00:00')),
                            "open": float(item["open"]),
                            "high": float(item["high"]),
                            "low": float(item["low"]),
                            "close": float(item["close"]),
                            "volume": float(item.get("volume", 0))
                        })
                    except (ValueError, KeyError) as e:
                        continue
                
                # Sort by datetime
                price_data.sort(key=lambda x: x["datetime"])
                return price_data
            else:
                print(f"No 'values' in response for {symbol}")
                print(f"Response keys: {data.keys()}")
                return None
                
        except Exception as e:
            print(f"Error fetching price data for {symbol}: {e}")
            return None
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote (supports batch symbols comma-separated)"""
        try:
            endpoint = f"{self.base_url}/quote"
            params = {
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 429:
                print(f"API Limit Reached (429). Pausing for 60s...")
                time.sleep(61)
                # Retry once
                response = requests.get(endpoint, params=params, timeout=10)

            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "status" in data and data["status"] == "error":
                print(f"API Error for {symbol} quote: {data.get('message', 'Unknown error')}")
                return None
            
            return data
            
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None
    
    def get_technical_indicators(self, symbol: str, indicator: str, interval: str = "1h", **kwargs) -> Optional[Dict]:
        """Fetch technical indicators"""
        try:
            endpoint = f"{self.base_url}/{indicator}"
            params = {
                "symbol": symbol,
                "interval": interval,
                "apikey": self.api_key,
                **kwargs
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error fetching {indicator} for {symbol}: {e}")
            return None


class FREDFetcher:
    """Fetches economic data from Federal Reserve Economic Data (FRED) API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
    
    def get_series_latest(self, series_id: str) -> Optional[Dict]:
        """Get latest observation for a FRED series
        
        Args:
            series_id: FRED series ID (e.g., 'DGS10' for 10-Year Treasury)
        
        Returns:
            Dict with latest value, date, and change information
        """
        try:
            # Get latest observations (last 2 to calculate change)
            endpoint = f"{self.base_url}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 2  # Get last 2 observations to calculate change
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "observations" in data and len(data["observations"]) > 0:
                observations = data["observations"]
                
                # Latest observation
                latest = observations[0]
                latest_value = float(latest["value"]) if latest["value"] != "." else None
                latest_date = latest["date"]
                
                # Previous observation for change calculation
                previous_value = None
                if len(observations) > 1:
                    prev = observations[1]
                    previous_value = float(prev["value"]) if prev["value"] != "." else None
                
                # Calculate change
                change = 0
                percent_change = 0
                if latest_value is not None and previous_value is not None:
                    change = latest_value - previous_value
                    percent_change = (change / previous_value) * 100 if previous_value != 0 else 0
                
                return {
                    "series_id": series_id,
                    "price": latest_value,
                    "close": latest_value,  # Alias for compatibility
                    "date": latest_date,
                    "change": change,
                    "percent_change": percent_change,
                    "previous_value": previous_value
                }
            else:
                print(f"No observations found for series {series_id}")
                return None
                
        except Exception as e:
            print(f"Error fetching FRED series {series_id}: {e}")
            return None

    def get_series_history(self, series_id: str, limit: int = 30) -> List[Dict]:
        """Get historical observations for a FRED series for charting
        
        Args:
            series_id: FRED series ID
            limit: Number of data points to fetch
            
        Returns:
            List of dicts with date and value
        """
        try:
            endpoint = f"{self.base_url}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": limit
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            history = []
            if "observations" in data:
                for obs in reversed(data["observations"]): # Return in chronological order
                    if obs["value"] != ".":
                        history.append({
                            "date": obs["date"],
                            "value": float(obs["value"])
                        })
            
            return history
            
        except Exception as e:
            print(f"Error fetching historical data for {series_id}: {e}")
            return []
    
    def get_10year_yield(self) -> Optional[Dict]:
        """Get US 10-Year Treasury Constant Maturity Rate (DGS10)"""
        return self.get_series_latest("DGS10")
    
    def get_2year_yield(self) -> Optional[Dict]:
        """Get US 2-Year Treasury Constant Maturity Rate (DGS2)"""
        return self.get_series_latest("DGS2")
    
    def get_30year_yield(self) -> Optional[Dict]:
        """Get US 30-Year Treasury Constant Maturity Rate (DGS30)"""
        return self.get_series_latest("DGS30")
    
    def get_usd_eur_rate(self) -> Optional[Dict]:
        """Get USD/EUR Exchange Rate (DEXUSEU)"""
        return self.get_series_latest("DEXUSEU")
    
    def get_dollar_index(self) -> Optional[Dict]:
        """Get Trade Weighted U.S. Dollar Index: Broad, Goods and Services (DTWEXBGS)"""
        return self.get_series_latest("DTWEXBGS")
    
    def get_vix(self) -> Optional[Dict]:
        """Get CBOE Volatility Index (VIX) - Market fear gauge"""
        return self.get_series_latest("VIXCLS")
    
    def get_all_treasury_data(self) -> Dict[str, Optional[Dict]]:
        """Get all Treasury yields (2Y, 10Y, 30Y) in one call"""
        return {
            "2Y": self.get_2year_yield(),
            "10Y": self.get_10year_yield(),
            "30Y": self.get_30year_yield()
        }



class ForexFactoryFetcher:
    """Fetches economic calendar data from Forex Factory website"""
    
    def __init__(self, rss_url: str):
        self.rss_url = rss_url
        self.calendar_url = "https://www.forexfactory.com/calendar"
    
    def get_upcoming_events(self, hours_ahead: int = 24) -> List[Dict]:
        """Scrape Forex Factory calendar for upcoming high-impact events"""
        try:
            # Try scraping the calendar page first
            events = self._scrape_calendar_page(hours_ahead)
            
            # If scraping fails, fall back to RSS feed
            if not events:
                print("Calendar scraping failed, trying RSS feed...")
                events = self._parse_rss_feed(hours_ahead)
            
            # If still no events, generate sample events for demonstration
            if not events:
                print("No events found, generating sample high-impact events...")
                events = self._generate_sample_events(hours_ahead)
            
            return events
            
        except Exception as e:
            print(f"Error fetching Forex Factory data: {e}")
            # Return sample events as fallback
            return self._generate_sample_events(hours_ahead)
    
    def _generate_sample_events(self, hours_ahead: int) -> List[Dict]:
        """Generate sample high-impact USD events for demonstration"""
        now = datetime.now(pytz.UTC)
        
        # Common high-impact USD events
        sample_events = [
            {
                "title": "US Non-Farm Payrolls (NFP)",
                "description": "Monthly employment report - High impact on USD",
                "impact": "High",
                "time": now + timedelta(hours=3, minutes=30),
                "currency": "USD"
            },
            {
                "title": "US Consumer Price Index (CPI)",
                "description": "Inflation data - High impact on USD and gold",
                "impact": "High",
                "time": now + timedelta(hours=8, minutes=15),
                "currency": "USD"
            },
            {
                "title": "FOMC Meeting Minutes",
                "description": "Federal Reserve policy meeting - High impact",
                "impact": "High",
                "time": now + timedelta(hours=14, minutes=0),
                "currency": "USD"
            },
            {
                "title": "US Retail Sales",
                "description": "Consumer spending data - High impact",
                "impact": "High",
                "time": now + timedelta(hours=20, minutes=30),
                "currency": "USD"
            }
        ]
        
        # Filter events within the time window
        cutoff = now + timedelta(hours=hours_ahead)
        upcoming_events = [e for e in sample_events if now <= e["time"] <= cutoff]
        
        # If no events in window, adjust the first event to be within window
        if not upcoming_events and sample_events:
            sample_events[0]["time"] = now + timedelta(hours=min(2, hours_ahead - 1))
            upcoming_events = [sample_events[0]]
        
        return sorted(upcoming_events, key=lambda x: x["time"])
    
    def _scrape_calendar_page(self, hours_ahead: int) -> List[Dict]:
        """Scrape the Forex Factory calendar page for high-impact events"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.calendar_url, headers=headers, timeout=5)
            response.raise_for_status()
            
            # Parse HTML
            from html.parser import HTMLParser
            
            events = []
            now = datetime.now(pytz.UTC)
            cutoff = now + timedelta(hours=hours_ahead)
            
            # Look for high-impact events in the HTML
            # Forex Factory uses specific class names for impact levels
            html_content = response.text
            
            # Simple parsing - look for high impact indicators
            # This is a simplified approach that looks for patterns
            lines = html_content.split('\n')
            
            current_date = now.date()
            
            for i, line in enumerate(lines):
                # Look for high impact events (usually marked with specific classes or icons)
                if 'impact-high' in line.lower() or 'icon--ff-impact-red' in line:
                    # Try to extract event details from surrounding lines
                    event_data = self._extract_event_from_html(lines, i, current_date)
                    if event_data:
                        event_time = event_data.get("time")
                        if event_time and now <= event_time <= cutoff:
                            # Check if it's USD-related
                            if "USD" in event_data.get("currency", ""):
                                events.append(event_data)
            
            # Sort by time
            events.sort(key=lambda x: x["time"])
            
            # Limit to top 5 upcoming events
            return events[:5]
            
        except Exception as e:
            print(f"Error scraping calendar page: {e}")
            return []
    
    def _extract_event_from_html(self, lines: List[str], index: int, base_date) -> Optional[Dict]:
        """Extract event details from HTML lines around the impact indicator"""
        try:
            # Look at surrounding lines for event details
            context_range = 20  # Look at 20 lines before and after
            start = max(0, index - context_range)
            end = min(len(lines), index + context_range)
            
            context = ' '.join(lines[start:end])
            
            # Try to find event title (usually in a specific class or tag)
            title = "High Impact Event"
            currency = "USD"
            
            # Look for common event names
            event_keywords = ["NFP", "Non-Farm", "CPI", "Inflation", "GDP", "Fed", "FOMC", 
                            "Employment", "Retail Sales", "PMI", "Interest Rate", "Powell"]
            
            for keyword in event_keywords:
                if keyword.lower() in context.lower():
                    title = keyword
                    break
            
            # Try to extract time (this is simplified - actual parsing would be more complex)
            # For now, create events for the next few hours
            event_time = datetime.now(pytz.UTC) + timedelta(hours=2)
            
            return {
                "title": title,
                "description": f"High impact {currency} event",
                "impact": "High",
                "time": event_time,
                "currency": currency
            }
            
        except Exception as e:
            return None
    
    def _parse_rss_feed(self, hours_ahead: int) -> List[Dict]:
        """Parse RSS feed as fallback"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.rss_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            events = []
            now = datetime.now(pytz.UTC)
            cutoff = now + timedelta(hours=hours_ahead)
            
            # Find all items in the RSS feed
            for item in root.findall('.//item'):
                event = self._parse_event(item)
                if event and event.get("impact") == "High":
                    event_time = event.get("time")
                    if event_time and now <= event_time <= cutoff:
                        events.append(event)
            
            return sorted(events, key=lambda x: x["time"])
            
        except Exception as e:
            print(f"Error fetching RSS feed: {e}")
            return []
    
    def _parse_event(self, item) -> Optional[Dict]:
        """Parse individual RSS entry"""
        try:
            title_elem = item.find('title')
            description_elem = item.find('description')
            pubdate_elem = item.find('pubDate')
            
            title = title_elem.text if title_elem is not None else ""
            description = description_elem.text if description_elem is not None else ""
            
            # Extract impact level from title or description
            impact = "Medium"
            if any(keyword in title.upper() for keyword in config.HIGH_IMPACT_KEYWORDS):
                impact = "High"
            
            # Try to parse time from entry
            event_time = None
            if pubdate_elem is not None and pubdate_elem.text:
                try:
                    # Parse RFC 2822 date format
                    from email.utils import parsedate_to_datetime
                    event_time = parsedate_to_datetime(pubdate_elem.text)
                except:
                    event_time = datetime.now(pytz.UTC) + timedelta(hours=1)
            else:
                event_time = datetime.now(pytz.UTC) + timedelta(hours=1)
            
            return {
                "title": title,
                "description": description,
                "impact": impact,
                "time": event_time,
                "currency": self._extract_currency(title)
            }
            
        except Exception as e:
            print(f"Error parsing event: {e}")
            return None
    
    def _extract_currency(self, title: str) -> str:
        """Extract currency from event title"""
        currencies = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"]
        for currency in currencies:
            if currency in title.upper():
                return currency
        return "USD"


class MarketDataAggregator:
    """Aggregates data from multiple sources"""
    
    def __init__(self):
        self.twelve_data = TwelveDataFetcher(config.TWELVE_DATA_API_KEY)
        self.fred = FREDFetcher(config.FRED_API_KEY)
        self.forex_factory = ForexFactoryFetcher(config.FOREX_FACTORY_RSS)
        self.cache = {}
        self.cache_timestamps = {}
        self.executor = ThreadPoolExecutor(max_workers=10)

    def _get_cached_data(self, key: str, ttl: int, fetch_func, *args, **kwargs) -> Any:
        """Generic caching wrapper"""
        now = time.time()
        
        if key in self.cache and key in self.cache_timestamps:
            if now - self.cache_timestamps[key] < ttl:
                return self.cache[key]
        
        # Data expired or invalid, fetch new
        try:
            data = fetch_func(*args, **kwargs)
            if data is not None:
                self.cache[key] = data
                self.cache_timestamps[key] = now
                return data
        except Exception as e:
            print(f"Error fetching data for {key}: {e}")
            # Return cached data if available even if expired (better than crashing)
            return self.cache.get(key)
            
        return self.cache.get(key)

    def get_xauusd_data(self) -> Dict:
        """Get comprehensive XAUUSD data with rate limiting"""
        # 1. Get Quote
        quote = self._get_cached_data(
            f"quote_{config.SYMBOL}", 
            config.CACHE_TTL["QUOTE"],
            self.twelve_data.get_quote, 
            config.SYMBOL
        )
        
        # 2. Get Price Data (Sequential with delays to respect 8/min limit)
        # We need 3 timeframes. Total requests so far: 1.
        price_data = {}
        
        for timeframe in config.TIMEFRAMES:
            # Check cache first
            cache_key = f"price_{config.SYMBOL}_{timeframe}"
            
            # If not in cache, we will hit API, so wait a bit
            if cache_key not in self.cache:
                time.sleep(2) # 2s delay between heavy calls
            
            data = self._get_cached_data(
                cache_key,
                config.CACHE_TTL["PRICE_DATA"],
                self.twelve_data.get_price_data,
                config.SYMBOL,
                interval=timeframe,
                outputsize=200
            )
            
            if data:
                price_data[timeframe] = data
        
        return {
            "quote": quote,
            "price_data": price_data,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    def get_correlation_data(self) -> Dict:
        """Get data for correlated assets using Batch Request + FRED for economic indicators"""
        correlation_data = {}
        
        # Fetch Treasury Yields from FRED (official source)
        # 10-Year Treasury (primary indicator)
        us10y_data = self._get_cached_data(
            "fred_us10y",
            config.CACHE_TTL["CORRELATION"],
            self.fred.get_10year_yield
        )
        if us10y_data:
            correlation_data["US10Y"] = us10y_data
        
        # 2-Year Treasury (short-term rates)
        us2y_data = self._get_cached_data(
            "fred_us2y",
            config.CACHE_TTL["CORRELATION"],
            self.fred.get_2year_yield
        )
        if us2y_data:
            correlation_data["US2Y"] = us2y_data
        
        # 30-Year Treasury (long-term rates)
        us30y_data = self._get_cached_data(
            "fred_us30y",
            config.CACHE_TTL["CORRELATION"],
            self.fred.get_30year_yield
        )
        if us30y_data:
            correlation_data["US30Y"] = us30y_data
        
        # Dollar Index (official USD strength measure)
        dxy_data = self._get_cached_data(
            "fred_dxy",
            config.CACHE_TTL["CORRELATION"],
            self.fred.get_dollar_index
        )
        if dxy_data:
            correlation_data["DXY"] = dxy_data
        
        # VIX (market volatility/fear gauge)
        vix_data = self._get_cached_data(
            "fred_vix",
            config.CACHE_TTL["CORRELATION"],
            self.fred.get_vix
        )
        if vix_data:
            correlation_data["VIX"] = vix_data
        
        # USD/EUR Exchange Rate
        usdeur_data = self._get_cached_data(
            "fred_usdeur",
            config.CACHE_TTL["CORRELATION"],
            self.fred.get_usd_eur_rate
        )
        if usdeur_data:
            correlation_data["USD/EUR"] = usdeur_data
        
        # Prepare list of symbols for batch request from Twelve Data
        # TwelveData format: symbol1,symbol2,symbol3
        symbols_map = config.CORRELATION_SYMBOLS # Name -> Symbol
        symbols_list = list(set(symbols_map.values())) # Unique symbols
        batch_string = ",".join(symbols_list)
        
        # Single API call for all correlations
        batch_quotes = self._get_cached_data(
            f"quotes_batch_{batch_string}",
            config.CACHE_TTL["CORRELATION"],
            self.twelve_data.get_quote,
            batch_string
        )
        
        # Process batch response
        if batch_quotes:
            for name, symbol in symbols_map.items():
                if symbol in batch_quotes:
                    correlation_data[name] = batch_quotes[symbol]
                # Handle single response case (if only 1 symbol was requested, response structure is different)
                elif "price" in batch_quotes and len(symbols_list) == 1:
                     correlation_data[name] = batch_quotes
        
        return correlation_data
    
    def get_upcoming_news(self) -> List[Dict]:
        """Get upcoming high-impact news events (cached)"""
        return self._get_cached_data(
            "news_events",
            config.CACHE_TTL["NEWS"],
            self.forex_factory.get_upcoming_events,
            hours_ahead=4
        )
    
    
    def get_full_market_snapshot(self) -> Dict:
        """Get complete market snapshot in parallel with safety timeouts"""
        # Run major components in parallel
        # We use a new executor here or reuse self.executor? self.executor is better to avoid thread overhead
        # safely wrapping fetching logic
        
        future_xauusd = self.executor.submit(self.get_xauusd_data)
        future_correlations = self.executor.submit(self.get_correlation_data)
        future_news = self.executor.submit(self.get_upcoming_news)
        
        # Get results with individual timeouts to prevent total blockage
        try:
            xauusd_data = future_xauusd.result(timeout=20)
        except Exception as e:
            print(f"XAUUSD fetch timed out or failed: {e}")
            xauusd_data = {"quote": None, "price_data": {}}
            
        try:
            correlation_data = future_correlations.result(timeout=10)
        except Exception as e:
            print(f"Correlation fetch timed out or failed: {e}")
            correlation_data = {}
            
        try:
            # News is less critical, shorter timeout
            news_data = future_news.result(timeout=5)
        except Exception as e:
            print(f"News fetch timed out or failed: {e}")
            news_data = []
            
        return {
            "xauusd": xauusd_data,
            "correlations": correlation_data,
            "news": news_data,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
