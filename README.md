<div align="center">
  <h1>🚀 Preddit</h1>
  <p><strong>A Super-Lightweight, Personalisable Reddit Mirror for the Minimalist Soul.</strong></p>
  
  <p>
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License MIT">
    <img src="https://img.shields.io/badge/Python-3.11+-green.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg" alt="Platform Pi">
  </p>
</div>

---

## 🌟 What is Preddit?

Preddit is not just another Reddit mirror. It's a **private, disk-first content aggregator** designed to run comfortably on hardware that others have long forgotten. 

While modern web apps demand gigabytes of RAM just to render a login page, Preddit lives on the edge, providing a distraction-free, lightning-fast reading experience directly from your self-hosted terminal or local network.

### Why Preddit?
- **Disk is Cheap, CPU is Expensive**: We index your favorite subreddits into a local SQLite DB, so you only scrape when you need to.
- **Ultra-Minimalist UI**: Server-side rendered HTML with zero JavaScript. Page weights are < 20KB.
- **Zero API, Zero Hassle**: No OAuth, no developer tokens, no tracking. Pure, honest scraping.
- **Hyper-Personalisable**: Set custom fetch intervals for every single subreddit. Want `/r/jobs` every 30 minutes but `/r/philosophy` once a day? Done.

---

## 🛠️ Pi-Powered: Built for the BCM2837

Preddit was born on a **Raspberry Pi 3 Model B (Rev 1.2)**. It is meticulously optimized for the following "weak" hardware:

- **CPU**: Broadcom BCM2837 (4 cores) @ 1.20 GHz
- **Architecture**: armv7l (32-bit)
- **RAM**: ~921 MiB Total
- **OS**: Raspbian GNU/Linux 13 (Trixie)

### Performance Metrics (On Pi 3)
| State | RAM Usage | CPU Usage |
|---|---|---|
| **Idle** | ~45 MiB | < 1% |
| **Fetching** | ~140 MiB | ~15% (Burst) |
| **Serving** | ~60 MiB | < 5% |

---

## 🚀 Getting Started

### 1. Installation
Preddit keeps dependencies to a bare minimum.

```bash
git clone https://github.com/yourusername/preddit.git
cd preddit
pip install -r requirements.txt
```

### 2. Configuration
Edit `config.yaml` to unleash your curiosity. The system supports custom fetch windows per subreddit:

```yaml
subreddits:
  - name: linux
    sort: new
    fetch_every: 3h
  - name: startups
    sort: hot
    fetch_every: 1h
```

### 3. Run Locally
```bash
python preddit.py
```
Open `http://localhost:9191` and breathe in the speed.

---

## 📦 Deployment (The "Villa" Method)

Preddit includes a built-in deployment script for remote Pi hosting. It sets up a `systemd` service so your mirror runs as a background daemon, surviving reboots and internet hiccups.

```bash
# Update deploy.py with your credentials
python deploy.py
```

---

## 🛡️ Privacy & SEO Friendly
- **SEO Optimized**: Headers and structure are designed to be indexed effectively if you choose to expose it via Cloudflare Tunnel.
- **Privacy First**: No cookies, no external fonts, no trackers. Your reading habits stay on your disk.

## 📄 License
This project is licensed under the [MIT License](LICENSE).

---
<div align="center">
  <p>Enlighten yourself. Stay lightweight.</p>
</div>
