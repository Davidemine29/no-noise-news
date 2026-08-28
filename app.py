import os
from flask import Flask, render_template, redirect, url_for
from database import get_all_articles
from main import run_pipeline

app = Flask(__name__)

@app.route("/")
def home():
    raw_articles = get_all_articles()
    articles = []
    
    for art in raw_articles:
        art_id, title, url, content, image_url, category, hashtags, created_at = art
        articles.append({
            "id": art_id,
            "title": title,
            "url": url,
            "content": content,
            "image_url": image_url,
            "category": category,
            "hashtags": hashtags,
            "created_at": created_at
        })
        
    return render_template("index.html", articles=articles)

@app.route("/refresh", methods=["GET", "POST"])
def refresh():
    run_pipeline()
    return redirect(url_for("home"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Avvio Dashboard su port {port}")
    app.run(host="0.0.0.0", port=port)