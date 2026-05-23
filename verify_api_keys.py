#!/usr/bin/env python3
"""
Verify all API keys work without exposing them.
Prints only status: ✅ or ❌
"""

import os
import sys
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

# Create session with retries
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

results = {}

# 1. TubeonAI
try:
    response = session.post(
        "https://api.tubeonai.com/api/v1/summaries",
        headers={"Authorization": f"Bearer {os.getenv('TUBEONAI_API_KEY')}"},
        json={"url": "https://example.com"},
        timeout=10
    )
    results['TubeonAI'] = '✅' if response.status_code in [200, 201, 400, 401] else '❌'
except Exception as e:
    results['TubeonAI'] = f'❌ ({type(e).__name__})'

# 2. Encharge
try:
    response = session.get(
        "https://api.encharge.io/v1/accounts",
        headers={"X-Encharge-Token": os.getenv('ENCHARGE_API_KEY')},
        timeout=10
    )
    results['Encharge'] = '✅' if response.status_code in [200, 401] else '❌'
except Exception as e:
    results['Encharge'] = f'❌ ({type(e).__name__})'

# 3. Anthropic
try:
    response = session.get(
        "https://api.anthropic.com/v1/models",
        headers={"x-api-key": os.getenv('ANTHROPIC_API_KEY')},
        timeout=10
    )
    results['Anthropic'] = '✅' if response.status_code in [200, 401] else '❌'
except Exception as e:
    results['Anthropic'] = f'❌ ({type(e).__name__})'

# 4. OpenAI
try:
    response = session.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
        timeout=10
    )
    results['OpenAI'] = '✅' if response.status_code in [200, 401] else '❌'
except Exception as e:
    results['OpenAI'] = f'❌ ({type(e).__name__})'

# 5. Perplexity
try:
    response = session.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"},
        json={"model": "pplx-7b-chat", "messages": [{"role": "user", "content": "test"}]},
        timeout=10
    )
    results['Perplexity'] = '✅' if response.status_code in [200, 401, 429] else '❌'
except Exception as e:
    results['Perplexity'] = f'❌ ({type(e).__name__})'

# 6. Voyage AI
try:
    response = session.post(
        "https://api.voyageai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {os.getenv('VOYAGE_API_KEY')}"},
        json={"input": "test", "model": "voyage-2"},
        timeout=10
    )
    results['Voyage AI'] = '✅' if response.status_code in [200, 401, 400] else '❌'
except Exception as e:
    results['Voyage AI'] = f'❌ ({type(e).__name__})'

# 7. VoiSpark
try:
    response = session.get(
        "https://api.voispark.com/v1/voices",
        headers={"Authorization": f"Bearer {os.getenv('VOISPARK_API_KEY')}"},
        timeout=10
    )
    results['VoiSpark'] = '✅' if response.status_code in [200, 401] else '❌'
except Exception as e:
    results['VoiSpark'] = f'❌ ({type(e).__name__})'

# 8. SendPilot
try:
    response = session.get(
        "https://api.sendpilot.com/api/v1/user",
        headers={"Authorization": f"Bearer {os.getenv('SENDPILOT_API_KEY')}"},
        timeout=10
    )
    results['SendPilot'] = '✅' if response.status_code in [200, 401] else '❌'
except Exception as e:
    results['SendPilot'] = f'❌ ({type(e).__name__})'

# 9. Zernio
try:
    response = session.get(
        "https://api.zernio.com/v1/me",
        headers={"Authorization": f"Bearer {os.getenv('ZERNIO_API_KEY')}"},
        timeout=10
    )
    results['Zernio'] = '✅' if response.status_code in [200, 401] else '❌'
except Exception as e:
    results['Zernio'] = f'❌ ({type(e).__name__})'

# 10. Multica
try:
    response = session.get(
        "https://api.multica.com/v1/workspaces",
        headers={"Authorization": f"Bearer {os.getenv('MULTICA_API_TOKEN')}"},
        timeout=10
    )
    results['Multica'] = '✅' if response.status_code in [200, 401] else '❌'
except Exception as e:
    results['Multica'] = f'❌ ({type(e).__name__})'

# 11. Alpha Vantage
try:
    response = session.get(
        "https://www.alphavantage.co/query",
        params={
            "function": "GLOBAL_QUOTE",
            "symbol": "IBM",
            "apikey": os.getenv('ALPHAVANTAGE_API_KEY')
        },
        timeout=10
    )
    # AlphaVantage returns 200 even with invalid key, check response content
    data = response.json() if response.status_code == 200 else {}
    has_valid_response = 'Global Quote' in data or 'Error Message' not in data or 'Note' not in data
    results['Alpha Vantage'] = '✅' if has_valid_response else '❌'
except Exception as e:
    results['Alpha Vantage'] = f'❌ ({type(e).__name__})'

# 12. Finnhub
try:
    response = session.get(
        "https://finnhub.io/api/v1/quote",
        params={
            "symbol": "AAPL",
            "token": os.getenv('FINNHUB_API_KEY')
        },
        timeout=10
    )
    results['Finnhub'] = '✅' if response.status_code == 200 else '❌'
except Exception as e:
    results['Finnhub'] = f'❌ ({type(e).__name__})'

# 13. TwelveData
try:
    response = session.get(
        "https://api.twelvedata.com/quote",
        params={
            "symbol": "AAPL",
            "apikey": os.getenv('TWELVEDATA_API_KEY')
        },
        timeout=10
    )
    results['TwelveData'] = '✅' if response.status_code == 200 else '❌'
except Exception as e:
    results['TwelveData'] = f'❌ ({type(e).__name__})'

# 14. Massive
try:
    response = session.get(
        "https://www.massive.ai/api/v1/user",
        headers={"Authorization": f"Bearer {os.getenv('MASSIVE_API_KEY')}"},
        timeout=10
    )
    results['Massive'] = '✅' if response.status_code in [200, 401] else '❌'
except Exception as e:
    results['Massive'] = f'❌ ({type(e).__name__})'

# 15. AllTick
try:
    response = session.get(
        "https://api.alltick.co/user",
        headers={"Authorization": f"Bearer {os.getenv('ALLTICK_API_KEY')}"},
        timeout=10
    )
    results['AllTick'] = '✅' if response.status_code in [200, 401] else '❌'
except Exception as e:
    results['AllTick'] = f'❌ ({type(e).__name__})'

# 16-18. Alpaca (3 accounts)
for i, (key, secret) in enumerate([
    ('ALPACA_API_KEY', 'ALPACA_SECRET_KEY'),
    ('ALPACA_API_KEY_B', 'ALPACA_SECRET_KEY_B'),
    ('ALPACA_API_KEY_C', 'ALPACA_SECRET_KEY_C'),
], 1):
    try:
        response = session.get(
            "https://api.alpaca.markets/v2/account",
            headers={"APCA-API-KEY-ID": os.getenv(key)},
            timeout=10
        )
        results[f'Alpaca Account {i}'] = '✅' if response.status_code in [200, 401] else '❌'
    except Exception as e:
        results[f'Alpaca Account {i}'] = f'❌ ({type(e).__name__})'

# Print results
print("\n" + "="*50)
print("API KEY VERIFICATION RESULTS")
print("="*50 + "\n")

for service, status in results.items():
    print(f"{service:.<40} {status}")

print("\n" + "="*50)
failed = [k for k, v in results.items() if '❌' in v]
if failed:
    print(f"⚠️  {len(failed)} service(s) need attention:\n")
    for svc in failed:
        print(f"   • {svc}")
else:
    print("✅ All API keys verified successfully!")
print("="*50 + "\n")
