# metal_stock_crypto_alert.py
import yfinance as yf
from datetime import datetime
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

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

load_dotenv()

def send_email_alert(symbol, name, current_price, change_percent):
    subject = f"🚨 PRICE ALERT: {name} moved {change_percent:+.2f}%"
    
    body = f"""
    <h2>Price Alert Triggered</h2>
    <p><strong>{name} ({symbol})</strong></p>
    <p><strong>Current Price:</strong> ${current_price:.4f}</p>
    <p><strong>Change:</strong> {change_percent:+.2f}%</p>
    <p><strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <hr>
    <p>This is an automated alert from your personal trading tracker.</p>
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
        print(f"✅ Email alert successfully sent for {symbol}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email for {symbol}: {e}")
        return False

def get_current_price(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.fast_info
        
        current_price = info.get('lastPrice') or info.get('regularMarketPrice')
        previous_close = info.get('previousClose')
        
        if not current_price or not previous_close:
            return {"symbol": ticker_symbol, "error": "No price data available"}

        change_percent = ((current_price - previous_close) / previous_close) * 100
        
        return {
            "name": TICKERS.get(ticker_symbol, ticker_symbol),
            "symbol": ticker_symbol,
            "current_price": round(current_price, 4),
            "previous_close": round(previous_close, 4),
            "change_percent": round(change_percent, 2),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"symbol": ticker_symbol, "error": str(e)}

def main():
    print("="*60)
    print("🚀 PRICE ALERT SCANNER STARTED")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    alerts_triggered = 0
    
    for symbol in TICKERS.keys():
        print(f"\nChecking {symbol}...")
        data = get_current_price(symbol)
        
        if "error" in data:
            print(f"❌ Error fetching {symbol}: {data['error']}")
            continue
            
        name = data['name']
        change = data['change_percent']
        price = data['current_price']
        
        arrow = "🟢" if change > 0 else "🔴"
        print(f"{arrow} {name:30} | ${price:.4f} | {change:+.2f}%")
        
        # Trigger alert if movement is 3% or more
        if abs(change) >= ALERT_THRESHOLD:
            print(f"   ⚠️  BIG MOVE DETECTED! Sending email alert...")
            success = send_email_alert(symbol, name, price, change)
            if success:
                alerts_triggered += 1
    
    print("\n" + "="*60)
    print(f"✅ SCAN COMPLETE - {alerts_triggered} alert(s) triggered")
    print("="*60)

if __name__ == "__main__":
    main()
