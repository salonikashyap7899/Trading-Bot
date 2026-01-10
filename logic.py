from http import client
from flask import session
from datetime import datetime, date
from binance.client import Client
from binance.exceptions import BinanceAPIException

import config
import math
import traceback
import time

_client = None
_symbol_cache = None
_symbol_cache_time = 0
_price_cache = {}
_price_cache_time = {}

def sync_time_with_binance():
    """Sync local time with Binance server time"""
    try:
        import requests
        response = requests.get('https://fapi.binance.com/fapi/v1/time')
        server_time = response.json()['serverTime']
        local_time = int(time.time() * 1000)
        time_offset = server_time - local_time
        return time_offset
    except Exception as e:
        print(f"⚠️ Could not sync time: {e}")
        return 0

def get_client():
    """Get or create Binance client with error handling - FIX: Timestamp issue"""
    global _client
    if _client is None:
        try:
            # FIX: Sync time with Binance first
            time_offset = sync_time_with_binance()
            print(f"⏰ Time offset with Binance: {time_offset}ms")
            
            # Create client with larger recvWindow
            _client = Client(
                config.BINANCE_KEY, 
                config.BINANCE_SECRET,
                {'timeout': 20}
            )
            
            # Apply time offset
            if abs(time_offset) > 1000:  # If offset > 1 second
                _client.timestamp_offset = time_offset
                print(f"✅ Applied time offset: {time_offset}ms")
            
            # Test connection with larger recvWindow
            _client.futures_account(recvWindow=60000)
            print("✅ Binance client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Binance client: {e}")
            print("💡 Tip: Make sure your system time is synced. Run: sudo ntpdate -s time.nist.gov")
            _client = None
    return _client

def initialize_session():
    """Initialize session variables"""
    if "trades" not in session:
        session["trades"] = []
    if "stats" not in session:
        session["stats"] = {}
    session.modified = True

def get_all_exchange_symbols():
    """Get symbols with caching to avoid rate limits - FIX: Better caching"""
    global _symbol_cache, _symbol_cache_time
    
    current_time = time.time()
    if _symbol_cache and (current_time - _symbol_cache_time) < config.SYMBOL_CACHE_DURATION:
        return _symbol_cache
    
    try:
        client = get_client()
        if client is None: 
            return ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
        
        info = client.futures_exchange_info()
        symbols = sorted([s["symbol"] for s in info["symbols"] 
                         if s["status"] == "TRADING" and s["quoteAsset"] == "USDT"])
        _symbol_cache = symbols
        _symbol_cache_time = current_time
        return symbols
    except BinanceAPIException as e:
        print(f"⚠️ Binance API Error getting symbols: {e}")
        return _symbol_cache if _symbol_cache else ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
    except Exception as e:
        print(f"❌ Error getting symbols: {e}")
        return _symbol_cache if _symbol_cache else ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]

def get_live_balance():
    """Get live balance with retry logic - FIX: Better error handling"""
    for attempt in range(config.MAX_RETRIES):
        try:
            client = get_client()
            if client is None: 
                return None, None
            
            acc = client.futures_account(recvWindow=60000)
            return float(acc["totalWalletBalance"]), float(acc["totalInitialMargin"])
        except BinanceAPIException as e:
            if "Too many requests" in str(e):
                print(f"⚠️ Rate limit hit, attempt {attempt + 1}/{config.MAX_RETRIES}")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(config.RETRY_DELAY * (attempt + 1))
                    continue
            print(f"❌ Binance API Error getting balance: {e}")
            return None, None
        except Exception as e:
            print(f"❌ Error getting balance: {e}")
            return None, None
    return None, None

