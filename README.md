# Metal, Crypto & Stock Price Alert System

A personal automated price tracker and alert system built for monitoring high-interest assets.

### Assets Being Tracked:
- **Gold Futures** (GC=F)
- **Silver Futures** (SI=F)
- **Bitcoin** (BTC-USD)
- **XRP** (XRP-USD)
- **Stellar** (XLM-USD)
- **Trump Media** (DJT)
- **Rumble Inc.** (RUM)

### Features
- Fetches real-time prices using Yahoo Finance
- Sends email alerts when any asset moves **±3%** or more from previous close
- Runs automatically every hour using GitHub Actions
- Clean logging for easy monitoring

### How It Works
The script runs every hour on GitHub. It checks the price change for each asset. If any asset moves 3% or more (up or down), you will receive an email alert at **mike.boaz@ymail.com**.

### Setup Summary
1. GitHub Secrets added (`SENDER_EMAIL` & `SENDER_PASSWORD`)
2. Gmail App Password configured
3. Workflow file created (`.github/workflows/price-alert.yml`)

### Files in this Repository
- `metal_stock_crypto_alert.py` → Main Python script
- `requirements.txt` → Required Python packages
- `.github/workflows/price-alert.yml` → Automated scheduling
- `README.md` → This file

---

**Built as a personal trading tool**  
Last updated: May 2026
