import threading
import time
from fetcher import PredditFetcher
from server import app
import yaml

def start_fetcher():
    print("[Orchestrator] Starting Fetcher...")
    fetcher = PredditFetcher()
    # Initial fetch on start
    fetcher.run_cycle()
    # Then run periodic loop
    fetcher.run_forever()

def start_server():
    print("[Orchestrator] Starting Web Server...")
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    host = config['server'].get('host', '0.0.0.0')
    port = config['server'].get('port', 8080)
    app.run(host=host, port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Note: On a Pi with very low RAM, running both in one process via threads
    # is fine as they are both IO bound. However, for maximum isolation,
    # separate systemd units are recommended.
    
    fetch_thread = threading.Thread(target=start_fetcher, daemon=True)
    fetch_thread.start()
    
    # Run server in main thread
    start_server()
