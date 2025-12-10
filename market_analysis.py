"""
Market Analysis Engine - Combines all data sources and generates insights
"""

from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional
import config
from data_fetcher import MarketDataAggregator
from technical_analysis import TechnicalAnalyzer


class MarketAnalysisEngine:
    """Main engine for market analysis and signal generation"""
    
    def __init__(self):
        self.data_aggregator = MarketDataAggregator()
        self.technical_analyzer = TechnicalAnalyzer()
        self.previous_data = {}
    
    def get_current_session(self) -> str:
        """Determine current trading session"""
        now = datetime.now(pytz.UTC)
        current_time = now.strftime("%H:%M")
        
        sessions_active = []
        for session, times in config.SESSIONS.items():
            start = times["start"]
            end = times["end"]
            
            if start <= current_time <= end:
                sessions_active.append(session)
        
        if len(sessions_active) > 1:
            return "/".join(sessions_active)
        elif len(sessions_active) == 1:
            return sessions_active[0]
        else:
            return "OFF-HOURS"
    
    def get_next_session_overlap(self) -> Optional[Dict]:
        """Calculate time until next session overlap"""
        now = datetime.now(pytz.UTC)
        
        # London/NY overlap is most significant (13:00-17:00 UTC)
        overlap_start = now.replace(hour=13, minute=0, second=0, microsecond=0)
        
        if now.hour >= 17:
            overlap_start += timedelta(days=1)
        elif now.hour < 13:
            pass  # Use today's overlap
        else:
            return {"session": "LONDON/NY", "minutes_until": 0, "active": True}
        
        minutes_until = int((overlap_start - now).total_seconds() / 60)
        
        return {
            "session": "LONDON/NY",
            "minutes_until": minutes_until,
            "active": False
        }
    
    def analyze_correlations(self, correlation_data: Dict) -> Dict:
        """Analyze correlation data and determine pressure on gold"""
        analysis = {}
        
        # US 10-Year Yield (inverse correlation with gold)
        if "US10Y" in correlation_data:
            us10y = correlation_data["US10Y"]
            price = float(us10y.get("price", us10y.get("close", 0)))
            change = float(us10y.get("change", 0))
            percent_change = float(us10y.get("percent_change", 0))
            
            # Convert percent change to basis points
            bps_change = percent_change * 100
            
            pressure = "Down" if change > 0 else "Up" if change < 0 else "Neutral"
            
            analysis["yield"] = {
                "price": price,
                "change_bps": bps_change,
                "pressure": pressure,
                "direction": "▲" if change > 0 else "▼" if change < 0 else "→"
            }
        
        # US 2-Year Yield (short-term rates, Fed policy indicator)
        if "US2Y" in correlation_data:
            us2y = correlation_data["US2Y"]
            price = float(us2y.get("price", us2y.get("close", 0)))
            change = float(us2y.get("change", 0))
            percent_change = float(us2y.get("percent_change", 0))
            bps_change = percent_change * 100
            
            analysis["yield_2y"] = {
                "price": price,
                "change_bps": bps_change,
                "direction": "▲" if change > 0 else "▼" if change < 0 else "→"
            }
        
        # US 30-Year Yield (long-term rates)
        if "US30Y" in correlation_data:
            us30y = correlation_data["US30Y"]
            price = float(us30y.get("price", us30y.get("close", 0)))
            change = float(us30y.get("change", 0))
            percent_change = float(us30y.get("percent_change", 0))
            bps_change = percent_change * 100
            
            analysis["yield_30y"] = {
                "price": price,
                "change_bps": bps_change,
                "direction": "▲" if change > 0 else "▼" if change < 0 else "→"
            }
        
        # Calculate Yield Curve (if we have both 2Y and 10Y)
        if "yield_2y" in analysis and "yield" in analysis:
            spread = analysis["yield"]["price"] - analysis["yield_2y"]["price"]
            analysis["yield_curve"] = {
                "spread": spread,
                "status": "Normal" if spread > 0 else "Inverted" if spread < -0.1 else "Flat"
            }
        
        # VIX (market volatility/fear gauge - direct correlation with gold as safe haven)
        if "VIX" in correlation_data:
            vix = correlation_data["VIX"]
            price = float(vix.get("price", vix.get("close", 0)))
            percent_change = float(vix.get("percent_change", 0))
            
            # VIX interpretation
            fear_level = "Extreme Fear" if price > 30 else "High Fear" if price > 20 else "Moderate" if price > 15 else "Low Fear"
            haven_demand = "Very High" if price > 30 else "High" if price > 20 else "Moderate" if price > 15 else "Low"
            
            analysis["vix"] = {
                "price": price,
                "percent_change": percent_change,
                "fear_level": fear_level,
                "haven_demand": haven_demand,
                "direction": "▲" if percent_change > 0 else "▼" if percent_change < 0 else "→"
            }
        
        # DXY (inverse correlation with gold) - Now from FRED official data
        if "DXY" in correlation_data:
            dxy = correlation_data["DXY"]
            price = float(dxy.get("price", dxy.get("close", 0)))
            percent_change = float(dxy.get("percent_change", 0))
            
            pressure_strength = "Strong" if abs(percent_change) > 0.5 else "Weak"
            pressure = f"{pressure_strength} Inverse"
            
            analysis["dxy"] = {
                "price": price,
                "percent_change": percent_change,
                "pressure": pressure,
                "direction": "▲" if percent_change > 0 else "▼" if percent_change < 0 else "→",
                "source": "FRED"
            }
        elif "USD/EUR" in correlation_data:
            # USD/EUR from FRED (inverse of EUR/USD)
            usdeur = correlation_data["USD/EUR"]
            price = float(usdeur.get("price", usdeur.get("close", 0)))
            percent_change = float(usdeur.get("percent_change", 0))
            
            # USD/EUR up = USD strong = bad for gold
            pressure_strength = "Strong" if abs(percent_change) > 0.5 else "Weak"
            pressure = f"{pressure_strength} Inverse"
            
            analysis["dxy"] = {
                "price": price,
                "percent_change": percent_change,
                "pressure": pressure,
                "direction": "▲" if percent_change > 0 else "▼" if percent_change < 0 else "→",
                "symbol": "USD/EUR",
                "source": "FRED"
            }
        elif "EUR/USD" in correlation_data:
            # EUR/USD as substitute for DXY (inverse relationship)
            eur = correlation_data["EUR/USD"]
            price = float(eur.get("price", eur.get("close", 0)))
            percent_change = float(eur.get("percent_change", 0))
            
            # EUR/USD up = USD weak = good for gold
            # EUR/USD down = USD strong = bad for gold
            pressure_strength = "Strong" if abs(percent_change) > 0.5 else "Weak"
            pressure = f"{pressure_strength} Direct" if percent_change > 0 else f"{pressure_strength} Inverse"
            
            analysis["dxy"] = {
                "price": price,
                "percent_change": percent_change,
                "pressure": pressure,
                "direction": "▲" if percent_change > 0 else "▼" if percent_change < 0 else "→",
                "symbol": "EUR/USD"
            }
        elif "USD/JPY" in correlation_data:
            # USD/JPY as substitute for DXY (direct relationship)
            usdjpy = correlation_data["USD/JPY"]
            price = float(usdjpy.get("price", usdjpy.get("close", 0)))
            percent_change = float(usdjpy.get("percent_change", 0))
            
            pressure_strength = "Strong" if abs(percent_change) > 0.5 else "Weak"
            pressure = f"{pressure_strength} Inverse"
            
            analysis["dxy"] = {
                "price": price,
                "percent_change": percent_change,
                "pressure": pressure,
                "direction": "▲" if percent_change > 0 else "▼" if percent_change < 0 else "→",
                "symbol": "USD/JPY"
            }
        
        # S&P 500 (risk sentiment) OR GBP/USD (risk sentiment proxy) OR VIX (already handled above)
        if "SPX" in correlation_data:
            spx = correlation_data["SPX"]
            percent_change = float(spx.get("percent_change", 0))
            
            haven_demand = "Low" if percent_change > 0.5 else "High" if percent_change < -0.5 else "Moderate"
            
            analysis["risk"] = {
                "percent_change": percent_change,
                "haven_demand": haven_demand,
                "direction": "▲" if percent_change > 0 else "▼" if percent_change < 0 else "→"
            }
        elif "GBP/USD" in correlation_data:
            # GBP/USD as risk sentiment proxy
            gbp = correlation_data["GBP/USD"]
            percent_change = float(gbp.get("percent_change", 0))
            
            # GBP/USD up = risk on = lower haven demand
            # GBP/USD down = risk off = higher haven demand
            haven_demand = "Low" if percent_change > 0.5 else "High" if percent_change < -0.5 else "Moderate"
            
            analysis["risk"] = {
                "percent_change": percent_change,
                "haven_demand": haven_demand,
                "direction": "▲" if percent_change > 0 else "▼" if percent_change < 0 else "→",
                "symbol": "GBP/USD"
            }
        
        # Bitcoin (alternative asset)
        if "BTC/USD" in correlation_data:
            btc = correlation_data["BTC/USD"]
            price = float(btc.get("price", btc.get("close", 0)))
            percent_change = float(btc.get("percent_change", 0))
            
            analysis["btc"] = {
                "price": price,
                "percent_change": percent_change,
                "direction": "▲" if percent_change > 0 else "▼" if percent_change < 0 else "→"
            }
        
        return analysis
    
    def determine_primary_driver(self, technical_data: Dict, news_events: List, correlation_analysis: Dict) -> str:
        """Determine the primary market driver"""
        # Check for upcoming high-impact news
        if news_events and len(news_events) > 0:
            next_event = news_events[0]
            event_time = next_event["time"]
            # Handle both datetime objects and ISO strings
            if isinstance(event_time, str):
                event_time = datetime.fromisoformat(event_time)
            time_until = (event_time - datetime.now(pytz.UTC)).total_seconds() / 60
            if time_until < 60:
                return "Fundamental"
        
        # Check for strong technical signals
        if technical_data.get("rsi_status") in ["Overbought", "Oversold"]:
            return "Technical"
        
        # Check for strong correlation movements
        if "yield" in correlation_analysis:
            if abs(correlation_analysis["yield"].get("change_bps", 0)) > 5:
                return "Fundamental"
        
        if "dxy" in correlation_analysis:
            if abs(correlation_analysis["dxy"].get("percent_change", 0)) > 0.5:
                return "Sentiment"
        
        return "Technical"
    
    def determine_momentum(self, technical_data: Dict, correlation_analysis: Dict) -> Dict:
        """Determine market momentum"""
        price_change = technical_data.get("price_change_1h", 0)
        ma_alignment = technical_data.get("ma_alignment", "Neutral")
        
        # Determine direction
        direction = "Bullish" if price_change > 0 else "Bearish" if price_change < 0 else "Neutral"
        
        # Determine strength
        abs_change = abs(price_change)
        if abs_change > 0.5:
            strength = "Strong"
        elif abs_change > 0.2:
            strength = "Moderate"
        else:
            strength = "Weak"
        
        return {
            "strength": strength,
            "direction": direction,
            "description": f"{strength} {direction}"
        }
    
    def check_alerts(self, technical_data: Dict, correlation_analysis: Dict, news_events: List) -> List[str]:
        """Check for alert conditions"""
        alerts = []
        
        current_price = technical_data.get("current_price", 0)
        nearest_levels = technical_data.get("nearest_levels", {})
        
        # Check proximity to key levels
        if "resistance" in nearest_levels:
            resistance, pips = nearest_levels["resistance"]
            proximity_pct = (abs(current_price - resistance) / current_price) * 100
            if proximity_pct < config.ALERT_PROXIMITY_PERCENT:
                alerts.append(f"Approaching Resistance: ${resistance:.2f} ({pips:.1f} pips)")
        
        if "support" in nearest_levels:
            support, pips = nearest_levels["support"]
            proximity_pct = (abs(current_price - support) / current_price) * 100
            if proximity_pct < config.ALERT_PROXIMITY_PERCENT:
                alerts.append(f"Approaching Support: ${support:.2f} ({pips:.1f} pips)")
        
        # Check yield movements
        if "yield" in correlation_analysis:
            bps_change = abs(correlation_analysis["yield"].get("change_bps", 0))
            if bps_change > config.YIELD_ALERT_BPS:
                alerts.append(f"Large Yield Move: {bps_change:.1f} bps")
        
        # Check DXY breakout
        if "dxy" in correlation_analysis:
            # This would require historical data to determine 30-day high/low
            # Simplified version
            pct_change = abs(correlation_analysis["dxy"].get("percent_change", 0))
            if pct_change > 1.0:
                alerts.append(f"Significant DXY Movement: {pct_change:.2f}%")
        
        # Check upcoming news
        if news_events:
            next_event = news_events[0]
            event_time = next_event["time"]
            # Handle both datetime objects and ISO strings
            if isinstance(event_time, str):
                event_time = datetime.fromisoformat(event_time)
            time_until = (event_time - datetime.now(pytz.UTC)).total_seconds() / 60
            if time_until < 30:
                alerts.append(f"High-Impact News in {int(time_until)} minutes: {next_event['title']}")
        
        # Check volume
        # This would require volume data from technical analysis
        
        return alerts if alerts else ["None"]
    
    def get_next_catalyst(self, news_events: List) -> Optional[Dict]:
        """Get next major catalyst"""
        if not news_events:
            return None
        
        next_event = news_events[0]
        event_time = next_event["time"]
        
        # Handle both datetime objects and ISO strings
        if isinstance(event_time, str):
            event_time = datetime.fromisoformat(event_time)
        
        time_until = (event_time - datetime.now(pytz.UTC)).total_seconds() / 60
        
        return {
            "event": next_event["title"],
            "time": event_time.strftime("%H:%M UTC"),
            "minutes_until": int(time_until),
            "impact": next_event["impact"]
        }
    
    def generate_market_snapshot(self) -> Dict:
        """Generate complete 15-minute market snapshot"""
        # Fetch all data in parallel
        market_data = self.data_aggregator.get_full_market_snapshot()
        
        xauusd_data = market_data["xauusd"]
        correlation_data = market_data["correlations"]
        news_events = market_data["news"]
        
        # Serialize news events (convert datetime objects to ISO strings)
        serialized_news = []
        if news_events:
            for event in news_events:
                serialized_event = event.copy()
                if "time" in serialized_event and isinstance(serialized_event["time"], datetime):
                    serialized_event["time"] = serialized_event["time"].isoformat()
                serialized_news.append(serialized_event)
        
        # Analyze XAUUSD on primary timeframe (1h)
        price_data_1h = xauusd_data["price_data"].get("1h")
        technical_data = self.technical_analyzer.analyze_timeframe(price_data_1h, "1h")
        
        # Analyze correlations
        correlation_analysis = self.analyze_correlations(correlation_data)
        
        # Determine market conditions
        primary_driver = self.determine_primary_driver(technical_data, news_events, correlation_analysis)
        momentum = self.determine_momentum(technical_data, correlation_analysis)
        alerts = self.check_alerts(technical_data, correlation_analysis, news_events)
        next_catalyst = self.get_next_catalyst(news_events)
        
        # Build snapshot
        snapshot = {
            "timestamp": datetime.now(pytz.UTC).isoformat(),
            "session": self.get_current_session(),
            "next_session_overlap": self.get_next_session_overlap(),
            "xauusd": {
                "price": technical_data.get("current_price", 0),
                "change_1h": technical_data.get("price_change_1h", 0),
                "quote": xauusd_data.get("quote", {})
            },
            "primary_driver": primary_driver,
            "momentum": momentum,
            "technical": technical_data,
            "correlations": correlation_analysis,
            "news": serialized_news,
            "next_catalyst": next_catalyst,
            "alerts": alerts
        }
        
        return snapshot
    
    def format_snapshot_text(self, snapshot: Dict) -> str:
        """Format snapshot as text output"""
        lines = []
        
        # Header
        timestamp = datetime.fromisoformat(snapshot["timestamp"]).strftime("%Y-%m-%d %H:%M:%S UTC")
        lines.append(f"[{timestamp}]")
        
        price = snapshot["xauusd"]["price"]
        change = snapshot["xauusd"]["change_1h"]
        session = snapshot["session"]
        lines.append(f"XAUUSD: ${price:.2f} | Change: {change:+.2f}% (1hr) | Session: {session}")
        lines.append("")
        
        # Primary driver and momentum
        lines.append(f"PRIMARY DRIVER: {snapshot['primary_driver']}")
        lines.append(f"MOMENTUM: {snapshot['momentum']['description']}")
        lines.append("")
        
        # Key monitors
        lines.append("KEY MONITORS:")
        lines.append("")
        
        # Yield watch
        if "yield" in snapshot["correlations"]:
            y = snapshot["correlations"]["yield"]
            lines.append(f"YIELD WATCH: 10Y @ {y['price']:.2f}% ({y['direction']} {abs(y['change_bps']):.1f}bps) → Gold Pressure: {y['pressure']}")
        
        # USD watch
        if "dxy" in snapshot["correlations"]:
            d = snapshot["correlations"]["dxy"]
            lines.append(f"USD WATCH: DXY @ {d['price']:.2f} ({d['direction']} {abs(d['percent_change']):.2f}%) → Inverse Pressure: {d['pressure']}")
        
        # Risk gauge
        if "risk" in snapshot["correlations"]:
            r = snapshot["correlations"]["risk"]
            lines.append(f"RISK GAUGE: SPX futures {r['direction']} {abs(r['percent_change']):.2f}% → Haven Demand: {r['haven_demand']}")
        
        lines.append("")
        
        # Technicals
        lines.append("TECHNICALS:")
        tech = snapshot["technical"]
        nearest = tech.get("nearest_levels", {})
        
        if "support" in nearest:
            support, pips = nearest["support"]
            lines.append(f"• Nearest Support: ${support:.2f} ({pips:.1f} pips below)")
        
        if "resistance" in nearest:
            resistance, pips = nearest["resistance"]
            lines.append(f"• Nearest Resistance: ${resistance:.2f} ({pips:.1f} pips above)")
        
        lines.append(f"• MA Alignment: {tech.get('ma_alignment', 'N/A')}")
        
        rsi = tech.get("rsi")
        if rsi:
            lines.append(f"• RSI(14): {rsi:.1f} [{tech.get('rsi_status', 'N/A')}]")
        
        lines.append("")
        
        # Next catalyst
        if snapshot["next_catalyst"]:
            cat = snapshot["next_catalyst"]
            lines.append(f"NEXT CATALYST: {cat['event']} at {cat['time']} in {cat['minutes_until']} minutes | Impact: {cat['impact']}")
        else:
            lines.append("NEXT CATALYST: None scheduled")
        
        lines.append("")
        
        # Alerts
        alerts = snapshot["alerts"]
        lines.append(f"ALERT CONDITIONS: {', '.join(alerts)}")
        
        return "\n".join(lines)
