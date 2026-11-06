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

## Etappe 2 – SQLite und Gerätespeicherung: als Nächstes

Status: Anforderungen bekannt; Implementierung und zusätzliche Installationen noch nicht freigegeben.

- [ ] Offene technische Entscheidungen bestätigen lassen.
- [ ] Installation benötigter Abhängigkeiten gesondert genehmigen lassen.
- [ ] SQLAlchemy und dateibasierte SQLite-Speicherung einrichten.
- [ ] Gerätemodell mit `id`, `name`, `address`, `status`, `latency_ms` und `last_checked_at` implementieren.
- [ ] Anfangsstatus `unknown` sicherstellen.
- [ ] `GET /api/devices` und `POST /api/devices` implementieren.
- [ ] IP-Adressen und Domänennamen validieren; doppelte Adressen behandeln.
- [ ] Persistenz nach Backend-Neustart nachweisen.
- [ ] Modell- und API-Tests implementieren und ausführen.
- [ ] Dokumentation aktualisieren.

Ping, automatische Überwachung und neue React-Komponenten gehören nicht zu dieser Etappe. `/api/health` bleibt unverändert.

## Weitere Etappen – noch abzugleichen

Ein bestätigter vollständiger Etappenplan nach Etappe 2 ist weder im Repository noch in der verfügbaren Gesprächshistorie enthalten. Weitere Nummern, Termine und Funktionen werden deshalb nicht als vereinbart dargestellt.

- [ ] Früheren Gesamtplan mit dem Benutzer abgleichen und ergänzen.
- [ ] Reihenfolge und Umfang späterer Netzwerkprüfungen, automatischer Überwachung und Frontend-Erweiterungen bestätigen.
- [ ] Vor Netzwerkprüfungen die Beschränkung auf erlaubte Adressen konkret festlegen.

## Unmittelbarer nächster Schritt

Benutzerfreigabe für Etappe 2 und offene technische Entscheidungen einholen. Bis dahin keine Implementierung beginnen.
