import time
from datetime import datetime
import random
import requests
import yaml
from bs4 import BeautifulSoup
from database import Database

class PredditFetcher:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.db = Database(self.config['storage']['db_path'])
        self.ua = self.config['fetcher']['user_agent']
        self.delay_min = self.config['fetcher']['request_delay_min']
        self.delay_max = self.config['fetcher']['request_delay_max']

    def fetch_thread_content(self, comment_url):
        if not comment_url: return None
        url = comment_url
        if not url.startswith('http'):
            url = f"https://old.reddit.com{url}"
        
        headers = {'User-Agent': self.ua}
        try:
            # We don't want to wait too long or fetch too much
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200: return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # The actual post content in old reddit
            content_div = soup.select_one('div.entry div.usertext-body div.md')
            if content_div:
                # Remove any images or media to keep it lightweight
                for img in content_div.find_all(['img', 'iframe', 'video']):
                    img.decompose()
                return str(content_div) # Keep HTML for formatting (links, bold, etc)
            return None
        except Exception as e:
            print(f"Error fetching thread content: {e}")
            return None

    def fetch_subreddit(self, name, sort="new", min_score=0):
        url = f"https://old.reddit.com/r/{name}/{sort}"
        headers = {'User-Agent': self.ua}
        
        print(f"Fetching /r/{name} ({sort})...")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            threads = []
            
            # Find all thread entries
            entries = soup.select('div.thing')
            for i, entry in enumerate(entries):
                try:
                    # Basic metadata extraction
                    reddit_id = entry.get('data-fullname')
                    title_elem = entry.select_one('a.title')
                    if not title_elem: continue
                    
                    title = title_elem.text
                    url = title_elem.get('href')
                    if url.startswith('/r/'):
                        url = "https://old.reddit.com" + url
                    
                    score_elem = entry.select_one('div.score.unvoted')
                    score = 0
                    if score_elem and score_elem.get('title'):
                        try: score = int(score_elem.get('title'))
                        except: pass
                    
                    # QUALITY GATE
                    if score < min_score:
                        continue
                    
                    author = entry.get('data-author', 'unknown')
                    
                    # Timestamp extraction
                    time_elem = entry.select_one('time.live-timestamp')
                    timestamp = int(time.time()) # fallback
                    
                    comment_elem = entry.select_one('a.comments')
                    comment_url = comment_elem.get('href') if comment_elem else ""

                    # Fetch content for top N threads to keep it lightweight
                    content = None
                    if i < 5: # Limit content fetching to top 5 threads
                        # CHECK: Do we already have this content?
                        if self.db.is_thread_fetched(reddit_id):
                            # print(f"Skipping content for {reddit_id} (already fetched)")
                            pass
                        else:
                            content = self.fetch_thread_content(comment_url)
                            if content:
                                time.sleep(random.uniform(1, 2)) # Be kind to Reddit

                    threads.append({
                        'reddit_id': reddit_id,
                        'subreddit': name,
                        'title': title,
                        'url': url,
                        'score': score,
                        'author': author,
                        'timestamp': timestamp,
                        'comment_url': comment_url,
                        'content': content
                    })
                except Exception as e:
                    print(f"Error parsing entry: {e}")
            
            saved = self.db.save_threads(threads)
            self.db.log_fetch(name, "success", saved)
            print(f"Successfully saved {saved} new threads for /r/{name}")
            return saved
            
        except Exception as e:
            print(f"Failed to fetch /r/{name}: {e}")
            self.db.log_fetch(name, "error", 0, str(e))
            return 0

    def reload_config(self):
        with open("config.yaml", 'r') as f:
            self.config = yaml.safe_load(f)
        self.ua = self.config['fetcher']['user_agent']
        self.delay_min = self.config['fetcher']['request_delay_min']
        self.delay_max = self.config['fetcher']['request_delay_max']

    def parse_interval(self, interval_str):
        if not interval_str: return 3600 # Default 1h
        try:
            unit = interval_str[-1].lower()
            value = int(interval_str[:-1])
            if unit == 'm': return value * 60
            if unit == 'h': return value * 3600
            if unit == 'd': return value * 86400
            return value
        except:
            return 3600

    def run_cycle(self):
        self.reload_config()
        now = datetime.now()
        print(f"\n--- Checking Subreddits: {time.ctime()} ---")
        
        for sub in self.config['subreddits']:
            name = sub['name']
            interval_str = sub.get('fetch_every', '1h')
            interval_sec = self.parse_interval(interval_str)
            
            last_fetch = self.db.get_last_fetch_time(name)
            
            # Check if it's time to fetch
            if last_fetch:
                elapsed = (now - last_fetch).total_seconds()
                if elapsed < interval_sec:
                    # print(f"Skipping /r/{name} (Last fetch: {last_fetch}, Next in {int(interval_sec - elapsed)}s)")
                    continue

            self.fetch_subreddit(name, sub.get('sort', 'new'), sub.get('min_score', 0))
            
            # Rate limiting jitter between actual fetches
            sleep_time = random.uniform(self.delay_min, self.delay_max)
            time.sleep(sleep_time)
        
        # Cleanup (once per cycle is fine)
        removed = self.db.cleanup_old_threads(self.config['storage']['retention_days'])
        if removed:
            print(f"Cleaned up {removed} expired threads.")

    def run_forever(self):
        # Shorter sleep in main loop to check intervals frequently
        while True:
            self.run_cycle()
            # print("Cycle check complete. Waiting 60s...")
            time.sleep(60) 

if __name__ == "__main__":
    fetcher = PredditFetcher()
    fetcher.run_cycle() # Run once for testing
