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

NEWS_FEEDS = {
    "geral": "https://g1.globo.com/rss/g1/",
    "tecnologia": "https://g1.globo.com/rss/g1/tecnologia/",
    "ciencia": "https://g1.globo.com/rss/g1/ciencia-e-saude/",
    "mundo": "https://g1.globo.com/rss/g1/mundo/",
    "brasil": "https://g1.globo.com/rss/g1/brasil/"
}

@app.route('/api/news', methods=['GET'])
def get_news():
    category = request.args.get('category', 'geral').lower()
    limit = request.args.get('limit', default=10, type=int)

    feed_url = NEWS_FEEDS.get(category)
    
    if not feed_url:
        return jsonify({
            "success": False,
            "error": f"Category '{category}' don't finded. Avaliable categories: {list(NEWS_FEEDS.keys())}"
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
            "error": f"Falha ao carregar notícias: {str(e)}"
        }), 500

@app.route('/api/news/txt', methods=['GET'])
def get_news_txt():
    category = request.args.get('category', 'geral').lower()
    limit = request.args.get('limit', default=5, type=int)

    feed_url = NEWS_FEEDS.get(category, NEWS_FEEDS["geral"])
    feed = feedparser.parse(feed_url)

    output = f"=== NEWS: {category.upper()} ===\n\n"
    for idx, entry in enumerate(feed.entries[:limit], 1):
        output += f"[{idx}] {entry.get('title', '')}\n"
        output += f"    Data: {entry.get('published', 'N/A')}\n"
        output += f"    Link: {entry.get('link', '')}\n\n"

    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Online News server 📰",
        "endpoints": {
            "json": "/api/news?category=tecnologia&limit=5",
            "txt_puro": "/api/news/txt?category=tecnologia&limit=5"
        },
        "categorias": list(NEWS_FEEDS.keys())
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)