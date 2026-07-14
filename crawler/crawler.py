import os
import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dotenv import load_dotenv

# Umgebungsvariablen laden
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Fehler: SUPABASE_URL oder SUPABASE_KEY fehlt!")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Konfiguration für den intelligenten Crawler
START_URL = "https://docs.python.org/3/tutorial/index.html"
ALLOWED_DOMAIN = urlparse(START_URL).netloc  # Z.B. "docs.python.org"
MAX_PAGES = 30  # Sicherheitshalber erst mal auf 30 Seiten limitieren
DELAY = 1.0     # 1 Sekunde Pause zwischen den Anfragen, um Server zu schonen (Politeness)

visited_urls = set()
urls_to_visit = [START_URL]

def get_domain(url):
    return urlparse(url).netloc

def extract_links(soup, base_url):
    links = []
    for anchor in soup.find_all('a', href=True):
        href = anchor['href']
        # Relative Links (z.B. "intro.html") in absolute Links ("https://.../intro.html") umwandeln
        absolute_url = urljoin(base_url, href)
        # Fragmente wie "#überschrift-1" abschneiden
        absolute_url = absolute_url.split('#')[0]
        
        # Nur Links erlauben, die auf derselben Domain liegen und noch nicht besucht wurden
        if get_domain(absolute_url) == ALLOWED_DOMAIN and absolute_url not in visited_urls:
            links.append(absolute_url)
    return links

def crawl_and_index(url: str):
    print(f"\n[{len(visited_urls) + 1}/{MAX_PAGES}] Crawle: {url}")
    
    try:
        headers = {'User-Agent': 'QueryCodeBot/1.0 (Developer Search Engine Education Project)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"-> Fehler beim Laden ({response.status_code})")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Unnötigen Kram entfernen
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()

        title = soup.title.string.strip() if soup.title else "Kein Titel"
        
        # Beschreibung generieren
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc.get('content').strip()
        else:
            plain_text = soup.get_text()
            description = " ".join(plain_text.split())[:180] + "..."

        content = " ".join(soup.get_text().split())

        # In Supabase speichern
        page_data = {
            "url": url,
            "title": title,
            "content": content,
            "description": description
        }
        
        supabase.table("webpages").upsert(page_data, on_conflict="url").execute()
        print(f"-> Erfolgreich indexiert: '{title}'")
        
        # Neue Links von dieser Seite extrahieren
        return extract_links(soup, url)

    except Exception as e:
        print(f"-> Fehler bei {url}: {e}")
        return []

# --- CRAWLER LOOP ---
if __name__ == "__main__":
    print(f"Starte rekursiven Crawler für Domain: {ALLOWED_DOMAIN}")
    
    while urls_to_visit and len(visited_urls) < MAX_PAGES:
        current_url = urls_to_visit.pop(0)
        
        if current_url in visited_urls:
            continue
            
        visited_urls.add(current_url)
        
        # Seite crawlen und neue Links erhalten
        new_links = crawl_and_index(current_url)
        
        # Neue Links an unsere To-Do-Liste anhängen
        for link in new_links:
            if link not in urls_to_visit and link not in visited_urls:
                urls_to_visit.append(link)
                
        # Politeness Delay einhalten
        time.sleep(DELAY)

    print(f"\nFertig! Insgesamt {len(visited_urls)} Seiten indexiert.")