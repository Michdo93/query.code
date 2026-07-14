import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Umgebungsvariablen aus der .env-Datei laden
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Fehler: SUPABASE_URL oder SUPABASE_KEY nicht in .env gefunden!")
    exit(1)

# Supabase-Client initialisieren
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def crawl_and_index(url: str):
    print(f"Crawle Seite: {url}...")
    
    try:
        # 2. HTML-Inhalt der Webseite herunterladen
        headers = {'User-Agent': 'QueryCodeBot/1.0 (Open Source Search Engine)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Fehler beim Laden der Seite ({response.status_code})")
            return

        # 3. HTML parsen mit BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Unnötige Elemente entfernen (Scripte, Styles, Navigation etc.)
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Titel auslesen (Standardmäßig das <title>-Tag)
        title = soup.title.string.strip() if soup.title else "Kein Titel"
        
        # Eine kurze Beschreibung generieren (Meta-Description oder die ersten 200 Zeichen)
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc.get('content').strip()
        else:
            # Fallback: Die ersten 200 Zeichen des Textes nehmen
            plain_text = soup.get_text()
            description = " ".join(plain_text.split())[:200] + "..."

        # Den gesamten bereinigten Textinhalt für die Volltextsuche extrahieren
        content = soup.get_text()
        content = " ".join(content.split()) # Entfernt überflüssige Leerzeichen/Absätze

        # 4. Daten für Supabase vorbereiten
        page_data = {
            "url": url,
            "title": title,
            "content": content,
            "description": description
        }

        # 5. Daten in Supabase hochladen (Upsert aktualisiert die Seite, falls sie schon existiert)
        print("Speichere Daten in der Supabase-Datenbank...")
        result = supabase.table("webpages").upsert(page_data, on_conflict="url").execute()
        
        print(f"Erfolgreich indiziert: '{title}'")

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

# --- TEST-LAUF ---
if __name__ == "__main__":
    # Wir testen den Crawler mit einer bekannten Programmierer-Ressource:
    # Der Python-Dokumentation für Einsteiger
    test_url = "https://docs.python.org/3/tutorial/index.html"
    crawl_and_index(test_url)