import sys
import subprocess

# Auto-instalação de dependências
required_packages = ['flask', 'flask_cors', 'feedparser', 'requests']

def install_missing_packages():
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Library '{package}' don't finded. Installing automatically...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install_missing_packages()

from flask import Flask, jsonify, request
from flask_cors import CORS
import feedparser

app = Flask(__name__)
CORS(app)

SPORTS_FEEDS = {
    # Globo feeds (yes, im brazillian)
    "futebol": "https://ge.globo.com/rss/futebol/",
    "brasileirao": "https://ge.globo.com/rss/futebol/brasileirao-serie-a/",
    "futebol-internacional": "https://ge.globo.com/rss/futebol/futebol-internacional/",
    "futebol-espanhol": "https://ge.globo.com/rss/futebol/futebol-espanhol/",
    "basquete": "https://ge.globo.com/rss/basquete/",
    "automobilismo": "https://ge.globo.com/rss/motor/"
}

@app.route('/api/sports', methods=['GET'])
def get_sports():
    category = request.args.get('category', 'futebol').lower()
    limit = request.args.get('limit', default=10, type=int)

    feed_url = SPORTS_FEEDS.get(category)
    
    if not feed_url:
        return jsonify({
            "success": False,
            "error": f"Category '{category}' don't finded. Avaliable categories: {list(SPORTS_FEEDS.keys())}"
        }), 400

    try:
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries[:limit]:
            articles.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", entry.get("description", "")),
                "link": entry.get("link", ""),
                "published": entry.get("published", entry.get("updated", ""))
            })

        return jsonify({
            "success": True,
            "category": category,
            "total": len(articles),
            "articles": articles
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Fail to load sportive data: {str(e)}"
        }), 500

@app.route('/api/sports/txt', methods=['GET'])
def get_sports_txt():
    category = request.args.get('category', 'futebol').lower()
    limit = request.args.get('limit', default=5, type=int)

    feed_url = SPORTS_FEEDS.get(category, SPORTS_FEEDS["futebol"])
    feed = feedparser.parse(feed_url)

    output = f"=== ESPORTES: {category.upper()} ===\n\n"
    for idx, entry in enumerate(feed.entries[:limit], 1):
        output += f"[{idx}] {entry.get('title', '')}\n"
        output += f"    Data: {entry.get('published', 'N/A')}\n"
        output += f"    Link: {entry.get('link', '')}\n\n"

    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Sports server ⚽",
        "endpoints": {
            "json": "/api/sports?category=brasileirao&limit=5",
            "txt_puro": "/api/sports/txt?category=futebol&limit=5"
        },
        "categorias": list(SPORTS_FEEDS.keys())
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3003, debug=True)
