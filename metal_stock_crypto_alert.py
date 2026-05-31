# metal_stock_crypto_alert.py
import yfinance as yf
from datetime import datetime
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# ====================== CONFIGURATION ======================
TICKERS = {
    "GC=F":  "Gold Futures",
    "SI=F":  "Silver Futures",
    "BTC-USD": "Bitcoin",
    "XRP-USD": "XRP (Ripple)",
    "XLM-USD": "Stellar (XLM)",
    "DJT":     "Trump Media & Technology (DJT)",
    "RUM":     "Rumble Inc. (RUM)"
}

ALERT_THRESHOLD = 3.0
RECIPIENT_EMAIL = "mike.boaz@ymail.com"

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# ===========================================================

def send_consolidated_email(results, alerts):
    """Send one email with full summary table"""
    subject = f"🚨 PRICE ALERT: {len(alerts)} asset(s) moved ±{ALERT_THRESHOLD}%"

    # Create a nice HTML table
    df = pd.DataFrame(results)
    df = df[['name', 'symbol', 'current_price', 'change_percent']]
    df.columns = ['Asset Name', 'Symbol', 'Current Price ($)', '% Change']
    
    html_table = df.to_html(index=False, border=1, classes="summary-table")
    
    body = f"""
    <h2>Price Movement Alert</h2>
    <p><strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p><strong>Alert Triggered:</strong> {len(alerts)} asset(s) moved ±{ALERT_THRESHOLD}% or more</p>
    
    <h3>Full Portfolio Summary</h3>
    {html_table}
    
    <hr>
    <p><em>This is an automated alert from your personal trading tracker.</em></p>
    """
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(f"✅ Consolidated email alert sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def get_current_price(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.fast_info
        
        current_price = info.get('lastPrice') or info.get('regularMarketPrice')
        previous_close = info.get('previousClose')
        
        if not current_price or not previous_close:
            return {"symbol": ticker_symbol, "error": "No price data"}

        change_percent = ((current_price - previous_close) / previous_close) * 100
        
        return {
            "name": TICKERS.get(ticker_symbol, ticker_symbol),
            "symbol": ticker_symbol,
            "current_price": round(current_price, 4),
            "change_percent": round(change_percent, 2),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"symbol": ticker_symbol, "error": str(e)}

def main():
    print("="*70)
    print("🚀 PRICE ALERT SCANNER STARTED")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = []
    alerts = []
    
    for symbol in TICKERS.keys():
        print(f"Checking {symbol}...")
        data = get_current_price(symbol)
        
        if "error" in data:
            print(f"❌ Error: {data['error']}")
            continue
            
        results.append(data)
        change = data['change_percent']
        
        arrow = "🟢" if change > 0 else "🔴"
        print(f"{arrow} {data['name']:30} | ${data['current_price']:.4f} | {change:+.2f}%")
        
        if abs(change) >= ALERT_THRESHOLD:
            alerts.append(data)
            print(f"   ⚠️  ALERT TRIGGERED for {data['name']}")
    
    # Send ONE consolidated email if any alerts were triggered
    if alerts:
        print(f"\n⚠️  Sending consolidated email with full summary...")
        send_consolidated_email(results, alerts)
    else:
        print("\n✅ No major movements detected. No email sent.")
    
    print("\n" + "="*70)
    print(f"SCAN COMPLETE - {len(alerts)} alert(s) triggered")
    print("="*70)

if __name__ == "__main__":
    main()
