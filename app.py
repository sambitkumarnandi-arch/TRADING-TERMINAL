import os
import sys
import json
import base64
import io
import uvicorn

# Ensure backend directory is in path for engine imports
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import date, timedelta
from engines.midpoint import get_midpoint_data, create_midpoint_excel, format_price
from engines.trend11 import get_11trend_data, create_11trend_excel
from engines.gann144 import get_gann_data, create_gann_excel, analyze_gann
from engines.footprint import get_realtime_footprint
from engines.news_scraper import get_news
from engines.scanner import run_scanner

app = FastAPI(title="Quant Terminal v4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="frontend")

class RunAllRequest(BaseModel):
    symbol: str = "NIFTY"
    market_type: str = "INDIA_NSE"
    start_date: str = None
    end_date: str = None
    timeframe: str = "Daily"
    multiplier: int = 1

class SymbolRequest(BaseModel):
    symbol: str
    market_type: str

class GannRequest(BaseModel):
    symbol: str
    market_type: str
    start_date: str = None
    end_date: str = None
    timeframe: str = "Daily"
    multiplier: int = 1

@app.get("/")
async def root():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "ok", "message": "Quant Terminal v4"}

@app.post("/api/midpoint")
async def api_midpoint(req: SymbolRequest):
    data, msg = get_midpoint_data(req.symbol, req.market_type)
    if data is None:
        raise HTTPException(status_code=404, detail=msg)
    excel = create_midpoint_excel(data)
    b64 = base64.b64encode(excel.getvalue()).decode()
    result = {k: float(v) if isinstance(v, (int, float)) else v for k, v in data.items()}
    result['_excel_b64'] = b64
    result['_excel_filename'] = f"{req.symbol}_MidPoint.xlsx"
    return result

@app.post("/api/trend11")
async def api_trend11(req: SymbolRequest):
    data, msg = get_11trend_data(req.symbol, req.market_type)
    if data is None:
        raise HTTPException(status_code=404, detail=msg)
    excel = create_11trend_excel(data['Dataframe'], data['Targets'], data['Stats'], data['Symbol'])
    b64 = base64.b64encode(excel.getvalue()).decode()
    result = {
        'Symbol': data['Symbol'], 'Exchange': data['Exchange'],
        'Date_Range': data['Date_Range'], 'Close': float(data['Close']),
        'Volatility': float(data['Volatility']), 'Expected_Range': float(data['Expected_Range']),
        'Degrees_List': data['Degrees_List'],
        'Targets': {
            'BUY': {str(k): float(v) for k, v in data['Targets']['BUY'].items()},
            'SELL': {str(k): float(v) for k, v in data['Targets']['SELL'].items()},
            'FACTOR': {str(k): float(v) for k, v in data['Targets']['FACTOR'].items()},
            'RANGE': {str(k): float(v) for k, v in data['Targets']['RANGE'].items()}
        },
        'Live_Price': float(data['Live_Price']),
        'Market_Status': data['Market_Status'], 'Status_Color': data['Status_Color'],
        '_excel_b64': b64, '_excel_filename': f"{req.symbol}_11Trend.xlsx"
    }
    return result

@app.post("/api/gann144")
async def api_gann144(req: GannRequest):
    today = date.today()
    start = req.start_date if req.start_date else str(today - timedelta(days=90))
    end = req.end_date if req.end_date else str(today)
    start_dt = date.fromisoformat(start)
    end_dt = date.fromisoformat(end)
    df = get_gann_data(req.symbol, req.market_type, start_dt, end_dt, req.timeframe)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for Gann analysis.")
    last_close, buy_status, sell_status = analyze_gann(df, req.multiplier)
    excel = create_gann_excel(df, req.symbol, buy_status, sell_status, req.multiplier)
    b64 = base64.b64encode(excel.getvalue()).decode()
    max_high = float(df['HIGH'].max() * req.multiplier)
    min_low = float(df['LOW'].min() * req.multiplier)
    diff = max_high - min_low
    time_cycles = [36, 45, 54, 63, 72, 81, 90, 108, 126, 144]
    price_cycles = [0.25, 0.3125, 0.375, 0.4375, 0.5, 0.5625, 0.625, 0.75, 0.875, 1.0]
    matrix = []
    for tc, pc in zip(time_cycles, price_cycles):
        active_diff = diff * pc
        h1 = max_high - active_diff
        res = [h1, h1-diff, h1-2*diff, h1-3*diff, h1-4*diff]
        l1 = min_low + active_diff
        sup = [l1, l1+diff, l1+2*diff, l1+3*diff, l1+4*diff]
        matrix.append({'tc': tc, 'pc': pc, 'h': [round(x, 6) for x in res], 'l': [round(x, 6) for x in sup]})
    return {
        'Symbol': req.symbol, 'Multiplier': req.multiplier,
        'Timeframe': req.timeframe, 'Last_Close': round(float(last_close), 6),
        'Max_High': round(max_high, 6), 'Min_Low': round(min_low, 6),
        'Diff': round(diff, 6), 'Buy_Status': buy_status, 'Sell_Status': sell_status,
        'Matrix': matrix,
        '_excel_b64': b64, '_excel_filename': f"{req.symbol}_Gann_144.xlsx"
    }

