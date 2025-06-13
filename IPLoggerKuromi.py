from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import threading
import webbrowser
import time
import requests
import datetime

app = Flask(__name__)
CORS(app)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iplogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Discord webhook URL - put your webhook URL here or leave as empty string
DISCORD_WEBHOOK_URL = ""

class IPLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100))
    user_agent = db.Column(db.String(300))
    timestamp = db.Column(db.Float)

with app.app_context():
    db.create_all()

# Simple in-memory live log storage for console page
live_logs = []

# Terminal-style HTML page
TERMINAL_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>IP Logger Console</title>
  <style>
    body {
      background-color: #0b0b0b;
      
      background-image: url('https://i.pinimg.com/736x/06/1a/e6/061ae63996e176f871ad3b6f18e1a024.jpg');
      background-size: cover;
      background-repeat: no-repeat;
      background-position: center;
      
      color: #39FF14;
      font-family: 'Fira Mono', monospace;
      padding: 20px;
      margin: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
      box-sizing: border-box;
      transition: background-color 0.3s ease, background-image 0.3s ease;
    }
    h2 {
      margin-bottom: 15px;
      text-shadow: 0 0 8px #39FF14;
      font-weight: 600;
    }
    #log {
      width: 600px;
      height: 60vh;
      overflow-y: auto;
      white-space: pre-wrap;
      background: #111;
      border: 2px solid #39FF14;
      border-radius: 8px;
      padding: 15px;
      box-sizing: border-box;
      font-size: 1.1rem;
      line-height: 1.4;
      user-select: text;
      scrollbar-width: thin;
      scrollbar-color: #39FF14 transparent;
      margin-bottom: 30px;
    }
    /* Scrollbar for WebKit browsers */
    #log::-webkit-scrollbar {
      width: 8px;
    }
    #log::-webkit-scrollbar-track {
      background: transparent;
    }
    #log::-webkit-scrollbar-thumb {
      background-color: #39FF14;
      border-radius: 4px;
    }
    /* Labels and inputs */
    label {
      color: #39FF14;
      font-family: 'Fira Mono', monospace;
      margin-bottom: 5px;
      user-select: none;
    }
    input[type="color"] {
      cursor: pointer;
      background: #111;
      border: 1px solid #39FF14;
      border-radius: 4px;
      padding: 2px 5px;
      margin-bottom: 20px;
      display: block;
    }
  </style>
</head>
<body>
  <h2>Kuromi IP Logger Live Console</h2>

  <label for="bgColorPicker">Change Background Color:</label>
  <input type="color" id="bgColorPicker" value="#0b0b0b">

  <div id="log"></div>

  <script>
    const logDiv = document.getElementById("log");
    const bgColorPicker = document.getElementById('bgColorPicker');

    async function fetchLogs() {
      try {
        const res = await fetch("/live-logs");
        const data = await res.json();
        logDiv.textContent = data.join('\\n');
        logDiv.scrollTop = logDiv.scrollHeight;
      } catch(e) {
        console.error("Failed to fetch logs:", e);
      }
    }

    setInterval(fetchLogs, 1000);
    fetchLogs();

    bgColorPicker.addEventListener('input', e => {
      document.body.style.backgroundColor = e.target.value;
      // Remove background image when changing color
      document.body.style.backgroundImage = 'none';
    });
  </script>
</body>
</html>
"""

def send_discord_webhook(ip, ua, ts):
    if not DISCORD_WEBHOOK_URL:
        return
    content = f"New IP logged:\nIP: {ip}\nUser-Agent: {ua}\nTime: {datetime.datetime.fromtimestamp(ts)}"
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": content}, timeout=5)
    except Exception as e:
        print(f"Failed to send Discord webhook: {e}")

@app.route('/')
def log_ip():
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    timestamp = time.time()

    # Save to database
    new_log = IPLog(ip_address=ip_address, user_agent=user_agent, timestamp=timestamp)
    db.session.add(new_log)
    db.session.commit()

    # Append to live logs, keep max 100 lines to save memory
    log_line = f"{datetime.datetime.fromtimestamp(timestamp)} | IP: {ip_address} | UA: {user_agent}"
    live_logs.append(log_line)
    if len(live_logs) > 100:
        live_logs.pop(0)

    # Print to terminal console
    print(log_line)

    # Send Discord webhook in background thread
    threading.Thread(target=send_discord_webhook, args=(ip_address, user_agent, timestamp), daemon=True).start()

    return "ERROR 404 PAGE DOES NOT EXIST.\n"

@app.route('/live-logs')
def live_logs_api():
    return jsonify(live_logs)

@app.route('/logs')
def get_logs():
    logs = IPLog.query.order_by(IPLog.timestamp.desc()).limit(100).all()
    logs_list = [{
        "ip": log.ip_address,
        "user_agent": log.user_agent,
        "time": datetime.datetime.fromtimestamp(log.timestamp).isoformat()
    } for log in logs]
    return jsonify(logs_list)

@app.route('/export-logs/csv')
def export_csv():
    import csv
    from io import StringIO

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'IP Address', 'User Agent', 'Timestamp'])
    for log in IPLog.query.order_by(IPLog.timestamp).all():
        cw.writerow([log.id, log.ip_address, log.user_agent, datetime.datetime.fromtimestamp(log.timestamp)])
    output = si.getvalue()
    return app.response_class(output, mimetype='text/csv')

@app.route('/export-logs/json')
def export_json():
    logs = IPLog.query.order_by(IPLog.timestamp).all()
    logs_list = [{
        "id": log.id,
        "ip_address": log.ip_address,
        "user_agent": log.user_agent,
        "timestamp": datetime.datetime.fromtimestamp(log.timestamp).isoformat()
    } for log in logs]
    return jsonify(logs_list)

# Fixed function name here to avoid endpoint conflict
@app.route('/clear-logs', methods=['POST'])
def clear_logs_route():
    try:
        num_rows_deleted = IPLog.query.delete()
        db.session.commit()
        print(f"Cleared {num_rows_deleted} log entries.")
        return jsonify({"message": f"Cleared {num_rows_deleted} log entries."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/console')
def console_page():
    return render_template_string(TERMINAL_HTML)

def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:5000/console")

if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(host='0.0.0.0', port=5000)
