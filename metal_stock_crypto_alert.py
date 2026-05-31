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

ALERT_THRESHOLD = 3.0  # Alert if change >= 3%
RECIPIENT_EMAIL = "mike.boaz@ymail.com"

# Email settings - Use environment variables for security (recommended)
SENDER_EMAIL = os.getenv("SENDER_EMAIL")          # e.g., your Gmail
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")    # App password (not regular password)
SMTP_SERVER = "smtp.gmail.com"                    # Change if using different provider
SMTP_PORT = 587
# ===========================================================

load_dotenv()  # Load environment variables from .env file

def send_email_alert(symbol, name, current_price, change_percent):
    """Send email alert when big move detected"""
    subject = f"🚨 PRICE ALERT: {name} moved {change_percent:+.2f}%"
    
    body = f"""
    <h2>Price Alert Triggered</h2>
    <p><strong>{name} ({symbol})</strong></p>
    <p><strong>Current Price:</strong> ${current_price:.4f}</p>
    <p><strong>Change:</strong> {change_percent:+.2f}% from previous close</p>
    <p><strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <hr>
    <p>This is an automated alert from your personal tracker.</p>
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
        print(f"✅ Email alert sent for {symbol}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

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
            "previous_close": round(previous_close, 4),
            "change_percent": round(change_percent, 2),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"symbol": ticker_symbol, "error": str(e)}

def main():
    print("🚀 Running Price Alert Scanner...\n")
    alerts_triggered = 0
    
    for symbol in TICKERS.keys():
        data = get_current_price(symbol)
        
        if "error" in data:
            print(f"❌ {symbol}: Error fetching data")
            continue
            
        name = data['name']
        change = data['change_percent']
        price = data['current_price']
        
        arrow = "🟢" if change > 0 else "🔴"
        print(f"{arrow} {name:30} | ${price:.4f} | {change:+.2f}%")
        
        # Check for alert
        if abs(change) >= ALERT_THRESHOLD:
            print(f"   ⚠️  ALERT: {name} moved {change:+.2f}% → Sending email!")
            send_email_alert(symbol, name, price, change)
            alerts_triggered += 1
    
    print(f"\n✅ Scan complete. {alerts_triggered} alert(s) sent.")

if __name__ == "__main__":
    main()
