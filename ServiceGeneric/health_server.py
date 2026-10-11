import sys
import subprocess

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

HEALTH_FEEDS = {
    "geral": "https://g1.globo.com/rss/g1/ciencia-e-saude/",
    "bem-estar": "https://g1.globo.com/rss/g1/bemestar/",
    "medicina": "https://g1.globo.com/rss/g1/ciencia-e-saude/"
}

@app.route('/api/health', methods=['GET'])
def get_health():
    category = request.args.get('category', 'geral').lower()
    limit = request.args.get('limit', default=10, type=int)

    feed_url = HEALTH_FEEDS.get(category)
    
    if not feed_url:
        return jsonify({
            "success": False,
            "error": f"Category '{category}' don't finded. Avaliable categories: {list(HEALTH_FEEDS.keys())}"
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
            "error": f"Fail to load health data: {str(e)}"
        }), 500

@app.route('/api/health/txt', methods=['GET'])
def get_health_txt():
    category = request.args.get('category', 'geral').lower()
    limit = request.args.get('limit', default=5, type=int)

    feed_url = HEALTH_FEEDS.get(category, HEALTH_FEEDS["geral"])
    feed = feedparser.parse(feed_url)

    output = f"=== HEALTH: {category.upper()} ===\n\n"
    for idx, entry in enumerate(feed.entries[:limit], 1):
        output += f"[{idx}] {entry.get('title', '')}\n"
        output += f"    Data: {entry.get('published', 'N/A')}\n"
        output += f"    Link: {entry.get('link', '')}\n\n"

    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Health server 🩺",
        "endpoints": {
            "json": "/api/health?category=bem-estar&limit=5",
            "txt_puro": "/api/health/txt?category=geral&limit=5"
        },
        "categorias": list(HEALTH_FEEDS.keys())
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3004, debug=True)
