# # config.py
# # Binance Credentials - IMPORTANT: Keep these secure!

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
# config.py
# Binance Futures Trading Configuration
# IMPORTANT: NEVER commit this file to git with real keys!

import os

# ────────────────────────────────────────────────────────────────
#  Preferred method: Load keys from environment variables
# ────────────────────────────────────────────────────────────────
# Set these in your terminal before running the app:
#
# Windows (Command Prompt):
# set BINANCE_API_KEY=your_actual_key_here
# set BINANCE_API_SECRET=your_actual_secret_here
# python app.py
#
# Linux/Mac:
# export BINANCE_API_KEY=your_actual_key_here
# export BINANCE_API_SECRET=your_actual_secret_here
# python app.py

API_KEY    = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# ────────────────────────────────────────────────────────────────
#  Fallback - Hardcode ONLY for LOCAL TESTING (NOT RECOMMENDED!)
#  → Use only temporarily, then delete or comment out!
# ────────────────────────────────────────────────────────────────
# API_KEY    = 'your_new_key_here_after_revoke'
# API_SECRET = 'your_new_secret_here_after_revoke'

# ────────────────────────────────────────────────────────────────
#  Critical safety check - fail early if keys are missing
# ────────────────────────────────────────────────────────────────
if not API_KEY or not API_SECRET:
    raise ValueError(
        "!!! CRITICAL SECURITY ERROR !!!\n"
        "Binance API key or secret is missing!\n\n"
        "You MUST do one of the following:\n"
        "1. Set environment variables BINANCE_API_KEY and BINANCE_API_SECRET\n"
        "   (recommended & safest method)\n"
        "   Example:\n"
        "   export BINANCE_API_KEY=...\n"
        "   export BINANCE_API_SECRET=...\n\n"
        "2. Or temporarily uncomment the hardcoded values below\n"
        "(but delete them after testing!)\n\n"
        "Your current config is NOT loading any real keys!"
    )

print("✓ Binance API keys loaded successfully (length check passed)")

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
USE_TESTNET = False  # ← Change to True when testing (strongly recommended!)

if USE_TESTNET:
    print("!!! WARNING: USING BINANCE FUTURES TESTNET MODE !!!")
    # Note: Most recent python-binance versions support:
    # client = Client(API_KEY, API_SECRET, testnet=True)