def get_live_price(symbol):
    """Get price with caching to avoid rate limits - FIX: Better caching"""
    global _price_cache, _price_cache_time
    
    current_time = time.time()
    if symbol in _price_cache and (current_time - _price_cache_time.get(symbol, 0)) < config.PRICE_CACHE_DURATION:
        return _price_cache[symbol]
    
    try:
        client = get_client()
        if client is None: 
            return _price_cache.get(symbol, None)
        
        price = float(client.futures_symbol_ticker(symbol=symbol)["price"])
        _price_cache[symbol] = price
        _price_cache_time[symbol] = current_time
        return price
    except BinanceAPIException as e:
        print(f"⚠️ Binance API Error getting price for {symbol}: {e}")
        return _price_cache.get(symbol, None)
    except Exception as e:
        print(f"❌ Error getting price for {symbol}: {e}")
        return _price_cache.get(symbol, None)

def get_symbol_filters(symbol):
    """Get symbol filters with error handling"""
    try:
        client = get_client()
        if client is None: return []
        info = client.futures_exchange_info()
        for s in info["symbols"]:
            if s["symbol"] == symbol: 
                return s["filters"]
    except Exception as e:
        print(f"⚠️ Error getting filters for {symbol}: {e}")
    return []

def get_lot_step(symbol):
    """Get lot size step for symbol"""
    for f in get_symbol_filters(symbol):
        if f["filterType"] == "LOT_SIZE": 
            return float(f["stepSize"])
    return 0.001

def round_qty(symbol, qty):
    """Round quantity to valid lot size"""
    step = get_lot_step(symbol)
    if step == 0:
        step = 0.001
    if step >= 1:
        return max(1, int(qty))
    precision = abs(int(round(-math.log10(step))))
    rounded = round(qty - (qty % step), precision)
    return rounded if rounded > 0 else step

def round_price(symbol, price):
    """Round price to valid tick size"""
    for f in get_symbol_filters(symbol):
        if f["filterType"] == "PRICE_FILTER":
            tick = float(f["tickSize"])
            if tick == 0:
                return price
            if tick >= 1:
                return int(price)
            precision = abs(int(round(-math.log10(tick))))
            return round(price - (price % tick), precision)
    return round(price, 2)

def calculate_position_sizing(unutilized_margin, entry, sl_type, sl_value):
    """Calculate position size and leverage based on risk management"""
    if entry <= 0: 
        return {"error": "Invalid Entry"}
    
    risk_amount = unutilized_margin * (config.MAX_RISK_PERCENT / 100)

    if sl_value > 0:
        if sl_type == "SL % Movement":
            sl_percent = sl_value
            sl_distance = entry * (sl_value / 100)
        else:
            sl_distance = abs(entry - sl_value)
            sl_percent = (sl_distance / entry) * 100

        if sl_distance <= 0: 
            return {"error": "Invalid SL distance"}

        # Leverage Formula: 100 / (SL% + 0.2)
        calculated_leverage = 100 / (sl_percent + 0.2)
        max_leverage = min(int(calculated_leverage), 125)
        
        # Position Value Formula: [Risk ÷ (SL% + 0.2)] × 100
        pos_value_usdt = (risk_amount / (sl_percent + 0.2)) * 100
        position_size = pos_value_usdt / entry
    else:
        max_leverage = 10
        position_size = risk_amount / entry

    return {
        "suggested_units": round(position_size, 6),
        "suggested_leverage": max_leverage,
        "max_leverage": max_leverage,
        "risk_amount": round(risk_amount, 2),
        "error": None
    }

