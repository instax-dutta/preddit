from flask import Flask, render_template, abort
from database import Database
import yaml

app = Flask(__name__)

# Load config for subreddit list
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    
db = Database(config['storage']['db_path'])

@app.route('/')
def index():
    subreddits = config['subreddits']
    # Get latest 10 threads across all subreddits for context
    recent_threads = db.get_threads(limit=10)
    return render_template('index.html', subreddits=subreddits, recent=recent_threads)

@app.route('/r/<name>')
def subreddit_view(name):
    # Verify subreddit exists in config
    sub_config = next((s for s in config['subreddits'] if s['name'].lower() == name.lower()), None)
    if not sub_config:
        abort(404)
        
    threads = db.get_threads(subreddit=name, limit=50)
    return render_template('subreddit.html', name=name, threads=threads)

if __name__ == '__main__':
    host = config['server'].get('host', '0.0.0.0')
    port = config['server'].get('port', 8080)
    app.run(host=host, port=port, debug=False)
