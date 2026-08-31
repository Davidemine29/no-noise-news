import feedparser
import re
from bs4 import BeautifulSoup
from database import init_db, save_article

RSS_FEEDS = {
    "Quantum & AI": [
        "https://www.technologyreview.com/feed/",
        "https://feeds.arstechnica.com/arstechnica/index"
    ],
    "Finanza Tech": [
        "https://www.ft.com/technology?format=rss",
    ],
    "Crypto & Web3": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://decrypt.co/feed"
    ]
}

def extract_image_from_entry(entry):
    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if 'url' in media:
                return media['url']
                
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if 'type' in enc and 'image' in enc['type']:
                return enc['href']
                
    content_html = ""
    if hasattr(entry, 'summary'):
        content_html = entry.summary
    elif hasattr(entry, 'content'):
        content_html = entry.content[0].value
        
    if content_html:
        soup = BeautifulSoup(content_html, 'html.parser')
        img_tag = soup.find('img')
        if img_tag and img_tag.get('src'):
            return img_tag['src']
            
    return None

def generate_hashtags(title, category):
    title_lower = title.lower()
    tags = set()
    
    if "Quantum" in category:
        tags.add("#QuantumComputing")
        tags.add("#DeepTech")
    elif "Finanza" in category:
        tags.add("#TechFinance")
        tags.add("#MarketNews")
    elif "Crypto" in category:
        tags.add("#Crypto")
        tags.add("#Web3")
        
    if "ai" in title_lower or "artificial intelligence" in title_lower:
        tags.add("#AI")
        tags.add("#TechTrends")
    if "nvidia" in title_lower:
        tags.add("#NVIDIA")
        tags.add("#Hardware")
    if "bitcoin" in title_lower or "btc" in title_lower:
        tags.add("#Bitcoin")
    if "ethereum" in title_lower or "eth" in title_lower:
        tags.add("#Ethereum")
    if "sec" in title_lower or "regulation" in title_lower:
        tags.add("#Regulation")
        
    if len(tags) < 2:
        tags.add("#Innovation")
        tags.add("#GlobalTech")
        
    return " ".join(list(tags)[:3])

def create_engaging_description(raw_html):
    if not raw_html:
        return "Tutti i dettagli e le implicazioni di questa svolta nell'articolo completo."
        
    soup = BeautifulSoup(raw_html, 'html.parser')
    text = soup.get_text().strip()
    
    if not text:
        return "Scopri i retroscena e l'impatto sul settore nell'analisi completa."
        
    if len(text) > 200:
        text = text[:197].rsplit(' ', 1)[0] + "..."
        
    return f"{text} Leggi l'analisi completa per scoprire tutti i dettagli."

def run_pipeline():
    print("🔄 Aggiornamento notizie, hashtag e descrizioni accattivanti...")
    init_db()
    
    total_saved = 0
    
    for category, urls in RSS_FEEDS.items():
        for url in urls:
            try:
                parsed_feed = feedparser.parse(url)
                # Legge fino a 15 notizie per ciascun feed invece di 5
                for entry in parsed_feed.entries[:15]:
                    title = entry.get('title', 'Titolo non disponibile')
                    link = entry.get('link', '#')
                    raw_summary = entry.get('summary', entry.get('description', ''))
                    
                    description = create_engaging_description(raw_summary)
                    hashtags = generate_hashtags(title, category)
                    
                    img_url = extract_image_from_entry(entry)
                    if not img_url:
                        img_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop&q=60"
                    
                    published = entry.get('published', 'Recente')
                    
                    save_article(
                        title=title,
                        url=link,
                        content=description,
                        image_url=img_url,
                        category=category,
                        hashtags=hashtags,
                        created_at=published
                    )
                    total_saved += 1
            except Exception as e:
                print(f"⚠️ Errore lettura feed {url}: {e}")
                
    print(f"✅ Sincronizzazione completata: {total_saved} articoli elaborati.")

if __name__ == "__main__":
    run_pipeline()
