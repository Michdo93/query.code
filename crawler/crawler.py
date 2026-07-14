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

# --- KONFIGURATION AUS DATEI LADEN ---
def load_sources(file_path="sources.txt"):
    if not os.path.exists(file_path):
        print(f"Fehler: Datei '{file_path}' wurde nicht gefunden!")
        # Fallback, falls die Datei fehlt
        return ["https://docs.python.org/3/tutorial/index.html"]
    
    with open(file_path, "r", encoding="utf-8") as f:
        # Zeilen einlesen, Leerzeichen entfernen und leere Zeilen ignorieren
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return urls

START_URLS = load_sources()

# Erlaubte Domains aus allen Start-URLs extrahieren (z.B. "www.w3schools.com" oder "github.com")
# Wir nutzen eine Liste, die wir mit .endswith() prüfen, um auch Subdomains (wie docs.python.org) zu erlauben.
ALLOWED_DOMAINS = [urlparse(url).netloc for url in START_URLS]

MAX_PAGES = 100  # Höheres Limit, da wir jetzt viele Quellen haben
DELAY = 1.0      # 1 Sekunde Pause zwischen Anfragen, um die Server nicht zu überlasten

visited_urls = set()
urls_to_visit = list(START_URLS)  # Alle Start-URLs in die To-Do-Liste packen

def is_allowed_domain(url):
    """Prüft, ob die Domain der URL auf unserer Whitelist steht oder eine Subdomain davon ist."""
    domain = urlparse(url).netloc
    for allowed in ALLOWED_DOMAINS:
        # Erlaubt die Domain selbst oder Subdomains (z.B. docs.github.com, wenn github.com erlaubt ist)
        if domain == allowed or domain.endswith("." + allowed):
            return True
    return False

def extract_links(soup, base_url):
    links = []
    for anchor in soup.find_all('a', href=True):
        href = anchor['href']
        absolute_url = urljoin(base_url, href)
        absolute_url = absolute_url.split('#')[0] # Anker-Tags entfernen
        
        # Nur Links erlauben, die auf einer der Whitelist-Domains liegen und neu sind
        if is_allowed_domain(absolute_url) and absolute_url not in visited_urls:
            links.append(absolute_url)
    return links

def crawl_and_index(url: str):
    print(f"\n[{len(visited_urls) + 1}/{MAX_PAGES}] Crawle: {url}")
    
    try:
        headers = {'User-Agent': 'QueryCodeBot/1.0 (Developer Search Engine Education Project)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        # UTF-8 Zeichensatz-Korrektur (Fix für kryptische Zeichen)
        response.encoding = response.apparent_encoding
        
        if response.status_code != 200:
            print(f"-> Fehler beim Laden ({response.status_code})")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Unnötigen Kram entfernen (Navigation, Footer, Scripts)
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
        
        return extract_links(soup, url)

    except Exception as e:
        print(f"-> Fehler bei {url}: {e}")
        return []

# --- CRAWLER LOOP ---
if __name__ == "__main__":
    print(f"Geladene Start-Quellen: {len(START_URLS)}")
    print(f"Erlaubte Domains: {ALLOWED_DOMAINS}")
    
    while urls_to_visit and len(visited_urls) < MAX_PAGES:
        current_url = urls_to_visit.pop(0)
        
        if current_url in visited_urls:
            continue
            
        visited_urls.add(current_url)
        
        new_links = crawl_and_index(current_url)
        
        for link in new_links:
            if link not in urls_to_visit and link not in visited_urls:
                urls_to_visit.append(link)
                
        time.sleep(DELAY)

    print(f"\nFertig! Insgesamt {len(visited_urls)} Seiten aus verschiedenen Quellen indexiert.")