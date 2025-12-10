"""
Technical Analysis Module - Calculates indicators and identifies key levels
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import config


class TechnicalAnalyzer:
    """Performs technical analysis on price data"""
    
    def __init__(self):
        self.support_resistance_cache = {}
    
    def calculate_rsi(self, data: List[Dict], period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index"""
        if len(data) < period + 1:
            return None
        
        # Get close prices
        closes = [candle["close"] for candle in data]
        
        # Calculate price changes
        gains = []
        losses = []
        
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        # Calculate average gains and losses
        if len(gains) < period:
            return None
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_moving_average(self, data: List[Dict], period: int) -> Optional[float]:
        """Calculate Simple Moving Average"""
        if len(data) < period:
            return None
        
        closes = [candle["close"] for candle in data[-period:]]
        return sum(closes) / period
    
    def calculate_moving_averages(self, data: List[Dict], periods: List[int]) -> Dict[int, Optional[float]]:
        """Calculate Simple Moving Averages"""
        mas = {}
        for period in periods:
            mas[period] = self.calculate_moving_average(data, period)
        return mas
    
    def identify_support_resistance(self, data: List[Dict], lookback: int = 50) -> Dict[str, List[float]]:
        """Identify key support and resistance levels"""
        if len(data) < 5:
            return {"resistance": [], "support": []}
        
        lookback = min(lookback, len(data))
        recent_data = data[-lookback:]
        
        highs = [candle["high"] for candle in recent_data]
        lows = [candle["low"] for candle in recent_data]
        
        resistance_levels = []
        support_levels = []
        
        # Simple peak detection
        for i in range(2, len(highs) - 2):
            # Resistance (local maxima)
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                resistance_levels.append(highs[i])
            
            # Support (local minima)
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                support_levels.append(lows[i])
        
        # Add recent high/low
        resistance_levels.append(max(highs))
        support_levels.append(min(lows))
        
        # Cluster similar levels
        resistance_levels = self._cluster_levels(resistance_levels)
        support_levels = self._cluster_levels(support_levels)
        
        return {
            "resistance": sorted(resistance_levels, reverse=True)[:5],
            "support": sorted(support_levels, reverse=True)[:5]
        }
    
    def _cluster_levels(self, levels: List[float], threshold: float = 0.001) -> List[float]:
        """Cluster similar price levels"""
        if not levels:
            return []
        
        levels = sorted(levels)
        clustered = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - clustered[-1]) / clustered[-1] > threshold:
                clustered.append(level)
        
        return clustered
    
    def find_nearest_levels(self, current_price: float, levels: Dict[str, List[float]]) -> Dict[str, Tuple[float, float]]:
        """Find nearest support and resistance to current price"""
        resistance_levels = [r for r in levels["resistance"] if r > current_price]
        support_levels = [s for s in levels["support"] if s < current_price]
        
        nearest_resistance = min(resistance_levels) if resistance_levels else None
        nearest_support = max(support_levels) if support_levels else None
        
        result = {}
        
        if nearest_resistance:
            pips_away = (nearest_resistance - current_price) * 10  # Approximate pips
            result["resistance"] = (nearest_resistance, pips_away)
        
        if nearest_support:
            pips_away = (current_price - nearest_support) * 10  # Approximate pips
            result["support"] = (nearest_support, pips_away)
        
        return result
    
    def calculate_pivot_points(self, data: List[Dict]) -> Dict[str, float]:
        """Calculate pivot points from previous day's data"""
        if len(data) < 2:
            return {}
        
        prev_day = data[-2]
        high = prev_day["high"]
        low = prev_day["low"]
        close = prev_day["close"]
        
        pivot = (high + low + close) / 3
        
        return {
            "pivot": pivot,
            "r1": 2 * pivot - low,
            "r2": pivot + (high - low),
            "r3": high + 2 * (pivot - low),
            "s1": 2 * pivot - high,
            "s2": pivot - (high - low),
            "s3": low - 2 * (high - pivot)
        }
    
    def get_ma_alignment(self, mas: Dict[int, Optional[float]], current_price: float) -> str:
        """Determine MA alignment (bullish/bearish/neutral)"""
        if not mas:
            return "Neutral"
        
        ma_values = {period: ma for period, ma in mas.items() if ma is not None}
        
        if not ma_values:
            return "Neutral"
        
        # Check if price is above all MAs (bullish) or below all MAs (bearish)
        above_all = all(current_price > ma for ma in ma_values.values())
        below_all = all(current_price < ma for ma in ma_values.values())
        
        if above_all:
            return "Bullish"
        elif below_all:
            return "Bearish"
        else:
            return "Neutral"
    
    def get_rsi_status(self, rsi_value: Optional[float]) -> str:
        """Get RSI status"""
        if rsi_value is None:
            return "N/A"
        elif rsi_value > config.RSI_OVERBOUGHT:
            return "Overbought"
        elif rsi_value < config.RSI_OVERSOLD:
            return "Oversold"
        else:
            return "Neutral"
    
    def analyze_timeframe(self, data: List[Dict], timeframe: str) -> Dict:
        """Perform complete technical analysis for a timeframe"""
        if data is None or len(data) < 20:
            return {"error": "Insufficient data"}
        
        current_price = data[-1]["close"]
        
        # Calculate indicators
        rsi = self.calculate_rsi(data, config.RSI_PERIOD)
        mas = self.calculate_moving_averages(data, config.MA_PERIODS)
        levels = self.identify_support_resistance(data)
        pivots = self.calculate_pivot_points(data)
        nearest = self.find_nearest_levels(current_price, levels)
        
        # Calculate price changes
        price_1h_ago = data[-5]["close"] if len(data) >= 5 else current_price
        price_change_1h = ((current_price - price_1h_ago) / price_1h_ago) * 100
        
        return {
            "timeframe": timeframe,
            "current_price": current_price,
            "price_change_1h": price_change_1h,
            "rsi": rsi,
            "rsi_status": self.get_rsi_status(rsi),
            "mas": mas,
            "ma_alignment": self.get_ma_alignment(mas, current_price),
            "support_resistance": levels,
            "nearest_levels": nearest,
            "pivot_points": pivots
        }
    
    def calculate_volume_profile(self, data: List[Dict]) -> Dict:
        """Calculate volume statistics"""
        if data is None or len(data) < config.VOLUME_LOOKBACK_DAYS:
            return {"error": "Insufficient data"}
        
        recent_data = data[-config.VOLUME_LOOKBACK_DAYS:]
        volumes = [candle["volume"] for candle in recent_data]
        
        avg_volume = sum(volumes) / len(volumes)
        current_volume = data[-1]["volume"]
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        return {
            "current_volume": current_volume,
            "average_volume": avg_volume,
            "volume_ratio": volume_ratio,
            "is_high_volume": volume_ratio > config.HIGH_VOLUME_THRESHOLD
        }
