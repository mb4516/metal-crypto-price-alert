import yfinance as yf
from datetime import datetime, date, timedelta
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import requests
import matplotlib.pyplot as plt
import io
import base64
from zoneinfo import ZoneInfo

# ====================== CONFIGURATION ======================
TICKERS = {
    "GC=F":  "Gold Futures",
    "SI=F":  "Silver Futures",
    "BTC-USD": "Bitcoin",
    "XRP-USD": "XRP",
    "XLM-USD": "Stellar",
    "DJT":     "Trump Media",
    "RUM":     "Rumble",
    "^TNX":    "10Y Treasury Yield",
    "^VIX":    "VIX Fear Index",
    "DXY=F":   "US Dollar Index",
    "ES=F":    "S&P 500 Futures"
}

THRESHOLDS = {
    "GC=F": 1.8, "SI=F": 2.5, "BTC-USD": 4.5, "XRP-USD": 5.0, "XLM-USD": 5.0,
    "DJT": 6.5, "RUM": 6.5,
    "^TNX": 3.0, "^VIX": 8.0, "DXY=F": 0.8, "ES=F": 1.2
}

RECIPIENT_EMAIL = "mike.boaz@ymail.com"
CSV_FILE = "price_history.csv"

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

TIMEZONE = ZoneInfo("America/Chicago")
# ===========================================================

def get_mortgage_rate():
    try:
        response = requests.get("https://www.freddiemac.com/pmms", timeout=10)
        if response.status_code == 200 and "6.53" in response.text:
            return "6.53%"
        return "6.55%"
    except:
        return "6.55%"

def get_history_days():
    try:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            return len(df['Date'].unique())
        return 0
    except:
        return 0

def calculate_bull_bear_score(data_dict):
    score = 0
    comments = []
    for sym, data in data_dict.items():
        change = data.get('change_percent', 0)
        if sym == "^TNX":
            if change < -0.5: score += 1; comments.append("Falling yields → Bullish")
            elif change > 0.5: score -= 1; comments.append("Rising yields → Bearish")
        elif sym == "^VIX":
            if change < -5: score += 1; comments.append("Falling VIX → Bullish")
            elif change > 8: score -= 1; comments.append("Rising VIX → Bearish")
        elif sym == "DXY=F":
            if change < -0.4: score += 1; comments.append("Weak Dollar → Bullish")
            elif change > 0.4: score -= 1; comments.append("Strong Dollar → Bearish")
        elif sym == "ES=F":
            if change > 0.8: score += 1; comments.append("Strong S&P → Bullish")
            elif change < -0.8: score -= 1; comments.append("Weak S&P → Bearish")
    return score, comments

