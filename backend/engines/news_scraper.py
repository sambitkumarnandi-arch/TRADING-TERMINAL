import requests
import re
import html
from datetime import datetime
import pytz
import random

SENTIMENT_KEYWORDS = {
    'bullish': ['surge', 'rally', 'gain', 'bullish', 'upgrade', 'buy', 'positive', 'growth', 'record high', 'breakout',
                'outperform', 'beat', 'exceed', 'bull run', 'uptrend', 'green', 'profit', 'recovery', 'boom', 'soar',
                'jump', 'climb', 'rise', 'expansion', 'opportunity', 'strong'],
    'bearish': ['plunge', 'crash', 'decline', 'fall', 'bearish', 'downgrade', 'sell', 'negative', 'recession', 'inflation',
                'drop', 'loss', 'cut', 'debt', 'crisis', 'downturn', 'red', 'slowdown', 'slump', 'fear', 'sell-off',
                'tumble', 'slide', 'weak', 'risk', 'volatile', 'uncertainty'],
    'neutral': ['flat', 'mixed', 'steady', 'stable', 'unchanged', 'hold', 'neutral', 'expected', 'announce', 'report',
                'meeting', 'decision', 'forecast', 'estimate', 'guidance', 'update', 'review', 'monitor', 'watch']
}

GEO_KEYWORDS = {
    'United States': ['us', 'usa', 'united states', 'america', 'american', 'new york', 'washington', 'fed', 'federal reserve', 'wall street', 'nasdaq', 'nyse'],
    'United Kingdom': ['uk', 'britain', 'british', 'london', 'england', 'ftse', 'boe', 'bank of england'],
    'China': ['china', 'chinese', 'beijing', 'shanghai', 'hong kong', 'shenzhen', 'pboc'],
    'India': ['india', 'indian', 'mumbai', 'delhi', 'bangalore', 'nifty', 'sensex', 'rbi', 'sebi'],
    'Japan': ['japan', 'japanese', 'tokyo', 'nikkei', 'boj', 'bank of japan'],
    'European Union': ['europe', 'eu', 'european', 'frankfurt', 'paris', 'berlin', 'ecb', 'european central bank'],
    'Middle East': ['middle east', 'saudi', 'uae', 'dubai', 'qatar', 'opec', 'oil', 'crude', 'gulf'],
    'Russia': ['russia', 'russian', 'moscow'],
    'Australia': ['australia', 'australian', 'sydney', 'rba'],
    'Brazil': ['brazil', 'brazilian', 'sao paulo', 'bovespa'],
    'Canada': ['canada', 'canadian', 'toronto', 'tsx'],
    'Switzerland': ['switzerland', 'swiss', 'zurich', 'snb'],
}

NARRATIVE_TEMPLATES = {
    'bullish': {
        'equity': 'Equity markets responding positively. Sector rotation toward related stocks expected.',
        'forex': 'Currency strengthening on this catalyst. Volatility expected in related pairs.',
        'crypto': 'Crypto momentum building. Institutional interest likely to accelerate.',
        'commodity': 'Commodity prices supported. Supply-demand dynamics shifting favorably.',
        'economy': 'Growth outlook improving. Risk-on sentiment boosting risk assets.',
        'bonds': 'Bond market pricing in positive outlook. Yield curve dynamics shifting.',
        'mutual_funds': 'MFs increasing allocation to growth assets. Sectoral fund flows positive.',
        'default': 'Markets pricing positive outcomes. Momentum likely to sustain.'
    },
    'bearish': {
        'equity': 'Risk-off sentiment dominating. Defensive positioning recommended.',
        'forex': 'Safe havens gaining. Carry trades under pressure.',
        'crypto': 'Crypto facing headwinds. Support levels being tested.',
        'commodity': 'Demand concerns rising. Inventory builds may accelerate.',
        'economy': 'Uncertainty rising. Central bank response critical to monitor.',
        'bonds': 'Flight to safety boosting bond prices. Yield compression underway.',
        'mutual_funds': 'MFs rotating to defensive sectors. Cash positions increasing.',
        'default': 'Defensive posture warranted. Wait for confirmation before positioning.'
    },
    'neutral': {
        'default': 'Markets awaiting clarity. Range-bound trading expected near-term.'
    }
}

