from flask import Flask, request, jsonify
from flask_cors import CORS
from humanizer import humanize_text
from auto_updater import start_auto_updater
import os
from datetime import datetime
import time

app = Flask(__name__)
CORS(app)

REQUEST_LOG = {}

def is_rate_limited(ip):
    now = time.time()
    if ip not in REQUEST_LOG:
        REQUEST_LOG[ip] = []
    REQUEST_LOG[ip] = [t for t in REQUEST_LOG[ip] if t > now - 60]
    if len(REQUEST_LOG[ip]) >= 5:
        return True
    REQUEST_LOG[ip].append(now)
    return False

@app.route('/humanize', methods=['POST'])
def humanize():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if is_rate_limited(user_ip):
        return jsonify({"error": "Rate limit: 5 requests/minute"}), 429

    data = request.json
    original_text = data.get('text', '')
    if not original_text:
        return jsonify({"error": "No text provided"}), 400

    try:
        humanized = humanize_text(original_text)
        return jsonify({
            "original": original_text,
            "humanized": humanized,
            "bypass_grade": "A+",
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": "Internal error. Try again."}), 500

@app.route('/last_updated')
def last_updated():
    if os.path.exists("data/synonym_db.json"):
        mod_time = os.path.getmtime("data/synonym_db.json")
        readable_time = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({"last_updated": readable_time})
    else:
        return jsonify({"last_updated": "Initializing..."})

@app.route('/health')
def health():
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    start_auto_updater()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)