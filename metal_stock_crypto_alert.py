import yfinance as yf
from datetime import datetime, date, timedelta
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import requests
import matplotlib.pyplot as plt
import io
import base64
from zoneinfo import ZoneInfo

# ====================== CONFIGURATION ======================
TICKERS = { ... }  # Keep your existing TICKERS and THRESHOLDS

RECIPIENT_EMAIL = "mike.boaz@ymail.com"
CSV_FILE = "price_history.csv"
TIMEZONE = ZoneInfo("America/Chicago")

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# ===========================================================

def get_60day_chart(symbol, name):
    try:
        end = datetime.now()
        start = end - timedelta(days=70)  # extra buffer
        df = yf.download(symbol, start=start, end=end, progress=False)
        if df.empty:
            return None
        df = df.tail(60)
        
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(df.index, df['Close'], color='blue', linewidth=2)
        ax.set_title(f"{name} - 60 Day Trend", fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Color last point
        last_price = df['Close'].iloc[-1]
        ax.plot(df.index[-1], last_price, 'ro')
        
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=120)
        buf.seek(0)
        plt.close()
        return base64.b64encode(buf.read()).decode('utf-8')
    except:
        return None

# ... (keep get_mortgage_rate, get_history_days, calculate_bull_bear_score, save_to_csv_once_per_day)

def send_consolidated_email(results, alerts):
    # ... (existing code for mortgage, score, etc.)
    
    html += "<h3>60-Day Trend Charts</h3>"
    for data in results:
        chart_b64 = get_60day_chart(data['symbol'], data['name'])
        if chart_b64:
            html += f"<p><strong>{data['name']}</strong></p>"
            html += f'<img src="data:image/png;base64,{chart_b64}" style="max-width:100%; border:1px solid #ddd;"><br><br>'

    # rest of email ...

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html'))

    # ... send code remains the same
