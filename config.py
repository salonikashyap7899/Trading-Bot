# config.py
# Binance Credentials - IMPORTANT: Keep these secure!

BINANCE_KEY = 'iyK0QCtq44CZb7K5BlRcZPCrjn2i7zeL52KQXxs9654NWkQnfQIvm1rKBaNhbXob'
BINANCE_SECRET = 'EowxqqSJr8vD15Bk8oUGArIn9TrYaXlmPjoccV7TVLqLFZ7aqId3KzJY9l5iurOp'

# # Trading Configuration
# MAX_TRADES_PER_DAY = 4
# MAX_TRADES_PER_SYMBOL_PER_DAY = 2  # FIX #1: Maximum 2 trades per symbol per day

# # Risk Management
# MAX_RISK_PERCENT = 1.0  # 1% risk per trade
# SL_EDIT_MIN_PERCENT = -1.0  # Minimum SL adjustment (can move SL up to -1%)
# SL_EDIT_MAX_PERCENT = 0.0   # Maximum SL adjustment (cannot move beyond entry)

# # Update Intervals (seconds) - FIX: Increased to reduce API calls
# POSITION_UPDATE_INTERVAL = 3
# PRICE_UPDATE_INTERVAL = 5

# # API Rate Limiting Protection - FIX: Better caching
# PRICE_CACHE_DURATION = 5  # Cache prices for 5 seconds
# SYMBOL_CACHE_DURATION = 3600  # Cache symbols for 1 hour
# MAX_RETRIES = 3  # Retry failed API calls
# RETRY_DELAY = 1  # Delay between retries in seconds


# # config.py
# Binance Futures Trading Configuration
# IMPORTANT: NEVER commit this file to git with real keys!

import os

# ────────────────────────────────────────────────────────────────
#          OPTION 1: Use environment variables (recommended)
# ────────────────────────────────────────────────────────────────
# Best practice: set these in terminal or .env file
#
# Windows (cmd):
# set BINANCE_API_KEY=your_key_here
# set BINANCE_API_SECRET=your_secret_here
#
# Linux/Mac:
# export BINANCE_API_KEY=your_key_here
# export BINANCE_API_SECRET=your_secret_here

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# ────────────────────────────────────────────────────────────────
#          OPTION 2: Hardcode (ONLY for local testing - NOT safe!)
# ────────────────────────────────────────────────────────────────
# Uncomment only if you really can't use environment variables
# And DELETE / CHANGE these keys immediately after testing!
#
# API_KEY    = 'iyK0QCtq44CZb7K5BlRcZPCrjn2i7zeL52KQXxs9654NWkQnfQIvm1rKBaNhbXob'
# API_SECRET = 'EowxqqSJr8vD15Bk8oUGArIn9TrYaXlmPjoccV7TVLqLFZ7aqId3KzJY9l5iurOp'

# ────────────────────────────────────────────────────────────────
#              Safety check - very important!
# ────────────────────────────────────────────────────────────────
if not API_KEY or not API_SECRET:
    raise ValueError(
        "!!! CRITICAL ERROR !!!\n"
        "Binance API key or secret is missing!\n"
        "Please set BINANCE_API_KEY and BINANCE_API_SECRET environment variables\n"
        "or uncomment and fill the hardcoded values (but only for testing!)"
    )

# ────────────────────────────────────────────────────────────────
#                   Trading Configuration
# ────────────────────────────────────────────────────────────────
MAX_TRADES_PER_DAY = 4
MAX_TRADES_PER_SYMBOL_PER_DAY = 2

# Risk Management
MAX_RISK_PERCENT = 1.0          # 1% risk per trade
SL_EDIT_MIN_PERCENT = -1.0      # Can move SL up to -1%
SL_EDIT_MAX_PERCENT = 0.0       # Cannot move SL beyond entry

# Update Intervals (seconds)
POSITION_UPDATE_INTERVAL = 3
PRICE_UPDATE_INTERVAL = 5

# Cache settings (reduce API calls)
PRICE_CACHE_DURATION = 5        # seconds
SYMBOL_CACHE_DURATION = 3600    # 1 hour

# API Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 1                 # seconds between retries

# ────────────────────────────────────────────────────────────────
#                   Optional - Testnet support
# ────────────────────────────────────────────────────────────────
USE_TESTNET = False  # Change to True when testing!!!

if USE_TESTNET:
    print("!!! USING BINANCE FUTURES TESTNET !!!")
    # Testnet base URLs (add to Client initialization if needed)
    # Client(..., testnet=True) usually handles this automatically




