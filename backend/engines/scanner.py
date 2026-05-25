import numpy as np
import pandas as pd
import pytz
from tvDatafeed import TvDatafeed, Interval

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
    ],
    'CRYPTO_PERP': [
        ('BTCUSDT', 'BINANCE'), ('ETHUSDT', 'BINANCE'), ('BNBUSDT', 'BINANCE'),
        ('SOLUSDT', 'BINANCE'), ('XRPUSDT', 'BINANCE'), ('ADAUSDT', 'BINANCE'),
        ('DOGEUSDT', 'BINANCE'), ('AVAXUSDT', 'BINANCE'), ('DOTUSDT', 'BINANCE'),
        ('LINKUSDT', 'BINANCE'), ('MATICUSDT', 'BINANCE'), ('UNIUSDT', 'BINANCE'),
        ('ATOMUSDT', 'BINANCE'), ('LTCUSDT', 'BINANCE'), ('FILUSDT', 'BINANCE'),
        ('APTUSDT', 'BINANCE'), ('ARBUSDT', 'BINANCE'), ('OPUSDT', 'BINANCE'),
        ('INJUSDT', 'BINANCE'), ('TIAUSDT', 'BINANCE'), ('NEARUSDT', 'BINANCE'),
        ('SUIUSDT', 'BINANCE'), ('SEIUSDT', 'BINANCE'), ('PEPEUSDT', 'BINANCE'),
        ('WIFUSDT', 'BINANCE'), ('RUNEUSDT', 'BINANCE'), ('AAVEUSDT', 'BINANCE'),
        ('FETUSDT', 'BINANCE'), ('STRKUSDT', 'BINANCE'), ('ENAUSDT', 'BINANCE')
    ]
}

CRYPTO_BENCHMARKS = [
    ('ETHBTC', 'BINANCE'),
    ('SOLBTC', 'BINANCE'),
]

def fetch_benchmarks(tv):
    bench_data = {}
    for sym, ex in CRYPTO_BENCHMARKS:
        try:
            df = tv.get_hist(symbol=sym, exchange=ex, interval=Interval.in_daily, n_bars=90)
            if df is not None and not df.empty and len(df) >= 20:
                bench_data[sym] = df['close'].values.astype(float)
        except Exception:
            continue
    return bench_data

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

def calculate_beta(asset_returns, benchmark_returns):
    if len(asset_returns) < 10 or len(benchmark_returns) < 10:
        return 1.0
    min_len = min(len(asset_returns), len(benchmark_returns))
    a_ret = asset_returns[-min_len:]
    b_ret = benchmark_returns[-min_len:]
    cov = np.cov(a_ret, b_ret)[0][1]
    var_b = np.var(b_ret)
    if var_b == 0:
        return 1.0
    return cov / var_b

def calculate_volatility(close_prices, period=14):
    if len(close_prices) < period:
        return 0.0
    returns = np.diff(close_prices[-period-1:]) / close_prices[-period-2:-1]
    return round(np.std(returns) * 100, 2)

