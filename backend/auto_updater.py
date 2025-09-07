import subprocess
import requests
import json
import os
import time
import threading
from datetime import datetime

UPDATE_INTERVAL = 300  # 5 minutes

SYNONYM_DB_PATH = "data/synonym_db.json"

API_SOURCES = [
    "https://raw.githubusercontent.com/dolph/dictionary/master/synonyms.json",
]

def update_pip_libraries():
    print(f"[{datetime.now()}] 🔧 Updating libraries...")
    try:
        subprocess.check_call(["pip", "install", "--upgrade", "-r", "requirements.txt"])
        print("✅ Libraries updated.")
    except Exception as e:
        print(f"❌ Failed: {e}")

def fetch_live_synonyms():
    print(f"[{datetime.now()}] 🌐 Fetching synonyms...")
    merged_db = {}
    for url in API_SOURCES:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for word, synonyms in data.items():
                    clean_word = word.lower().strip()
                    if clean_word not in merged_db:
                        merged_db[clean_word] = []
                    for syn in synonyms:
                        if syn not in merged_db[clean_word]:
                            merged_db[clean_word].append(syn)
                print(f"✅ Loaded {len(data)} from {url}")
        except Exception as e:
            print(f"⚠️ Error: {e}")
    os.makedirs("data", exist_ok=True)
    with open(SYNONYM_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(merged_db, f, indent=2, ensure_ascii=False)
    print(f"💾 DB saved with {len(merged_db)} entries.")

def auto_update_loop():
    while True:
        try:
            update_pip_libraries()
            fetch_live_synonyms()
        except Exception as e:
            print(f"🔄 Update failed: {e}")
        print(f"💤 Sleeping {UPDATE_INTERVAL}s...")
        time.sleep(UPDATE_INTERVAL)

def start_auto_updater():
    updater_thread = threading.Thread(target=auto_update_loop, daemon=True)
    updater_thread.start()
    print("🚀 Auto-updater started (every 5 min).")