import numpy as np
import pandas as pd
import pytz
from datetime import timedelta, datetime, timezone
from tvDatafeed import TvDatafeed, Interval

tv = TvDatafeed()
ist = pytz.timezone('Asia/Kolkata')
ist_offset = timezone(timedelta(hours=5, minutes=30))

YFINANCE_NSE = {
    'NIFTY': '^NSEI', 'BANKNIFTY': '^NSEBANK',
    'RELIANCE': 'RELIANCE.NS', 'TCS': 'TCS.NS',
    'HDFCBANK': 'HDFCBANK.NS', 'INFY': 'INFY.NS',
    'ICICIBANK': 'ICICIBANK.NS', 'SBIN': 'SBIN.NS',
    'BHARTIARTL': 'BHARTIARTL.NS', 'ITC': 'ITC.NS',
    'KOTAKBANK': 'KOTAKBANK.NS', 'LT': 'LT.NS',
    'WIPRO': 'WIPRO.NS', 'AXISBANK': 'AXISBANK.NS',
    'BAJFINANCE': 'BAJFINANCE.NS', 'MARUTI': 'MARUTI.NS',
    'TITAN': 'TITAN.NS', 'SUNPHARMA': 'SUNPHARMA.NS',
    'HCLTECH': 'HCLTECH.NS', 'ONGC': 'ONGC.NS',
}

YFINANCE_US = {
    'SPY': 'SPY', 'QQQ': 'QQQ', 'AAPL': 'AAPL', 'MSFT': 'MSFT',
    'GOOGL': 'GOOGL', 'AMZN': 'AMZN', 'TSLA': 'TSLA', 'NVDA': 'NVDA',
    'META': 'META', 'JPM': 'JPM', 'V': 'V', 'JNJ': 'JNJ',
}

YFINANCE_MAP = {}
YFINANCE_MAP.update(YFINANCE_NSE)
YFINANCE_MAP.update(YFINANCE_US)

INTERVAL_MAP = {
    '1m': ('1m', '7d'), '5m': ('5m', '1mo'), '15m': ('15m', '1mo'),
    '30m': ('30m', '1mo'), '1h': ('1h', '5d'), '1H': ('1h', '5d'),
    '4h': ('1h', '1mo'), '4H': ('1h', '1mo'),
    '1d': ('1d', '6mo'), '1D': ('1d', '6mo'),
    'daily': ('1d', '6mo'), 'Daily': ('1d', '6mo'),
}

def n_bars_to_period(n_bars, interval):
    if interval in ('1m',): return '7d'
    if interval in ('5m','15m','30m'): return '1mo'
    if interval in ('1h','1H'): return '5d' if n_bars <= 120 else '1mo'
    if interval in ('4h','4H'): return '1mo' if n_bars <= 180 else '3mo'
    return '6mo'

def fetch_ohlcv(symbol, market_type, interval='1h', n_bars=50):
    try:
        # For NSE and US stocks, try yfinance first
        if market_type in ('INDIA_NSE',) and symbol in YFINANCE_NSE:
            df = _fetch_yfinance(YFINANCE_NSE[symbol], interval, n_bars)
            if df is not None: return df, 'yfinance'
        if market_type in ('US_STOCKS',) and symbol in YFINANCE_US:
            df = _fetch_yfinance(YFINANCE_US[symbol], interval, n_bars)
            if df is not None: return df, 'yfinance'
    except Exception:
        pass

    # Fallback to tvDatafeed
    try:
        ex_map = {
            'FOREX': ['OANDA','FOREXCOM','FX_IDC','FX'],
            'BINANCE_SPOT': ['BINANCE','COINBASE','KUCOIN'],
            'BINANCE_PERP': ['BINANCE','BYBIT','OKX'],
            'INDIA_NSE': ['NSE','BSE'],
            'INDIA_BSE': ['BSE','NSE'],
            'US_STOCKS': ['NASDAQ','NYSE','AMEX'],
            'CRYPTO': ['BINANCE','COINBASE'],
            'CRYPTO_PERP': ['BINANCE','BYBIT'],
        }
        exchanges = ex_map.get(market_type, ['NSE','BINANCE','OANDA'])
        tv_interval = _tv_interval(interval)
        for ex in exchanges:
            df = tv.get_hist(symbol=symbol, exchange=ex, interval=tv_interval, n_bars=n_bars)
            if df is not None and not df.empty:
                df = df[['open','high','low','close','volume']].copy()
                df.columns = ['open','high','low','close','volume']
                # tvDatafeed returns naive timestamps - assume IST for NSE/BSE, UTC for others
                if ex in ('NSE', 'BSE'):
                    if df.index.tzinfo is None:
                        df.index = df.index.tz_localize(ist)
                else:
                    if df.index.tzinfo is None:
                        df.index = df.index.tz_localize('UTC').tz_convert(ist)
                return df, f'tvDatafeed({ex})'
    except Exception:
        pass

    return None, 'no data'

def _fetch_yfinance(yf_symbol, interval, n_bars):
    import yfinance as yf
    yf_interval, yf_period = INTERVAL_MAP.get(interval, ('1h', '5d'))
    period = n_bars_to_period(n_bars, interval)
    df = yf.download(yf_symbol, period=period, interval=yf_interval, progress=False, auto_adjust=True)
    if df is None or df.empty:
        return None
    df.columns = [col[0].lower() for col in df.columns]
    df = df[['open','high','low','close','volume']].copy()
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize(ist)
    else:
        df.index = df.index.tz_convert(ist)
    return df

def _tv_interval(interval):
    mapping = {
        '1m': Interval.in_1_minute, '5m': Interval.in_5_minutes,
        '15m': Interval.in_15_minutes, '30m': Interval.in_30_minutes,
        '1h': Interval.in_1_hour, '1H': Interval.in_1_hour,
        '4h': Interval.in_4_hour, '4H': Interval.in_4_hour,
        '1d': Interval.in_daily, '1D': Interval.in_daily,
        'daily': Interval.in_daily, 'Daily': Interval.in_daily,
    }
    return mapping.get(interval, Interval.in_1_hour)