MF_NARRATIVES = {
    'equity': {
        'bullish': 'Mutual funds are expected to increase equity exposure. Large-cap and flexi-cap funds may see inflows. Sectoral funds in banking and IT likely to benefit.',
        'bearish': 'Fund managers may trim equity positions and increase cash allocation. Defensive sectors like FMCG and pharma preferred.',
        'neutral': 'Funds likely to maintain current allocation with stock-specific approach. Waiting for clearer direction.'
    },
    'crypto': {
        'bullish': 'Crypto-focused funds and ETFs seeing increased subscriptions. Institutional products gaining traction.',
        'bearish': 'Fund advisors cautioning against overexposure. Risk management protocols being activated.',
        'neutral': 'Funds maintaining strategic allocation. Waiting for regulatory clarity.'
    },
    'commodity': {
        'bullish': 'Commodity funds and Gold ETFs attracting inflows. Natural resources funds well-positioned.',
        'bearish': 'Funds reducing commodity overweight. Moving to cash or defensive assets.',
        'neutral': 'Strategic allocation maintained. Tactical adjustments based on price action.'
    },
    'bonds': {
        'bullish': 'Bond funds seeing strong inflows. Duration strategies being extended by fund managers.',
        'bearish': 'Funds shortening duration. Credit quality concerns prompting defensive moves.',
        'neutral': 'Income funds maintaining laddered approach. Waiting for rate clarity.'
    },
    'economy': {
        'bullish': 'Aggressive funds increasing equity allocation. Balanced advantage funds favoring equities.',
        'bearish': 'Fund managers moving to safe havens. Liquid and money market funds preferred.',
        'neutral': 'Hybrid funds maintaining dynamic allocation. Waiting for data confirmation.'
    },
    'default': {
        'bullish': 'Fund houses bullish on risk assets. Systematic investment plans seeing higher flows.',
        'bearish': 'Asset allocation favoring protection. SWP and dividend yield strategies gaining.',
        'neutral': 'Funds in wait-and-watch mode. Diversified approach recommended.'
    }
}

def classify_sentiment(text):
    text_lower = text.lower()
    bs = sum(1 for w in SENTIMENT_KEYWORDS['bullish'] if w in text_lower)
    br = sum(1 for w in SENTIMENT_KEYWORDS['bearish'] if w in text_lower)
    return 'bullish' if bs > br + 1 else ('bearish' if br > bs + 1 else 'neutral')

