# Kuromi IP Logger

A simple Flask-based IP logger with real-time live console, database storage, and optional Discord webhook notifications.
please read the how to use

## Features

- Logs visitor IP addresses and User-Agent strings.
- Stores logs in a lightweight SQLite database.
- Real-time terminal-style live console with auto-updating logs.
- Customizable background color and background image for the console.
- Export logs as CSV or JSON.
- Clear logs via API endpoint.
- Optional Discord webhook integration for new IP notifications.
- Lightweight and easy to deploy locally or on a server.

## Requirements

- Python 3.7 or higher
- Flask
- Flask_SQLAlchemy
- Flask_CORS
- requests




API Endpoints
GET /live-logs — Returns a JSON array of recent live logs for real-time display.
GET /logs — Returns the latest 100 stored logs in JSON format.
GET /export-logs/csv — Downloads all stored logs as a CSV file.
GET /export-logs/json — Downloads all stored logs as JSON.
POST /clear-logs — Clears all stored logs from the database.

Customization
Change the background image URL or default background color by editing the inline CSS in the TERMINAL_HTML variable inside app.py.
Use the color picker in the console to dynamically change the background color.
(Optional) Add your Discord webhook URL to receive notifications when new IPs are logged.

Notes
This app logs IP addresses and User-Agent headers of visitors. Use responsibly and comply with privacy laws.
The SQLite database iplogs.db is created automatically in the app directory.
The live console displays the latest 100 logs and auto-refreshes every second.

License
This project is licensed under the MIT License. See the LICENSE file for details.
This project is intended solely for educational and testing purposes. It demonstrates how to log IP addresses and user-agent information using Flask and how to display live logs.

Important:

Always obtain explicit consent from users before collecting or storing any personal data.
Use this tool responsibly and ethically, respecting privacy laws such as GDPR, CCPA, and others applicable in your jurisdiction.
Unauthorized logging or tracking of individuals without their knowledge is illegal and unethical.
By using this project, you agree to comply with all relevant laws and regulations and to respect the privacy and rights of others.
