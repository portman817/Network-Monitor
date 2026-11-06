# Entwicklungsplan

Stand: 6. November 2026.

## Etappe 1 – abgeschlossen

- [x] Backend-Grundgerüst mit Python, FastAPI und Uvicorn erstellen.
- [x] `GET /api/health` mit `{"status":"ok"}` implementieren.
- [x] React-Oberfläche mit Vite und Anzeige der Backend-Erreichbarkeit erstellen.
- [x] Entwicklungsproxy für `/api` einrichten.
- [x] Abhängigkeiten installieren und Grundprüfungen durchführen; laut bisheriger README am 5. November 2026.
- [x] Frontend-Build erfolgreich prüfen; laut bisheriger README.
- [x] Ersten lokalen Git-Commit erstellen: `ea42fd0d408dcc23a99b2024943deaac85696b9a`, 5. November 2026.

Historische Laufzeitprüfungen wurden bei der Dokumentationsarbeit nicht wiederholt. Die Nachweisgrenzen stehen in `DEVLOG.md`.

## Dokumentationsgrundlage – erstellt

- [x] Agentenregeln, Anforderungen, Entwicklungsplan und Entwicklungsjournal anlegen.
- [x] README auf Deutsch übertragen und mit der Dokumentation verknüpfen.

## Etappe 2 – SQLite und Gerätespeicherung: abgeschlossen

Status: Implementierung vom Benutzer freigegeben; Installation von SQLAlchemy, pytest und httpx gesondert genehmigt. 40 Tests erfolgreich; Einzelheiten in DEVLOG.md.

- [x] Technische Details im Rahmen der freigegebenen Etappe festlegen und dokumentieren.
- [x] Installation benötigter Abhängigkeiten gesondert genehmigen lassen.
- [x] SQLAlchemy und dateibasierte SQLite-Speicherung einrichten.
- [x] Gerätemodell mit `id`, `name`, `address`, `status`, `latency_ms` und `last_checked_at` implementieren.
- [x] Anfangsstatus `unknown` sicherstellen.
- [x] `GET /api/devices` und `POST /api/devices` implementieren.
- [x] IP-Adressen und Domänennamen validieren; doppelte Adressen behandeln.
- [x] Persistenz nach Backend-Neustart nachweisen.
- [x] Modell- und API-Tests implementieren und ausführen.
- [x] Dokumentation aktualisieren.

Ping, automatische Überwachung und neue React-Komponenten gehören nicht zu dieser Etappe. `/api/health` bleibt unverändert.

## Weitere Etappen – noch abzugleichen

Ein bestätigter vollständiger Etappenplan nach Etappe 2 ist weder im Repository noch in der verfügbaren Gesprächshistorie enthalten. Weitere Nummern, Termine und Funktionen werden deshalb nicht als vereinbart dargestellt.

- [ ] Früheren Gesamtplan mit dem Benutzer abgleichen und ergänzen.
- [ ] Reihenfolge und Umfang späterer Netzwerkprüfungen, automatischer Überwachung und Frontend-Erweiterungen bestätigen.
- [ ] Vor Netzwerkprüfungen die Beschränkung auf erlaubte Adressen konkret festlegen.

## Unmittelbarer nächster Schritt

Ergebnisse der Etappe 2 mit dem Benutzer prüfen und den weiteren Etappenplan abstimmen. Keine zusätzlichen Überwachungsfunktionen ohne neue Freigabe beginnen. Der Persistenznachweis erfolgte durch zwei getrennte Anwendungsinstanzen mit geschlossenen und neu geöffneten Datenbankverbindungen, ohne externe Serverprozesse.
