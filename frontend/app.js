// 1. Supabase Client initialisieren
const SUPABASE_URL = "https://bwsagojtisfakjkdeyvi.supabase.co";
const SUPABASE_ANON_KEY = "sb_publishable_o8OglJjW0V2M9AP8Ck-atA_r9dQZrNf";

// Geändert: Wir nutzen "supabaseClient" statt "supabase", um Namenskonflikte zu vermeiden
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// 2. HTML-Elemente greifen
const searchForm = document.getElementById('search-form');
const searchInput = document.getElementById('search-input');
const resultsContainer = document.getElementById('results');
const loadingIndicator = document.getElementById('loading');

// 3. Event Listener für das Absenden der Suche
searchForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Verhindert Neuladen der Seite
    
    const query = searchInput.value.trim();
    if (!query) return;

    // UI-Zustand anpassen (Laden anzeigen, alte Ergebnisse löschen)
    loadingIndicator.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    resultsContainer.innerHTML = '';

    try {
        // 4. Datenbankabfrage an Supabase senden
        // Wir nutzen die PostgreSQL-Volltextsuche auf unserer Spalte "fts_document"
        const { data, error } = await supabaseClient
            .from('webpages')
            .select('title, url, description')
            .textSearch('fts_document', query);

        loadingIndicator.classList.add('hidden');

        if (error) {
            console.error("Fehler bei der Suche:", error);
            resultsContainer.innerHTML = `<p class="text-red-400">Ein Fehler ist aufgetreten.</p>`;
            resultsContainer.classList.remove('hidden');
            return;
        }

        // 5. Ergebnisse anzeigen
        if (data.length === 0) {
            resultsContainer.innerHTML = `<p class="text-gray-400 text-center">Keine Ergebnisse für "${query}" gefunden.</p>`;
        } else {
            data.forEach(page => {
                const resultHTML = `
                    <div class="p-5 bg-gray-800 rounded-lg border border-gray-750 hover:border-gray-600 transition-all">
                        <a href="${page.url}" target="_blank" class="text-xl font-semibold text-blue-400 hover:underline">
                            ${page.title}
                        </a>
                        <p class="text-xs text-emerald-400 mt-1 truncate">${page.url}</p>
                        <p class="text-sm text-gray-300 mt-2">${page.description || 'Keine Beschreibung verfügbar.'}</p>
                    </div>
                `;
                resultsContainer.insertAdjacentHTML('beforeend', resultHTML);
            });
        }
        
        resultsContainer.classList.remove('hidden');

    } catch (err) {
        console.error("Unerwarteter Fehler:", err);
        loadingIndicator.classList.add('hidden');
    }
});