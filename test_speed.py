
import time
from data_fetcher import MarketDataAggregator
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

def test_performance():
    print("Initializing MarketDataAggregator...")
    aggregator = MarketDataAggregator()
    
    print("\n--- Test 1: Cold Start (No Cache) ---")
    start_time = time.time()
    snapshot = aggregator.get_full_market_snapshot()
    duration = time.time() - start_time
    
    print(f"Time taken: {duration:.2f} seconds")
    print(f"Keys present: {list(snapshot.keys())}")
    
    if duration > 10:
        print("WARNING: Cold start still taking > 10 seconds!")
    else:
        print("SUCCESS: Cold start significantly improved!")

    print("\n--- Test 2: Warm Start (Cached) ---")
    start_time = time.time()
    snapshot = aggregator.get_full_market_snapshot()
    duration = time.time() - start_time
    
    print(f"Time taken: {duration:.4f} seconds")
    if duration < 0.1:
        print("SUCCESS: Caching is working correctly!")
    else:
        print("WARNING: Caching might not be working as expected.")

if __name__ == "__main__":
    test_performance()