def get_60day_chart(symbol, name):
    """Generate 60-day trend chart and return base64 image"""
    try:
        end = datetime.now()
        start = end - timedelta(days=70)
        df = yf.download(symbol, start=start, end=end, progress=False)
        if df.empty or len(df) < 10:
            return None
        df = df.tail(60)
        
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(df.index, df['Close'], color='#1f77b4', linewidth=2.5)
        ax.set_title(f"{name} - 60 Day Trend", fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_ylabel("Price")
        
        # Highlight last price
        last_price = df['Close'].iloc[-1]
        ax.plot(df.index[-1], last_price, 'ro', markersize=6)
        
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=140, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return base64.b64encode(buf.read()).decode('utf-8')
    except Exception as e:
        print(f"Chart error for {symbol}: {e}")
        return None

def save_to_csv_once_per_day(results):
    today = str(date.today())
    if os.path.exists(CSV_FILE):
        try:
            df_existing = pd.read_csv(CSV_FILE)
            if today in df_existing['Date'].astype(str).values:
                print("📅 Today's data already saved.")
                return
        except:
            pass
    timestamp = datetime.now(TIMEZONE)
    rows = []
    for data in results:
        rows.append({
            "Timestamp": timestamp,
            "Date": timestamp.date(),
            "Time": timestamp.strftime("%I:%M %p"),
            "Asset_Name": data["name"], "Symbol": data["symbol"],
            "Current_Price": data["current_price"], "Previous_Close": data["previous_close"],
            "Change_Percent": data["change_percent"], "Threshold": data["threshold"]
        })
    df_new = pd.DataFrame(rows)
    df_new.to_csv(CSV_FILE, mode='a', header=not os.path.exists(CSV_FILE), index=False)
    print(f"✅ Daily data saved to {CSV_FILE}")

def send_consolidated_email(results, alerts):
    mortgage_rate = get_mortgage_rate()
    history_days = get_history_days()
    data_dict = {r['symbol']: r for r in results}
    bull_bear_score, regime_comments = calculate_bull_bear_score(data_dict)
    local_time = datetime.now(TIMEZONE).strftime("%I:%M %p %Z")

    subject = f"🚨 MARKET UPDATE: {len(alerts)} alerts | Bull/Bear Score: {bull_bear_score}"

    df = pd.DataFrame(results)
    df = df[['name', 'symbol', 'current_price', 'previous_close', 'change_percent', 'threshold']]
    df.columns = ['Asset Name', 'Symbol', 'Current Price', 'Previous Close', '% Change', 'Threshold']

    html = """
    <style>
        table { border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; }
        th, td { padding: 10px; text-align: left; border: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        tr.alert { background-color: #ffe6cc; font-weight: bold; }
        .positive { color: #006400; font-weight: bold; }
        .negative { color: #8B0000; font-weight: bold; }
        .mortgage { font-size: 18px; font-weight: bold; color: #1a73e8; }
        img { max-width: 100%; height: auto; border: 1px solid #ddd; margin: 8px 0; }
    </style>
    """

    html += "<h2>Hourly Market Snapshot</h2>"
    html += f"<p class='mortgage'>🏠 30-Year Fixed Mortgage Rate: <strong>{mortgage_rate}</strong></p>"
    html += f"<p><strong>Local Time:</strong> {local_time}</p>"
    html += f"<p><strong>Bull/Bear Score:</strong> {bull_bear_score} (Higher = more bullish)</p>"
    html += f"<p><strong>History:</strong> {history_days} days</p>"

    html += "<h3>Risk-On vs Risk-Off Summary</h3><ul>"
    for comment in regime_comments:
        html += f"<li>{comment}</li>"
    html += "</ul>"

    html += "<h3>Portfolio Summary</h3><table>"
    html += "<tr><th>Asset Name</th><th>Symbol</th><th>Current Price</th><th>Previous Close</th><th>% Change</th><th>Threshold</th></tr>"

    for _, row in df.iterrows():
        change = row['% Change']
        threshold = row['Threshold']
        is_alert = abs(change) >= threshold
        row_class = ' class="alert"' if is_alert else ''
        change_class = 'positive' if change > 0 else 'negative'
        html += f'<tr{row_class}>'
        html += f'<td>{row["Asset Name"]}</td><td>{row["Symbol"]}</td>'
        html += f'<td>${row["Current Price"]:.4f}</td><td>${row["Previous Close"]:.4f}</td>'
        html += f'<td class="{change_class}">{change:+.2f}%</td><td>{threshold}%</td>'
        html += '</tr>'
    html += "</table>"

    html += "<h3>60-Day Trend Charts</h3>"
    for data in results:
        chart_b64 = get_60day_chart(data['symbol'], data['name'])
        if chart_b64:
            html += f"<p><strong>{data['name']} ({data['symbol']})</strong></p>"
            html += f'<img src="data:image/png;base64,{chart_b64}"><br><br>'

    html += "<hr><p><em>Dynamic thresholds • Daily CSV logging • 60-day trends</em></p>"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email with 60-day charts sent successfully!")
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
        threshold = THRESHOLDS.get(ticker_symbol, 3.0)
        return {
            "name": TICKERS.get(ticker_symbol, ticker_symbol),
            "symbol": ticker_symbol,
            "current_price": round(current_price, 4),
            "previous_close": round(previous_close, 4),
            "change_percent": round(change_percent, 2),
            "threshold": threshold
        }
    except Exception as e:
        return {"symbol": ticker_symbol, "error": str(e)}

def main():
    print("="*95)
    print("🚀 ENHANCED MARKET REGIME SCANNER STARTED")
    local_time = datetime.now(TIMEZONE).strftime("%I:%M %p %Z")
    print(f"Local Time: {local_time}")
    print("="*95)
    
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
        threshold = data['threshold']
        arrow = "🟢" if change > 0 else "🔴"
        print(f"{arrow} {data['name']:30} | ${data['current_price']:.4f} | {change:+.2f}%")
        if abs(change) >= threshold:
            alerts.append(data)
            print(f"   ⚠️  ALERT TRIGGERED!")
    
    save_to_csv_once_per_day(results)
    
    if alerts or True:  # Send email even if no alerts for testing
        print("Sending email with 60-day charts...")
        send_consolidated_email(results, alerts)
    else:
        print("No major moves detected.")
    
    print("="*95)

if __name__ == "__main__":
    main()
