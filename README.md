# Binance Futures Trading Bot - FIXED VERSION

## 🚀 Features

### ✅ All Fixed Issues

1. **Same Symbol Trade Limit**: Maximum 2 trades per symbol per day ✓
2. **Live Position Updates**: Real-time data from Binance (updates every 3 seconds) ✓
3. **TP/SL Placement**: Actually places orders on Binance with proper error handling ✓
4. **Dynamic Position Count**: Shows actual number of open positions ✓
5. **API Rate Limiting**: Better caching to avoid "Too many requests" errors ✓
6. **Partial Close**: Close positions partially by percentage ✓
7. **Editable SL**: Adjust stop loss between -1% to 0% ✓

## 📋 Requirements

- Python 3.8+
- Active Binance Futures account
- API keys with Futures trading enabled

## 🔧 Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure API Keys:**
Edit `config.py` and add your Binance API credentials:
```python
BINANCE_KEY = 'your_api_key_here'
BINANCE_SECRET = 'your_secret_key_here'
```

⚠️ **IMPORTANT**: Never share your API keys!

## 🎯 Configuration

Edit `config.py` to customize:

```python
# Trading Limits
MAX_TRADES_PER_DAY = 4                  # Maximum total trades per day
MAX_TRADES_PER_SYMBOL_PER_DAY = 2       # Maximum trades per symbol per day

# Risk Management
MAX_RISK_PERCENT = 1.0                  # Risk 1% per trade
SL_EDIT_MIN_PERCENT = -1.0              # SL can be adjusted up to -1%
SL_EDIT_MAX_PERCENT = 0.0               # SL cannot go beyond entry

# Update Intervals (seconds)
POSITION_UPDATE_INTERVAL = 3            # Update positions every 3 seconds
PRICE_UPDATE_INTERVAL = 5               # Update prices every 5 seconds
```

## 🚀 Running the Bot

```bash
python app.py
```

The bot will start on `http://0.0.0.0:5000`

Open your browser and navigate to `http://localhost:5000`

## 📊 Usage Guide

### Placing a Trade

1. **Select Symbol**: Choose trading pair (e.g., BTCUSDT)
2. **Choose Side**: LONG or SHORT
3. **Set Entry Price**: Auto-fills with market price
4. **Configure Stop Loss**: MANDATORY (SL % Movement or SL Points)
5. **Optional TP Levels**: Set TP1 (with percentage) and TP2
6. **Review Position Sizing**: Auto-calculated based on 1% risk
7. **Click**: "EXECUTE EXCHANGE ORDER"

### Managing Positions

- **View Live Positions**: Updates every 3 seconds with real-time P&L
- **Partial Close**: Click "Partial" button and enter percentage (1-99%)
- **Close Position**: Click "Close" button to exit entire position
- **Adjust SL**: Enter value between -1% and 0%, click "Update SL"

### Live Trade Log

- Shows last 50 trades from Binance
- Updates every 5 seconds
- Download as CSV by clicking "📥 CSV" button

## 🔐 Security

- ✅ Leverage auto-calculated based on SL
- ✅ Maximum 1% risk per trade
- ✅ Daily trade limits enforced
- ✅ Per-symbol trade limits enforced
- ✅ SL adjustment restricted to -1% to 0%

## ⚡ Performance Optimizations

1. **Price Caching**: Prices cached for 5 seconds to reduce API calls
2. **Symbol Caching**: Symbols cached for 1 hour
3. **Retry Logic**: Auto-retry failed API calls up to 3 times
4. **Error Handling**: Comprehensive error handling for all Binance API calls

## 🐛 Troubleshooting

### "Too many requests" Error

- Bot now has aggressive caching to prevent this
- Price updates: 5 seconds
- Position updates: 3 seconds
- If still occurring, increase intervals in `config.py`

### SL/TP Not Placing

- Check console logs for error messages
- Verify API keys have Futures trading permissions
- Ensure sufficient margin in account
- Check if symbol supports STOP_MARKET orders

### Position Count Shows 0

- Wait 3 seconds for first update
- Check if you have actual open positions on Binance
- Verify API keys are correct

## 📝 Trading Logic

### Position Sizing Formula

```
Risk Amount = Unutilized Margin × 1%
Leverage = 100 / (SL% + 0.2)
Position Value = [Risk ÷ (SL% + 0.2)] × 100
Position Size = Position Value / Entry Price
```

### Example

- Unutilized Margin: $1000
- Risk: $10 (1%)
- SL: 2%
- Leverage: 100 / 2.2 = 45x
- Position Value: ($10 / 2.2) × 100 = $454.55
- Entry: $90,000
- Position Size: 0.00505 BTC

## 📈 Advanced Features

### Partial TP Strategy

1. Set TP1 at first target (e.g., +3%)
2. Set TP1 Qty % (e.g., 50%) - takes 50% profit
3. Set TP2 at second target (e.g., +5%)
4. Remaining 50% exits at TP2

### Dynamic SL Adjustment

- Move SL to breakeven when in profit
- Tighten SL as price moves favorably
- Can only move SL between -1% to 0% from entry
- Cannot move SL beyond entry (prevents turning winner into loser)

## ⚠️ Important Notes

1. **Test First**: Test with small positions before going live
2. **Monitor Actively**: Keep an eye on positions and market conditions
3. **Check Logs**: Console shows all API interactions and errors
4. **Backup Keys**: Keep API keys secure and backed up
5. **Know Risks**: Trading involves risk of loss

## 🔄 Updates in This Fixed Version

### What Was Fixed:

1. ✅ **Trade Limits**: Per-symbol limit now properly enforced
2. ✅ **Live Updates**: Positions and trades now fetch REAL data from Binance
3. ✅ **TP/SL Placement**: Orders now actually placed on Binance exchange
4. ✅ **Position Count**: Dynamically updates based on actual open positions
5. ✅ **API Errors**: Better caching and retry logic to prevent rate limits
6. ✅ **Error Handling**: Comprehensive error handling throughout
7. ✅ **Timestamps**: Real timestamps on all positions and trades

### Key Improvements:

- Better error messages
- Retry logic for failed API calls
- Aggressive caching to reduce API usage
- Real-time position updates
- Dynamic UI updates
- CSV export for trade history

## 📞 Support

For issues or questions:
1. Check console logs for detailed error messages
2. Verify API key permissions on Binance
3. Ensure you're using Binance Futures (not Spot)
4. Check your account has sufficient balance

## ⚖️ Disclaimer

This bot is for educational purposes. Trading cryptocurrencies carries risk. 
Always trade responsibly and never risk more than you can afford to lose.

---

**Version**: 2.0 (Fixed)
**Last Updated**: January 2025
**Status**: ✅ All Issues Resolved# Trading-Bot
