import numpy as np
import pytz
import pandas as pd
from tvDatafeed import TvDatafeed, Interval

def process_footprint(df):
    if df is None or df.empty:
        return df
    ist_tz = pytz.timezone('Asia/Kolkata')
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize('UTC').tz_convert(ist_tz)
    else:
        df.index = df.index.tz_convert(ist_tz)
    df = df.sort_index()
    df['Vol_SMA_20'] = df['volume'].rolling(window=20).mean()
    df['Rel_Volume'] = df['volume'] / df['Vol_SMA_20']
    df['Rel_Volume'] = df['Rel_Volume'].fillna(1.0)
    df['Candle_Type'] = np.where(df['close'] > df['open'], 'Bullish', 'Bearish')
    return df

def extract_zones(df, timeframe_label, top_n=3):
    if df is None or df.empty or 'Rel_Volume' not in df.columns:
        return []
    top_df = df.sort_values(by='Rel_Volume', ascending=False).head(top_n).copy()
    zones = []
    for index, row in top_df.iterrows():
        action = "Support Zone Formed" if row['Candle_Type'] == 'Bullish' else "Resistance Wall Formed"
        color = "#00ff7f" if row['Candle_Type'] == 'Bullish' else "#ff3366"
        zones.append({
            '_dt': index,
            'Time': index.strftime('%d %b %H:%M IST'),
            'TF': timeframe_label,
            'Action': action,
            'Volume_Spike': f"{row['Rel_Volume']:.1f}x",
            'Zone': f"{float(row['low']):.2f} - {float(row['high']):.2f}",
            'Color': color
        })
    zones.sort(key=lambda z: z['_dt'])
    return zones

def get_realtime_footprint(symbol, market_type):
    symbol = symbol.upper().strip()
    ex_map = {
        'FOREX': ['OANDA','FOREXCOM','FX_IDC'],
        'BINANCE_SPOT': ['BINANCE','COINBASE','KUCOIN'],
        'BINANCE_PERP': ['BINANCE','BYBIT','OKX'],
        'INDIA_NSE': ['NSE','BSE'], 'INDIA_BSE': ['BSE','NSE'],
        'US_STOCKS': ['NASDAQ','NYSE','AMEX']
    }
    exchanges_to_try = ex_map.get(market_type, ['BINANCE','OANDA','NSE','NASDAQ'])
    try:
        tv = TvDatafeed()
        df_3m = None; df_15m = None; df_30m = None; df_4h = None; successful_exchange = None
        for ex in exchanges_to_try:
            temp_3m = tv.get_hist(symbol=symbol, exchange=ex, interval=Interval.in_3_minute, n_bars=200)
            if temp_3m is not None and not temp_3m.empty and 'volume' in temp_3m.columns:
                df_3m = temp_3m.dropna(subset=['open','high','low','close','volume'])
                temp_15m = tv.get_hist(symbol=symbol, exchange=ex, interval=Interval.in_15_minute, n_bars=200)
                df_15m = temp_15m.dropna(subset=['open','high','low','close','volume']) if temp_15m is not None and not temp_15m.empty else pd.DataFrame()
                temp_30m = tv.get_hist(symbol=symbol, exchange=ex, interval=Interval.in_30_minute, n_bars=200)
                df_30m = temp_30m.dropna(subset=['open','high','low','close','volume']) if temp_30m is not None and not temp_30m.empty else pd.DataFrame()
                temp_4h = tv.get_hist(symbol=symbol, exchange=ex, interval=Interval.in_4_hour, n_bars=200)
                df_4h = temp_4h.dropna(subset=['open','high','low','close','volume']) if temp_4h is not None and not temp_4h.empty else pd.DataFrame()
                successful_exchange = ex; break
        if df_3m is None or df_3m.empty or len(df_3m) < 25:
            return None, "Live data connection failed."
        if df_3m['volume'].sum() == 0:
            return None, f"'{symbol}' is a Spot Index (Volume=0). Use a Future Contract."
        df_3m = process_footprint(df_3m)
        df_15m = process_footprint(df_15m)
        df_30m = process_footprint(df_30m)
        df_4h = process_footprint(df_4h)
        recent_3m = df_3m.tail(5).copy()
        live_alerts = []
        for index, row in recent_3m.iterrows():
            if row['Rel_Volume'] >= 2.0:
                action = "ACCUMULATION (Whale Buying)" if row['Candle_Type'] == 'Bullish' else "DISTRIBUTION (Whale Selling)"
                color = "#00ff7f" if row['Candle_Type'] == 'Bullish' else "#ff3366"
                live_alerts.append({
                    'Time': index.strftime('%H:%M IST'),
                    'Action': action,
                    'Volume_Spike': f"{row['Rel_Volume']:.1f}x",
                    'Price': float(row['close']),
                    'Color': color
                })
        live_alerts.sort(key=lambda a: a['Time'])
        intraday_raw = extract_zones(df_15m, "15m", 3) + extract_zones(df_30m, "30m", 3)
        intraday_raw.sort(key=lambda z: z['_dt'])
        for z in intraday_raw: del z['_dt']
        intraday_zones = intraday_raw
        macro_raw = extract_zones(df_4h, "4H", 4)
        macro_raw.sort(key=lambda z: z['_dt'])
        for z in macro_raw: del z['_dt']
        macro_zones = macro_raw
        return {
            'Symbol': symbol, 'Exchange': successful_exchange,
            'Live_Alerts': live_alerts, 'Intraday_Zones': intraday_zones, 'Macro_Zones': macro_zones
        }, "Success"
    except Exception as e:
        return None, f"Institutional Feed Error: {str(e)}"