def run_scanner(market_filter=None):
    tv = TvDatafeed()
    results = []
    perp_results = []
    ist = pytz.timezone('Asia/Kolkata')
    now = pd.Timestamp.now(ist).strftime('%d %b %Y, %H:%M IST')

    universe = {}
    if market_filter and market_filter in SCAN_UNIVERSE:
        if market_filter == 'CRYPTO_PERP':
            pass
        else:
            universe[market_filter] = SCAN_UNIVERSE[market_filter]
    else:
        universe = {k: v for k, v in SCAN_UNIVERSE.items() if k != 'CRYPTO_PERP'}

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

    results.sort(key=lambda x: x.get('alpha', 0), reverse=True)
    output = {'scanned_at': now, 'total_scanned': len(results), 'results': results}

    run_perp = (market_filter == 'CRYPTO_PERP') or (market_filter is None)
    if run_perp:
        try:
            bench_data = fetch_benchmarks(tv)
            perp_assets = SCAN_UNIVERSE['CRYPTO_PERP']

            for sym, ex in perp_assets:
                try:
                    df = tv.get_hist(symbol=sym, exchange=ex, interval=Interval.in_daily, n_bars=90)
                    if df is None or df.empty or len(df) < 20:
                        continue

                    close_prices = df['close'].values.astype(float)
                    last_close = float(close_prices[-1])
                    high_prices = df['high'].values.astype(float)
                    low_prices = df['low'].values.astype(float)

                    price_delta_7d = ((close_prices[-1] - close_prices[-8]) / close_prices[-8]) * 100 if len(close_prices) >= 8 else 0
                    price_delta_14d = ((close_prices[-1] - close_prices[-15]) / close_prices[-15]) * 100 if len(close_prices) >= 15 else 0
                    price_delta_30d = ((close_prices[-1] - close_prices[-31]) / close_prices[-31]) * 100 if len(close_prices) >= 31 else 0
                    delta_positive = price_delta_7d > 0 or price_delta_14d > 0
                    asset_returns = np.diff(close_prices) / close_prices[:-1]

                    bench_alphas = {}
                    for bench_sym, bench_close in bench_data.items():
                        if len(bench_close) < 20:
                            continue
                        bench_returns = np.diff(bench_close) / bench_close[:-1]
                        beta = calculate_beta(asset_returns, bench_returns)
                        expected_return = beta * np.mean(bench_returns[-len(asset_returns):])
                        actual_return = np.mean(asset_returns[-min(len(asset_returns), 30):])
                        alpha_val = round((actual_return - expected_return) * 100, 2)
                        bench_alphas[bench_sym] = {'beta': round(beta, 2), 'alpha': alpha_val}

                    adx = calculate_adx(df)
                    rsi = calculate_rsi(close_prices)
                    atr = np.mean([high_prices[i] - low_prices[i] for i in range(-14, 0)]) if len(high_prices) >= 14 else 0
                    atr_pct = round((atr / last_close) * 100, 2) if last_close > 0 else 0
                    volumes = df['volume'].values.astype(float)
                    avg_vol = np.mean(volumes[-20:]) if len(volumes) >= 20 else np.mean(volumes)
                    recent_vol = np.mean(volumes[-3:]) if len(volumes) >= 3 else avg_vol
                    vol_ratio = round(recent_vol / avg_vol, 2) if avg_vol > 0 else 1.0

                    composite_alpha_score = 0.0
                    for b in bench_alphas.values():
                        composite_alpha_score += b['alpha']
                    composite_alpha_score = round(composite_alpha_score / len(bench_alphas), 2) if bench_alphas else 0

                    breakout = adx > 25 and price_delta_14d > 5 and composite_alpha_score > 0
                    breakdown = adx > 25 and price_delta_14d < -5 and composite_alpha_score < 0

                    if adx >= 25:
                        perp_signal = "BUY" if (rsi > 55 and price_delta_14d > 0) else ("SELL" if (rsi < 45 and price_delta_14d < 0) else "NEUTRAL")
                    elif adx >= 15:
                        perp_signal = "NEUTRAL"
                    else:
                        perp_signal = "WEAK"

                    alpha_score = min(composite_alpha_score + 50, 100)
                    alpha_score = max(alpha_score, 0)
                    if alpha_score >= 75:
                        rating = "STRONG BUY"
                    elif alpha_score >= 60:
                        rating = "BUY"
                    elif alpha_score >= 45:
                        rating = "HOLD"
                    elif alpha_score >= 30:
                        rating = "WEAK"
                    else:
                        rating = "AVOID"

                    perp_results.append({
                        'symbol': sym, 'exchange': ex, 'market': 'CRYPTO_PERP',
                        'price': last_close, 'adx': adx, 'rsi': rsi,
                        'volatility_pct': atr_pct, 'volume_ratio': vol_ratio,
                        'delta_7d': round(price_delta_7d, 2),
                        'delta_14d': round(price_delta_14d, 2),
                        'delta_30d': round(price_delta_30d, 2),
                        'delta_positive': bool(delta_positive),
                        'alpha_vs_benchmarks': bench_alphas,
                        'composite_alpha': composite_alpha_score,
                        'alpha_score': round(alpha_score, 1),
                        'rating': rating, 'signal': perp_signal,
                        'breakout': bool(breakout), 'breakdown': bool(breakdown),
                    })
                except Exception:
                    continue

            perp_results.sort(key=lambda x: x['composite_alpha'], reverse=True)
        except Exception:
            pass

        output['crypto_perp'] = {
            'total_scanned': len(perp_results),
            'results': perp_results,
            'breakouts': [r for r in perp_results if r.get('breakout')],
            'breakdowns': [r for r in perp_results if r.get('breakdown')],
        }

    return output