def detect_category(title, text):
    combined = (title + ' ' + text).lower()
    categories = {
        'equity': ['stock', 'share', 'equity', 'nifty', 'sensex', 's&p', 'nasdaq', 'dow', 'ipo',
                   'dividend', 'earnings', 'rally', 'bull market', 'bear market', 'index'],
        'forex': ['forex', 'currency', 'dollar', 'euro', 'pound', 'yen', 'rupee', 'exchange rate', 'usd', 'eur'],
        'crypto': ['bitcoin', 'crypto', 'blockchain', 'ethereum', 'btc', 'eth', 'altcoin', 'defi', 'nft'],
        'commodity': ['gold', 'silver', 'oil', 'crude', 'commodity', 'copper', 'gas', 'wheat', 'corn'],
        'bonds': ['bond', 'yield', 'treasury', 'g-sec', 'corporate bond', 'credit spread', 'duration', 'coupon'],
        'mutual_funds': ['mutual fund', 'mf', 'sip', 'nav', 'folio', 'aum', 'fund house', 'etf', 'index fund'],
        'economy': ['gdp', 'inflation', 'cpi', 'interest rate', 'fed', 'central bank', 'recession', 'unemployment']
    }
    scores = {cat: sum(1 for k in keys if k in combined) for cat, keys in categories.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 'economy'

def get_geo_location(title, text):
    combined = (title + ' ' + text).lower()
    for country, keywords in GEO_KEYWORDS.items():
        if any(k in combined for k in keywords):
            coords = {
                'United States': [37.0902, -95.7129],
                'United Kingdom': [55.3781, -3.4360],
                'China': [35.8617, 104.1954],
                'India': [20.5937, 78.9629],
                'Japan': [36.2048, 138.2529],
                'European Union': [48.8566, 2.3522],
                'Middle East': [24.4539, 54.3773],
                'Russia': [61.5240, 105.3188],
                'Australia': [-25.2744, 133.7751],
                'Brazil': [-14.2350, -51.9253],
                'Canada': [56.1304, -106.3468],
                'Switzerland': [46.8182, 8.2275],
            }
            return country, coords.get(country, [0, 0])
    return 'Global', [20, 0]

def generate_narrative(sentiment, category, title):
    base = NARRATIVE_TEMPLATES.get(sentiment, {}).get(category, NARRATIVE_TEMPLATES.get(sentiment, {}).get('default', ''))
    if not base:
        base = NARRATIVE_TEMPLATES['neutral']['default']
    word_count = len(title.split())
    detail = ' This is a significant development with broad market implications.' if word_count > 12 else ' Market participants are closely monitoring.'
    return base + detail

def generate_mf_take(sentiment, category, title):
    cat_templates = MF_NARRATIVES.get(category, MF_NARRATIVES['default'])
    return cat_templates.get(sentiment, MF_NARRATIVES['default']['neutral'])

def fetch_news_web():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    news_items = []

    # Try TradingView's feed
    try:
        resp = requests.get('https://news.tradingview.com/feed/?format=json', headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items', data.get('articles', data.get('data', [])))
            if isinstance(items, list):
                for item in items[:30]:
                    title = item.get('title', item.get('headline', ''))
                    if not title: continue
                    summary = item.get('summary', item.get('description', ''))
                    source = item.get('source', item.get('source_name', 'TradingView'))
                    if isinstance(source, dict): source = source.get('title', 'TradingView')
                    sentiment = classify_sentiment(title + ' ' + summary)
                    category = detect_category(title, summary)
                    country, coords = get_geo_location(title, summary)
                    narrative = generate_narrative(sentiment, category, title)
                    mf_take = generate_mf_take(sentiment, category, title)
                    news_items.append({
                        'id': len(news_items) + 1,
                        'title': html.unescape(title),
                        'summary': html.unescape(summary[:250]) if summary else '',
                        'url': item.get('url', ''),
                        'source': source,
                        'timestamp': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M'),
                        'date': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d %b %Y'),
                        'sentiment': sentiment,
                        'category': category,
                        'narrative': narrative,
                        'mf_take': mf_take,
                        'country': country,
                        'lat': coords[0],
                        'lon': coords[1]
                    })
    except: pass

    if news_items: return news_items

    # Fallback: scrape HTML
    try:
        resp = requests.get('https://www.tradingview.com/news/', headers=headers, timeout=15)
        if resp.status_code == 200:
            titles = re.findall(r'"title":"([^"]+)"', resp.text)
            for t in titles[:25]:
                t = html.unescape(t).strip()
                if len(t) < 10: continue
                sentiment = classify_sentiment(t)
                category = detect_category(t, '')
                country, coords = get_geo_location(t, '')
                narrative = generate_narrative(sentiment, category, t)
                mf_take = generate_mf_take(sentiment, category, t)
                news_items.append({
                    'id': len(news_items) + 1, 'title': t, 'summary': '',
                    'url': '', 'source': 'TradingView',
                    'timestamp': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M'),
                    'date': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d %b %Y'),
                    'sentiment': sentiment, 'category': category,
                    'narrative': narrative, 'mf_take': mf_take,
                    'country': country, 'lat': coords[0], 'lon': coords[1]
                })
    except: pass

    if news_items: return news_items

    # Final fallback: Google Finance
    try:
        resp = requests.get('https://www.google.com/finance/?hl=en', headers=headers, timeout=15)
        if resp.status_code == 200:
            titles = re.findall(r'<a[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</a>', resp.text)
            if not titles:
                titles = re.findall(r'"title":"([^"]+)"', resp.text)
            for t in titles[:20]:
                t = html.unescape(t).strip()
                if len(t) < 10: continue
                sentiment = classify_sentiment(t)
                category = detect_category(t, '')
                country, coords = get_geo_location(t, '')
                narrative = generate_narrative(sentiment, category, t)
                mf_take = generate_mf_take(sentiment, category, t)
                news_items.append({
                    'id': len(news_items) + 1, 'title': t, 'summary': '',
                    'url': '', 'source': 'Google Finance',
                    'timestamp': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M'),
                    'date': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d %b %Y'),
                    'sentiment': sentiment, 'category': category,
                    'narrative': narrative, 'mf_take': mf_take,
                    'country': country, 'lat': coords[0], 'lon': coords[1]
                })
    except: pass

    return news_items

MOCK_NEWS = [
    {'title': 'S&P 500 Hits Record High on Tech Rally', 'summary': 'Technology stocks surge as AI optimism drives investor sentiment to all-time highs across major indices.', 'source': 'Bloomberg', 'category': 'equity', 'sentiment': 'bullish'},
    {'title': 'Fed Signals Potential Rate Cut in September', 'summary': 'Federal Reserve officials indicate willingness to ease policy if inflation continues its moderating trend.', 'source': 'Reuters', 'category': 'economy', 'sentiment': 'bullish'},
    {'title': 'Crude Oil Prices Surge on Supply Concerns', 'summary': 'Brent crude jumps above $85 as Middle East tensions threaten global supply routes and production.', 'source': 'CNBC', 'category': 'commodity', 'sentiment': 'bullish'},
    {'title': 'Bitcoin Breaks $70,000 Resistance Level', 'summary': 'Cryptocurrency market exceeds $2.5T market cap as institutional adoption and ETF flows accelerate globally.', 'source': 'CoinDesk', 'category': 'crypto', 'sentiment': 'bullish'},
    {'title': 'European Markets Mixed Ahead of ECB Decision', 'summary': 'Traders cautious as European Central Bank prepares for crucial monetary policy announcement.', 'source': 'Financial Times', 'category': 'equity', 'sentiment': 'neutral'},
    {'title': 'US Dollar Strengthens on Solid Economic Data', 'summary': 'Greenback gains against major peers as US labor market and GDP data exceed expectations.', 'source': 'Bloomberg', 'category': 'forex', 'sentiment': 'bearish'},
    {'title': 'Nifty 50 Consolidates After Record-Breaking Run', 'summary': 'Indian benchmark takes a breather as profit-booking emerges near all-time highs. Broader market resilient.', 'source': 'Economic Times', 'category': 'equity', 'sentiment': 'neutral'},
    {'title': 'Gold Prices Retreat as Bond Yields Climb', 'summary': 'Precious metal slides from recent highs on rising US Treasury yields and hawkish Fed commentary.', 'source': 'Kitco', 'category': 'commodity', 'sentiment': 'bearish'},
    {'title': 'OPEC+ Considers Extending Production Cuts', 'summary': 'Oil alliance debates maintaining output restrictions through Q4 to support flagging crude prices.', 'source': 'Reuters', 'category': 'commodity', 'sentiment': 'bullish'},
    {'title': 'China GDP Growth Slows to Multi-Year Low', 'summary': 'Chinese economy faces headwinds from property sector weakness and faltering consumer confidence.', 'source': 'Xinhua', 'category': 'economy', 'sentiment': 'bearish'},
    {'title': 'Mutual Fund SIP Inflows Hit Record High', 'summary': 'Systematic investment plan contributions cross milestone as retail participation in equity MFs surges.', 'source': 'Morningstar', 'category': 'mutual_funds', 'sentiment': 'bullish'},
    {'title': 'Tesla Shares Jump on Delivery Beat', 'summary': 'EV maker exceeds quarterly estimates on strong demand in China and Europe markets.', 'source': 'CNBC', 'category': 'equity', 'sentiment': 'bullish'},
    {'title': 'US Bond Market Flashing Recession Warning', 'summary': 'Yield curve inversion deepens as short-term rates exceed long-term, historically a recession signal.', 'source': 'WSJ', 'category': 'bonds', 'sentiment': 'bearish'},
    {'title': 'UK Inflation Holds Steady at 2.2%', 'summary': 'Bank of England expected to maintain cautious stance as services inflation remains elevated.', 'source': 'Financial Times', 'category': 'economy', 'sentiment': 'neutral'},
    {'title': 'Mutual Fund ELSS Schemes See Tax-Saving Inflows', 'summary': 'Equity-linked saving schemes attract heavy investments as deadline for tax planning approaches.', 'source': 'Value Research', 'category': 'mutual_funds', 'sentiment': 'bullish'},
    {'title': 'Ethereum ETF Inflows Surge Past $1 Billion Mark', 'summary': 'Spot Ethereum ETFs see record weekly flows as institutional investors expand crypto allocation.', 'source': 'CoinDesk', 'category': 'crypto', 'sentiment': 'bullish'},
    {'title': 'Japan Government Bond Yields Hit Decade High', 'summary': 'BOJ policy normalization fuels bond selloff as traders brace for further tightening.', 'source': 'Nikkei', 'category': 'bonds', 'sentiment': 'bearish'},
    {'title': 'Goldman Sachs Upgrades India Equity to Overweight', 'summary': 'Investment bank cites strong earnings growth and demographic dividend for bullish India stance.', 'source': 'Reuters', 'category': 'equity', 'sentiment': 'bullish'},
    {'title': 'Commodity Supercycle May Extend Through Decade', 'summary': 'Analysts predict sustained commodity demand from green energy transition and infrastructure spending.', 'source': 'McKinsey', 'category': 'commodity', 'sentiment': 'bullish'},
    {'title': 'Debt Mutual Funds See Inflows as Rates Stabilize', 'summary': 'Investors flock to bond funds and target maturity funds as interest rate outlook turns favorable.', 'source': 'CRISIL', 'category': 'mutual_funds', 'sentiment': 'bullish'},
    {'title': 'European Bond Yields Rise on Growth Optimism', 'summary': 'German bund yields climb as Eurozone economic data beats expectations across manufacturing and services.', 'source': 'Bloomberg', 'category': 'bonds', 'sentiment': 'bearish'},
    {'title': 'Small-Cap Mutual Funds Rally 35% in 6 Months', 'summary': 'Aggressive funds outperform benchmarks as mid and small-cap segments attract strong retail flows.', 'source': 'Economic Times', 'category': 'mutual_funds', 'sentiment': 'bullish'},
    {'title': 'Gold ETF Holdings Rise for Fifth Straight Month', 'summary': 'Central bank buying and geopolitical uncertainty drive sustained demand for gold-backed ETFs.', 'source': 'World Gold Council', 'category': 'commodity', 'sentiment': 'bullish'},
    {'title': 'Crypto Mutual Funds Launch for Retail Investors', 'summary': 'SEBI-registered fund houses launch India\'s first crypto-focused mutual fund products for retail.', 'source': 'Business Standard', 'category': 'crypto', 'sentiment': 'bullish'},
]

def get_news():
    news = fetch_news_web()
    if not news:
        news = []
        for i, item in enumerate(MOCK_NEWS):
            sentiment = item.get('sentiment', classify_sentiment(item['title']))
            category = item.get('category', detect_category(item['title'], item['summary']))
            country, coords = get_geo_location(item['title'], item.get('summary', ''))
            narrative = generate_narrative(sentiment, category, item['title'])
            mf_take = generate_mf_take(sentiment, category, item['title'])
            news.append({
                'id': i + 1,
                'title': item['title'],
                'summary': item['summary'],
                'url': item.get('url', ''),
                'source': item.get('source', 'Financial Press'),
                'timestamp': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M'),
                'date': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d %b %Y'),
                'sentiment': sentiment,
                'category': category,
                'narrative': narrative,
                'mf_take': mf_take,
                'country': country,
                'lat': coords[0],
                'lon': coords[1]
            })
    return news
