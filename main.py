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

def create_engaging_description(entry, title):
    """
    Estrae il testo reale dall'articolo RSS, rimuove l'HTML e crea 
    un riassunto incisivo e dinamico.
    """
    raw_content = ""
    
    # Cerca il testo nel summary o nel content dell'RSS
    if hasattr(entry, 'summary') and entry.summary:
        raw_content = entry.summary
    elif hasattr(entry, 'content') and entry.content:
        raw_content = entry.content[0].value

    # Pulizia del tag HTML
    soup = BeautifulSoup(raw_content, 'html.parser')
    clean_text = soup.get_text().strip()
    
    # Rimuove spazi doppi o newlines
    clean_text = re.sub(r'\s+', ' ', clean_text)

    # Se il feed non ha testo o è troppo breve, usa il titolo come spunto
    if not clean_text or len(clean_text) < 30:
        return f"Cosa c'è dietro gli ultimi sviluppi su {title}? Scopri i punti chiave e l'impatto sul settore."

    # Se il testo è lungo, lo taglia in modo pulito alla fine di una parola (max 180 caratteri)
    if len(clean_text) > 180:
        short_text = clean_text[:175].rsplit(' ', 1)[0]
        # Pulisce eventuale punteggiatura rimasta prima dei puntini
        short_text = re.sub(r'[,;:\-–]$', '', short_text)
        return f"{short_text}..."

    return clean_text

def run_pipeline():
    print("🔄 Aggiornamento notizie, hashtag e riassunti dinamici...")
    init_db()
    
    total_saved = 0
    
    for category, urls in RSS_FEEDS.items():
        for url in urls:
            try:
                parsed_feed = feedparser.parse(url)
                for entry in parsed_feed.entries[:15]:
                    title = entry.get('title', 'Titolo non disponibile')
                    link = entry.get('link', '#')
                    
                    # Genera il riassunto reale ed accattivante
                    description = create_engaging_description(entry, title)
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
