# SYMBOL COMPATIBILITY NOTES FOR TWELVE DATA API

## Free Tier Limitations

The Twelve Data free tier has limitations on which symbols are available. Based on testing:

### ✅ Usually Available on Free Tier:
- **XAU/USD** - Gold (Forex pair)
- **BTC/USD** - Bitcoin
- **EUR/USD** - Euro
- **GBP/USD** - British Pound
- Major forex pairs

### ❌ May Require Paid Plan:
- **US10Y** - US 10-Year Treasury Yield (404 error)
- **DXY** - US Dollar Index (404 error)
- **SPX** - S&P 500 Index (404 error)
- Most indices and bonds

## Alternative Symbols for Free Tier

If you're using the free tier, consider these alternatives:

### Instead of DXY (Dollar Index):
- Use **EUR/USD** (inverse correlation to USD strength)
- Use **USD/JPY** (direct correlation to USD strength)

### Instead of US10Y (Treasury Yield):
- No direct alternative on free tier
- Monitor via external sources

### Instead of SPX (S&P 500):
- Use **SPY** (S&P 500 ETF) - may work
- Monitor via external sources

## Recommended Free Tier Configuration

```python
CORRELATION_SYMBOLS = {
    "EUR/USD": "EUR/USD",      # Euro (inverse to USD strength)
    "USD/JPY": "USD/JPY",      # Yen (direct to USD strength)
    "GBP/USD": "GBP/USD",      # Pound (risk sentiment)
    "BTC/USD": "BTC/USD"       # Bitcoin (alternative asset)
}
```

## Upgrading Your Plan

To access all symbols (DXY, US10Y, SPX), consider upgrading to:
- **Basic Plan**: $7.99/month - 800 API calls/day
- **Pro Plan**: $29.99/month - 8,000 API calls/day
- Visit: https://twelvedata.com/pricing

## Current Configuration

Your current config uses:
- XAU/USD ✅ (should work)
- US10Y ❌ (requires paid plan)
- DXY ❌ (requires paid plan)  
- SPX ❌ (requires paid plan)
- BTC/USD ✅ (should work)

The system will continue to work, but correlation data for US10Y, DXY, and SPX will not be available until you upgrade or change to alternative symbols.
