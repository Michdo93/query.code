# 🔍 Query.code

**Query.code** ist eine schlanke, performante und komplett kostenlose Open-Source-Suchmaschine, die speziell für Entwickler-Wissen (Dokumentationen, Foren, Tutorials) optimiert ist. 

Das gesamte Projekt ist so aufgebaut, dass es im **Free-Tier** bekannter Cloud-Anbieter läuft und dient als anschauliches Lernprojekt für moderne Webtechnologien.

## 🚀 Live-Demo
Das Frontend ist über GitHub Pages öffentlich erreichbar:
👉 **[DEINE-LIVE-URL-HIER-EINFÜGEN]** *(z. B. https://dein-username.github.io/query-code/frontend/)*

---

## 🛠️ Die Architektur

Das Projekt basiert auf einer minimalen und effizienten Serverless-Struktur:

* **Frontend:** Gehostet auf **GitHub Pages** (HTML5, Tailwind CSS, Vanilla JS). Es kommuniziert direkt über die Supabase JavaScript-Bibliothek mit der Datenbank.
* **Datenbank & API:** **Supabase** (PostgreSQL). Nutzt die native Postgres-Volltextsuche (`tsvector` & `tsquery`) für blitzschnelle Suchergebnisse mit Relevanz-Ranking, geschützt durch Row-Level-Security (RLS).
* **Crawler / Indexer:** Ein **Python**-Skript (`BeautifulSoup4`, `Requests`), das rekursiv Webseiten liest, bereinigt und über den sicheren `service_role`-Schlüssel direkt in die Datenbank einspeist.

---

## 💻 Lokales Setup (Selbst ausprobieren)

Du kannst dieses Projekt in weniger als 10 Minuten für dich selbst nachbauen.

### 1. Supabase vorbereiten
1. Erstelle ein kostenloses Projekt auf [supabase.com](https://supabase.com).
2. Gehe in den **SQL Editor** und führe das Skript aus `supabase/schema.sql` aus. Das erstellt die Tabellen, Such-Indizes und Sicherheitsregeln (RLS).

### 2. Crawler einrichten (Python)
1. Navigiere in den Crawler-Ordner:
   ```bash
   cd crawler
   ```

2. Installiere die Abhängigkeiten:
    ```bash
    pip install -r requirements.txt
    ```


3. Erstelle eine `.env` Datei im Ordner `crawler/` mit deinen Supabase-Zugangsdaten:
    ```env
    SUPABASE_URL=DEINE_SUPABASE_PROJEKT_URL
    SUPABASE_KEY=DEIN_SERVICE_ROLE_SECRET_KEY
    ```


4. Starte den Crawler, um deine Datenbank mit Inhalten zu füttern:
    ```bash
    python crawler.py
    ```

### 3. Frontend anpassen & starten

1. Öffne `frontend/app.js` und trage oben deine `SUPABASE_URL` und deinen **öffentlichen** `SUPABASE_ANON_KEY` ein.
2. Starte einen lokalen Server, um CORS-Fehler im Browser zu vermeiden:
```bash
# Im Ordner /frontend
python -m http.server 8000
```


3. Rufe `http://localhost:8000` auf und teste deine eigene Suchmaschine!

---

## 🤝 Mitmachen / Contributing

Du möchtest neue Features hinzufügen, den Crawler optimieren oder das Design verschönern?

1. Forke das Projekt.
2. Erstelle einen Feature-Branch (`git checkout -b feature/cooles-neues-feature`).
3. Committe deine Änderungen (`git commit -m 'feat: füge cooles Feature hinzu'`).
4. Pushe den Branch (`git push origin feature/cooles-neues-feature`).
5. Erstelle einen Pull Request!

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert – siehe die [LICENSE](https://github.com/Michdo93/query.code/LICENSE)-Datei für Details.