import feedparser
import re
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from database import init_db, save_article

# Inizializzazione del traduttore in lingua italiana
translator = GoogleTranslator(source='auto', target='it')

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

def translate_to_italian(text):
    """Traduce il testo in italiano gestendo eventuali blocchi o eccezioni."""
    if not text or not text.strip():
        return ""
    try:
        # Tronca a 500 caratteri per evitare timeout o blocchi nell'API di traduzione
        return translator.translate(text[:500])
    except Exception as e:
        print(f"⚠️ Errore durante la traduzione: {e}")
        return text

def extract_image_from_entry(entry):
    """Estrae l'immagine dall'entry del feed RSS o dall'HTML integrato."""
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
    """Genera hashtag dinamici in italiano basati sul contesto."""
    title_lower = title.lower()
    tags = set()
    
    if "Quantum" in category:
        tags.add("#CalcoloQuantistico")
        tags.add("#DeepTech")
    elif "Finanza" in category:
        tags.add("#FinanzaTech")
        tags.add("#Mercati")
    elif "Crypto" in category:
        tags.add("#Cripto")
        tags.add("#Web3")
        
    if "ai" in title_lower or "intelligenza" in title_lower or "intelligence" in title_lower:
        tags.add("#IA")
        tags.add("#Innovazione")
    if "nvidia" in title_lower:
        tags.add("#NVIDIA")
        tags.add("#Hardware")
    if "bitcoin" in title_lower or "btc" in title_lower:
        tags.add("#Bitcoin")
    if "ethereum" in title_lower or "eth" in title_lower:
        tags.add("#Ethereum")
        
    if len(tags) < 2:
        tags.add("#Futuro")
        tags.add("#Tecnologia")
        
    return " ".join(list(tags)[:3])

def create_engaging_description(entry, title_it):
    """Estrae e pulisce il riassunto reale dell'articolo prima di tradurlo."""
    raw_content = ""
    if hasattr(entry, 'summary') and entry.summary:
        raw_content = entry.summary
    elif hasattr(entry, 'content') and entry.content:
        raw_content = entry.content[0].value

    soup = BeautifulSoup(raw_content, 'html.parser')
    clean_text = soup.get_text().strip()
    clean_text = re.sub(r'\s+', ' ', clean_text)

    if not clean_text or len(clean_text) < 30:
        return f"Quali sono gli impatti e le prospettive future di {title_it}? Scopri tutti i dettagli."

    if len(clean_text) > 180:
        short_text = clean_text[:175].rsplit(' ', 1)[0]
        short_text = re.sub(r'[,;:\-–]$', '', short_text)
        clean_text = f"{short_text}..."

    return translate_to_italian(clean_text)

def run_pipeline():
    print("🔄 Aggiornamento notizie, traduzione in italiano e generazione hashtag...")
    init_db()
    
    total_saved = 0
    
    for category, urls in RSS_FEEDS.items():
        for url in urls:
            try:
                parsed_feed = feedparser.parse(url)
                for entry in parsed_feed.entries[:10]:
                    raw_title = entry.get('title', 'Titolo non disponibile')
                    link = entry.get('link', '#')
                    
                    # 1. Traduzione del Titolo
                    title_it = translate_to_italian(raw_title)
                    
                    # 2. Traduzione del Riassunto
                    description_it = create_engaging_description(entry, title_it)
                    
                    # 3. Generazione Hashtag
                    hashtags = generate_hashtags(raw_title, category)
                    
                    img_url = extract_image_from_entry(entry)
                    if not img_url:
                        img_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop&q=60"
                    
                    published = entry.get('published', 'Recente')
                    
                    save_article(
                        title=title_it,
                        url=link,
                        content=description_it,
                        image_url=img_url,
                        category=category,
                        hashtags=hashtags,
                        created_at=published
                    )
                    total_saved += 1
            except Exception as e:
                print(f"⚠️ Errore durante la lettura o traduzione del feed {url}: {e}")
                
    print(f"✅ Sincronizzazione completata: {total_saved} articoli elaborati in italiano.")

if __name__ == "__main__":
    run_pipeline()
