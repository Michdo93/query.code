CREATE OR REPLACE FUNCTION search_webpages_with_headline(query_text TEXT)
RETURNS TABLE (
    id BIGINT,
    url TEXT,
    title TEXT,
    headline TEXT
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        webpages.id,
        webpages.url,
        webpages.title,
        -- Hier passiert die Magie: ts_headline schneidet den Text um das Suchwort herum aus
        ts_headline('german', webpages.content, plainto_tsquery('german', query_text), 
            'StartSel=<b>, StopSel=</b>, MaxWords=35, MinWords=15, ShortWord=3') AS headline
    FROM webpages
    WHERE webpages.fts_document @@ plainto_tsquery('german', query_text)
    ORDER BY ts_rank(webpages.fts_document, plainto_tsquery('german', query_text)) DESC;
END;
$$;