import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
from database import get_paged_articles, get_all_articles
from main import run_pipeline

app = Flask(__name__)

def format_article(art):
    art_id, title, url, content, image_url, category, hashtags, created_at = art
    return {
        "id": art_id,
        "title": title,
        "url": url,
        "content": content,
        "image_url": image_url,
        "category": category,
        "hashtags": hashtags,
        "created_at": created_at
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/articles")
def api_articles():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 5))
    
    raw_articles, total_count = get_paged_articles(page=page, limit=limit)
    formatted_batch = [format_article(art) for art in raw_articles]
    
    has_more = (page * limit) < total_count
    
    return jsonify({
        "articles": formatted_batch,
        "has_more": has_more,
        "total": total_count
    })

@app.route("/refresh", methods=["GET", "POST"])
def refresh():
    run_pipeline()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify({"status": "ok"})
    return redirect(url_for("home"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Avvio Dashboard su porta {port}")
    app.run(host="0.0.0.0", port=port)