@app.post("/api/footprint")
async def api_footprint(req: SymbolRequest):
    data, msg = get_realtime_footprint(req.symbol, req.market_type)
    if data is None:
        raise HTTPException(status_code=404, detail=msg)
    result = {
        'Symbol': data['Symbol'], 'Exchange': data['Exchange'],
        'Live_Alerts': [
            {'Time': a['Time'], 'Action': a['Action'], 'Volume_Spike': a['Volume_Spike'],
             'Price': float(a['Price']), 'Color': a['Color']}
            for a in data['Live_Alerts']
        ],
        'Intraday_Zones': data['Intraday_Zones'],
        'Macro_Zones': data['Macro_Zones']
    }
    return result

@app.get("/api/news")
async def api_news():
    news = get_news()
    sents = {'bullish': len([n for n in news if n['sentiment'] == 'bullish']),
             'bearish': len([n for n in news if n['sentiment'] == 'bearish']),
             'neutral': len([n for n in news if n['sentiment'] == 'neutral'])}
    cats = {}
    for n in news:
        c = n['category']
        cats[c] = cats.get(c, 0) + 1
    return {'news': news, 'sentiment_counts': sents, 'category_counts': cats}

@app.get("/api/scanner")
@app.get("/api/scanner/{market}")
async def api_scanner(market: str = None):
    result = run_scanner(market)
    return result

@app.post("/api/run-all")
async def api_run_all(req: RunAllRequest):
    today = date.today()
    start = req.start_date if req.start_date else str(today - timedelta(days=90))
    end = req.end_date if req.end_date else str(today)
    results = {}
    # Midpoint
    mp_data, mp_msg = get_midpoint_data(req.symbol, req.market_type)
    if mp_data:
        mp_excel = create_midpoint_excel(mp_data)
        results['midpoint'] = {k: float(v) if isinstance(v, (int, float)) else v for k, v in mp_data.items()}
        results['midpoint']['_excel_b64'] = base64.b64encode(mp_excel.getvalue()).decode()
    else:
        results['midpoint'] = {'error': mp_msg}
    # 11-Trend
    t11_data, t11_msg = get_11trend_data(req.symbol, req.market_type)
    if t11_data:
        t11_excel = create_11trend_excel(t11_data['Dataframe'], t11_data['Targets'], t11_data['Stats'], t11_data['Symbol'])
        results['trend11'] = {
            'Symbol': t11_data['Symbol'], 'Exchange': t11_data['Exchange'],
            'Close': float(t11_data['Close']), 'Volatility': float(t11_data['Volatility']),
            'Expected_Range': float(t11_data['Expected_Range']), 'Live_Price': float(t11_data['Live_Price']),
            'Market_Status': t11_data['Market_Status'], 'Degrees_List': t11_data['Degrees_List'],
            'Targets': {
                'BUY': {str(k): float(v) for k, v in t11_data['Targets']['BUY'].items()},
                'SELL': {str(k): float(v) for k, v in t11_data['Targets']['SELL'].items()}
            }
        }
        results['trend11']['_excel_b64'] = base64.b64encode(t11_excel.getvalue()).decode()
    else:
        results['trend11'] = {'error': t11_msg}
    # Gann 144
    start_dt = date.fromisoformat(start)
    end_dt = date.fromisoformat(end)
    gann_df = get_gann_data(req.symbol, req.market_type, start_dt, end_dt, req.timeframe)
    if not gann_df.empty:
        last_close, buy_status, sell_status = analyze_gann(gann_df, req.multiplier)
        gann_excel = create_gann_excel(gann_df, req.symbol, buy_status, sell_status, req.multiplier)
        results['gann144'] = {
            'Symbol': req.symbol, 'Last_Close': round(float(last_close), 6),
            'Buy_Status': buy_status, 'Sell_Status': sell_status,
            '_excel_b64': base64.b64encode(gann_excel.getvalue()).decode()
        }
    else:
        results['gann144'] = {'error': 'No data for Gann analysis.'}
    # Footprint
    fp_data, fp_msg = get_realtime_footprint(req.symbol, req.market_type)
    if fp_data:
        results['footprint'] = {
            'Symbol': fp_data['Symbol'], 'Exchange': fp_data['Exchange'],
            'Live_Alerts': [{'Time': a['Time'], 'Action': a['Action'], 'Volume_Spike': a['Volume_Spike'], 'Price': float(a['Price']), 'Color': a['Color']} for a in fp_data['Live_Alerts']],
            'Intraday_Zones': fp_data['Intraday_Zones'],
            'Macro_Zones': fp_data['Macro_Zones']
        }
    else:
        results['footprint'] = {'error': fp_msg}
    return results

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
