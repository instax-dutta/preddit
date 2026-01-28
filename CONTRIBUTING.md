# Contributing to Preddit

First off, thank you for considering contributing to Preddit! It's people like you who make Preddit such a cool tool for the self-hosted community.

## Our Philosophy
- **Minimalism**: If it can be done with the standard library or a lightweight package, do it.
- **Performance**: We optimize for Raspberry Pi 3 class hardware. Every byte and clock cycle counts.
- **Privacy**: No tracking, no external APIs, just clean scraping.

## How Can I Contribute?

### Reporting Bugs
- Check the issues page to see if it's already reported.
- Provide a clear description and steps to reproduce.

### Suggesting Enhancements
- We love new ideas! Especially ones that improve the "personalisable" aspect of the reader.
- Keep in mind our low-power target.

### Pull Requests
1. Fork the repo and create your branch from `main`.
2. Ensure your code follows the existing style (clean, procedural Python).
3. Test your changes on a low-resource device if possible.
4. Update the README or documentation if necessary.

## Development Setup
```bash
git clone https://github.com/instax-dutta/preddit.git
cd preddit
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python preddit.py
```

Thank you for making Preddit better!
