import numpy as np
import pandas as pd
import pytz
from tvDatafeed import TvDatafeed, Interval

# Asset universe to scan
SCAN_UNIVERSE = {
    'INDIA_NSE': [
        ('NIFTY', 'NSE'), ('BANKNIFTY', 'NSE'), ('RELIANCE', 'NSE'), ('TCS', 'NSE'),
        ('HDFCBANK', 'NSE'), ('INFY', 'NSE'), ('ICICIBANK', 'NSE'), ('SBIN', 'NSE'),
        ('BHARTIARTL', 'NSE'), ('ITC', 'NSE'), ('KOTAKBANK', 'NSE'), ('LT', 'NSE'),
        ('WIPRO', 'NSE'), ('AXISBANK', 'NSE'), ('BAJFINANCE', 'NSE'), ('MARUTI', 'NSE'),
        ('TITAN', 'NSE'), ('SUNPHARMA', 'NSE'), ('HCLTECH', 'NSE'), ('ONGC', 'NSE')
    ],
    'CRYPTO': [
        ('BTCUSD', 'BINANCE'), ('ETHUSD', 'BINANCE'), ('BNBUSD', 'BINANCE'),
        ('SOLUSD', 'BINANCE'), ('XRPUSD', 'BINANCE'), ('ADAUSD', 'BINANCE'),
        ('DOGEUSD', 'BINANCE'), ('AVAXUSD', 'BINANCE'), ('DOTUSD', 'BINANCE'),
        ('LINKUSD', 'BINANCE'), ('MATICUSD', 'BINANCE'), ('UNIUSD', 'BINANCE')
    ],
    'FOREX': [
        ('XAUUSD', 'OANDA'), ('XAGUSD', 'OANDA'), ('EURUSD', 'OANDA'),
        ('GBPUSD', 'OANDA'), ('USDJPY', 'OANDA'), ('AUDUSD', 'OANDA'),
        ('USDCAD', 'OANDA'), ('NZDUSD', 'OANDA'), ('USOIL', 'OANDA'),
        ('WTICOUSD', 'OANDA'), ('XPTUSD', 'OANDA'), ('XPDUSD', 'OANDA')
    ],
    'US_STOCKS': [
        ('SPY', 'AMEX'), ('QQQ', 'NASDAQ'), ('AAPL', 'NASDAQ'), ('MSFT', 'NASDAQ'),
        ('GOOGL', 'NASDAQ'), ('AMZN', 'NASDAQ'), ('TSLA', 'NASDAQ'), ('NVDA', 'NASDAQ'),
        ('META', 'NASDAQ'), ('JPM', 'NYSE'), ('V', 'NYSE'), ('JNJ', 'NYSE')
    ]
}

def calculate_adx(df, period=14):
    high = df['high'].values.astype(float)
    low = df['low'].values.astype(float)
    close = df['close'].values.astype(float)
    n = len(close)
    if n < period + 1:
        return 0.0
    tr = np.zeros(n)
    for i in range(1, n):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i-1])
        lc = abs(low[i] - close[i-1])
        tr[i] = max(hl, hc, lc)
    atr = np.mean(tr[1:period+1])
    up_move = np.zeros(n)
    down_move = np.zeros(n)
    for i in range(1, n):
        up_move[i] = high[i] - high[i-1]
        down_move[i] = low[i-1] - low[i]
    plus_dm = np.zeros(n)
    minus_dm = np.zeros(n)
    for i in range(1, n):
        if up_move[i] > down_move[i] and up_move[i] > 0:
            plus_dm[i] = up_move[i]
        if down_move[i] > up_move[i] and down_move[i] > 0:
            minus_dm[i] = down_move[i]
    plus_di = 100 * np.mean(plus_dm[1:period+1]) / atr if atr > 0 else 0
    minus_di = 100 * np.mean(minus_dm[1:period+1]) / atr if atr > 0 else 0
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
    return round(dx, 2)

def calculate_rsi(close_prices, period=14):
    closes = close_prices.astype(float)
    deltas = np.diff(closes)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 100
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def calculate_alpha(dx, rsi, volume_ratio):
    trend_score = min(dx / 100, 1.0) * 40
    if rsi > 70:
        momentum_score = 20
    elif rsi > 55:
        momentum_score = 30
    elif rsi < 30:
        momentum_score = 25
    elif rsi < 45:
        momentum_score = 20
    else:
        momentum_score = 15
    vol_score = min(volume_ratio / 2, 1.0) * 30
    total = trend_score + momentum_score + vol_score
    if total >= 75:
        rating = "STRONG BUY"
    elif total >= 60:
        rating = "BUY"
    elif total >= 45:
        rating = "HOLD"
    elif total >= 30:
        rating = "WEAK"
    else:
        rating = "AVOID"
    return round(total, 1), rating

def run_scanner(market_filter=None):
    tv = TvDatafeed()
    results = []
    ist = pytz.timezone('Asia/Kolkata')
    now = pd.Timestamp.now(ist).strftime('%d %b %Y, %H:%M IST')

    universe = {}
    if market_filter and market_filter in SCAN_UNIVERSE:
        universe[market_filter] = SCAN_UNIVERSE[market_filter]
    else:
        universe = SCAN_UNIVERSE

    for market_name, assets in universe.items():
        for sym, ex in assets:
            try:
                df = tv.get_hist(symbol=sym, exchange=ex, interval=Interval.in_daily, n_bars=30)
                if df is None or df.empty or len(df) < 15:
                    continue
                close_prices = df['close'].values
                last_close = float(close_prices[-1])
                prev_close = float(close_prices[-2]) if len(close_prices) > 1 else last_close
                change_pct = round((last_close - prev_close) / prev_close * 100, 2) if prev_close > 0 else 0
                volumes = df['volume'].values.astype(float)
                avg_vol = np.mean(volumes[-10:]) if len(volumes) >= 10 else np.mean(volumes)
                recent_vol = np.mean(volumes[-3:]) if len(volumes) >= 3 else avg_vol
                vol_ratio = round(recent_vol / avg_vol, 2) if avg_vol > 0 else 1.0
                adx = calculate_adx(df)
                rsi = calculate_rsi(close_prices)
                alpha, rating = calculate_alpha(adx, rsi, vol_ratio)
                signal = "BUY" if alpha >= 60 else ("SELL" if alpha < 30 else "NEUTRAL")
                results.append({
                    'symbol': sym, 'exchange': ex, 'market': market_name,
                    'price': last_close, 'change_pct': change_pct,
                    'adx': adx, 'rsi': rsi, 'alpha': alpha,
                    'volume_ratio': vol_ratio, 'rating': rating, 'signal': signal
                })
            except Exception:
                continue

    results.sort(key=lambda x: x['alpha'], reverse=True)
    return {'scanned_at': now, 'total_scanned': len(results), 'results': results}
