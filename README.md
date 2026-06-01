# Metal, Crypto & Stock Price Alert System

A personal automated trading monitor built for Mike Boaz.

### Assets Being Tracked:
- **Gold Futures** (GC=F)
- **Silver Futures** (SI=F)
- **Bitcoin** (BTC-USD)
- **XRP** (XRP-USD)
- **Stellar** (XLM-USD)
- **Trump Media** (DJT)
- **Rumble Inc.** (RUM)

### Key Features
- Real-time price data from Yahoo Finance
- **Dynamic Threshold Alerts** — each asset has its own custom % threshold
- **Consolidated Email Alerts** — sends **one email** with a clean, highlighted table when any asset hits its threshold
- **Price History Logging** — automatically saves all price data to `price_history.csv` on every run
- Runs automatically every hour using GitHub Actions

### Dynamic Thresholds (Default)
| Asset          | Threshold |
|----------------|---------|
| Gold (GC=F)    | 1.8%    |
| Silver (SI=F)  | 2.5%    |
| Bitcoin        | 4.5%    |
| XRP / XLM      | 5.0%    |
| DJT / RUM      | 6.5%    |

### Files in Repository
- `metal_stock_crypto_alert.py` → Main script (dynamic alerts + CSV logging)
- `requirements.txt` → Python dependencies
- `.github/workflows/price-alert.yml` → Hourly automation
- `price_history.csv` → Historical price data (auto-generated)
- `README.md`

### How It Works
Every hour the script:
1. Checks current prices and % change for all assets
2. Saves the data to `price_history.csv`
3. If any asset exceeds **its own threshold**, sends **one consolidated email** with full portfolio summary

You can download `price_history.csv` anytime from GitHub to analyze performance.

---

**Personal Trading Tool**  
Built for Mike Boaz | Last updated: May 2026