def get_open_positions():
    """FIX: Get REAL open positions from Binance with live data"""
    try:
        client = get_client()
        if client is None:
            return []
        
        positions = client.futures_position_information(recvWindow=60000)
        open_positions = []
        
        for pos in positions:
            position_amt = float(pos['positionAmt'])
            if position_amt != 0:
                entry_price = float(pos['entryPrice'])
                mark_price = float(pos['markPrice'])
                unrealized_pnl = float(pos['unRealizedProfit'])
                liquidation_price = float(pos['liquidationPrice'])
                leverage = int(pos['leverage'])
                
                notional = float(pos['notional'])
                initial_margin = abs(notional) / leverage
                roi_percent = (unrealized_pnl / initial_margin * 100) if initial_margin > 0 else 0
                
                if mark_price > 0 and liquidation_price > 0:
                    if position_amt > 0:
                        margin_ratio = ((mark_price - liquidation_price) / mark_price) * 100
                    else:
                        margin_ratio = ((liquidation_price - mark_price) / mark_price) * 100
                else:
                    margin_ratio = 0
                
                open_orders = get_open_orders_for_symbol(pos['symbol'])
                
                open_positions.append({
                    'symbol': pos['symbol'],
                    'side': 'LONG' if position_amt > 0 else 'SHORT',
                    'amount': abs(position_amt),
                    'size_usdt': abs(notional),
                    'margin_usdt': initial_margin,
                    'margin_ratio': abs(margin_ratio),
                    'entry_price': entry_price,
                    'mark_price': mark_price,
                    'unrealized_pnl': unrealized_pnl,
                    'roi_percent': roi_percent,
                    'leverage': leverage,
                    'liquidation_price': liquidation_price,
                    'open_orders': open_orders,
                    'timestamp': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return open_positions
    except BinanceAPIException as e:
        print(f"⚠️ Binance API Error getting positions: {e}")
        return []
    except Exception as e:
        print(f"❌ Error getting open positions: {e}")
        traceback.print_exc()
        return []

def get_open_orders_for_symbol(symbol):
    """Get all open orders (TP/SL) for a specific symbol"""
    try:
        client = get_client()
        if client is None:
            return []
        
        orders = client.futures_get_open_orders(symbol=symbol, recvWindow=60000)
        order_list = []
        
        for order in orders:
            order_list.append({
                'orderId': order['orderId'],
                'type': order['type'],
                'side': order['side'],
                'price': float(order.get('stopPrice', order.get('price', 0))),
                'origQty': float(order['origQty']),
                'status': order['status']
            })
        
        return order_list
    except Exception as e:
        print(f"⚠️ Error getting open orders for {symbol}: {e}")
        return []

def check_trade_limits(symbol):
    """FIX #1: Check both daily total and per-symbol limits"""
    today = datetime.utcnow().date().isoformat()
    stats = session.get("stats", {}).get(today, {"total": 0, "symbols": {}})
    
    if stats["total"] >= config.MAX_TRADES_PER_DAY:
        return False, f"❌ Daily limit reached ({config.MAX_TRADES_PER_DAY} trades)"
    
    symbol_count = stats.get("symbols", {}).get(symbol, 0)
    if symbol_count >= config.MAX_TRADES_PER_SYMBOL_PER_DAY:
        return False, f"❌ Symbol limit reached ({config.MAX_TRADES_PER_SYMBOL_PER_DAY} trades for {symbol} today)"
    
    return True, "OK"

def update_trade_stats(symbol):
    """Update trade statistics for limits tracking"""
    today = datetime.utcnow().date().isoformat()
    if "stats" not in session:
        session["stats"] = {}
    if today not in session["stats"]:
        session["stats"][today] = {"total": 0, "symbols": {}}
    
    session["stats"][today]["total"] += 1
    
    if symbol not in session["stats"][today]["symbols"]:
        session["stats"][today]["symbols"][symbol] = 0
    session["stats"][today]["symbols"][symbol] += 1
    
    session.modified = True
def execute_trade_action(
    balance, symbol, side, entry, order_type,
    sl_type, sl_value, sizing,
    user_units, user_lev, margin_mode,
    tp1, tp1_pct, tp2
):
    can_trade, limit_msg = check_trade_limits(symbol)
    if not can_trade:
        return {"success": False, "message": limit_msg}

    try:
        client = get_client()
        if client is None:
            return {"success": False, "message": "Binance client not connected"}

        units = user_units if user_units > 0 else sizing["suggested_units"]
        qty = round_qty(symbol, units)

        leverage = int(user_lev) if user_lev > 0 else sizing["max_leverage"]
        client.futures_change_leverage(symbol=symbol, leverage=leverage)

        try:
            client.futures_change_margin_type(symbol=symbol, marginType=margin_mode)
        except BinanceAPIException:
            pass

        entry_side = Client.SIDE_BUY if side == "LONG" else Client.SIDE_SELL
        exit_side = Client.SIDE_SELL if side == "LONG" else Client.SIDE_BUY

        # ================= ENTRY =================
        entry_order = client.futures_create_order(
            symbol=symbol,
            side=entry_side,
            type="MARKET",
            quantity=qty
        )

        time.sleep(1)
        actual_entry = float(client.futures_mark_price(symbol=symbol)["markPrice"])

        # ================= STOP LOSS =================
        sl_order_id = None
        sl_price_value = None

        if sl_value > 0:
            sl_percent = sl_value if sl_type == "SL % Movement" else abs(entry - sl_value) / entry * 100

            sl_price = (
                actual_entry * (1 - sl_percent / 100)
                if side == "LONG"
                else actual_entry * (1 + sl_percent / 100)
            )

            sl_price = round_price(symbol, sl_price)
            sl_price_value = sl_price

            sl_order = client.futures_create_order(
                symbol=symbol,
                side=exit_side,
                type="STOP_MARKET",
                stopPrice=sl_price,
                closePosition=True,
                workingType="MARK_PRICE",
                priceProtect=True
            )

            sl_order_id = sl_order["orderId"]

        # ================= TP1 =================
        tp1_order_id = None
        if tp1 > 0 and tp1_pct > 0:
            tp1_qty = round_qty(symbol, qty * (tp1_pct / 100))
            tp1_price = round_price(symbol, tp1)

            tp1_order = client.futures_create_order(
                symbol=symbol,
                side=exit_side,
                type="TAKE_PROFIT_MARKET",
                stopPrice=tp1_price,
                quantity=tp1_qty,
                workingType="MARK_PRICE",
                priceProtect=True
            )
            tp1_order_id = tp1_order["orderId"]

        # ================= TP2 =================
        tp2_order_id = None
        if tp2 > 0:
            tp2_price = round_price(symbol, tp2)

            tp2_order = client.futures_create_order(
                symbol=symbol,
                side=exit_side,
                type="TAKE_PROFIT_MARKET",
                stopPrice=tp2_price,
                closePosition=True,
                workingType="MARK_PRICE",
                priceProtect=True
            )
            tp2_order_id = tp2_order["orderId"]

        update_trade_stats(symbol)

        return {
            "success": True,
            "message": "✅ Order placed with SL & TP",
            "order_ids": {
                "entry": entry_order["orderId"],
                "sl": sl_order_id,
                "tp1": tp1_order_id,
                "tp2": tp2_order_id
            }
        }

    except BinanceAPIException as e:
        return {"success": False, "message": str(e)}
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_today_stats():
    """Get today's trade statistics"""
    today = datetime.utcnow().date().isoformat()
    stats = session.get("stats", {}).get(today, {"total": 0, "symbols": {}})
    return {
        "total_trades": stats.get("total", 0),
        "max_trades": config.MAX_TRADES_PER_DAY,
        "symbol_trades": stats.get("symbols", {}),
        "max_per_symbol": config.MAX_TRADES_PER_SYMBOL_PER_DAY
    }

def live_trade_logger(symbol):
    try:
        positions = client.futures_position_information(symbol=symbol)
        for p in positions:
            qty = float(p["positionAmt"])
            pnl = float(p["unRealizedProfit"])

            if qty != 0:
                print(f"📊 LIVE | {symbol} | Qty: {qty} | PnL: {pnl}")
            else:
                print(f"✅ POSITION CLOSED | {symbol}")
    except Exception as e:
        print(f"⚠️ Live log error: {e}")
