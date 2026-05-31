# Metal, Crypto & Stock Price Alert System

A personal automated price tracker and alert system for metals, crypto, and meme stocks.

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
- **Consolidated Email Alerts**: Sends **one single email** containing a full summary table of **all assets** whenever any asset moves **±3%** or more
- Runs automatically every hour on GitHub Actions
- Clean logging for easy debugging

### How It Works
Every hour the script checks price changes.  
If **any** asset moves 3% or more (up or down), you will receive **one email** at `mike.boaz@ymail.com` showing:
- Current price of every symbol
- Daily % gain/loss for all assets
- Clear highlighting of the big movers

### Repository Files
- `metal_stock_crypto_alert.py` → Main alert script (consolidated email version)
- `requirements.txt`
- `.github/workflows/price-alert.yml` → Hourly automation
- `README.md`

---

**Personal Trading Tool**  
Built for Mike Boaz | Last updated: May 2026
