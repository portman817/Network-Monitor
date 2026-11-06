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

## Etappe 3 – React-Geräteoberfläche: abgeschlossen

Vom Benutzer am 6. November 2026 freigegeben.

- [x] Geräte über `GET /api/devices` laden und tabellarisch anzeigen.
- [x] Formular für Name und Adresse mit `POST /api/devices` bereitstellen.
- [x] Fehlende Messwerte kenntlich machen; unbekannten Status anzeigen.
- [x] Ladezustand, leere Liste, Validierungsfehler und doppelte Adressen behandeln.
- [x] Mehrfache Formularübermittlung während des Speicherns verhindern.
- [x] Liste nach erfolgreicher Erstellung aktualisieren; Wiederholung fehlgeschlagener Abrufe ermöglichen.
- [x] Frontend-Build, neun API-Client-Tests und 40 Backend-Tests erfolgreich ausführen.
- [x] Browserprüfung mit isolierter Testdatenbank durchführen und Dokumentation aktualisieren.

## Etappe 4 – ICMP Ping, Latenzmessung und Statusaktualisierung: abgeschlossen

- [x] Vor Implementierungsbeginn den konkreten Umfang abstimmen und freigeben lassen.
- [x] Erlaubte Zieladressen und deren Durchsetzung vor Netzwerkprüfungen festlegen.
- [x] ICMP Ping und Latenzmessung implementieren.
- [x] Status und Prüfzeitpunkt nach definierter UTC-Konvention aktualisieren.
- [x] Erfolg, Nichterreichbarkeit und technische Fehler testen.

Freigabe: ausschließlich `127.0.0.1`; manuelle Einzelprüfung unter Windows. Statuswerte `unknown`, `online`, `offline`. 79 Backend-Tests, 16 Frontend-Tests und Frontend-Build erfolgreich; realer Loopback-Test samt Persistenzprüfung erfolgreich.

## Etappe 5 – Fehlerbehandlung, Oberflächenverbesserungen und Tests: geplant

- [ ] Fehlerbehandlung vervollständigen.
- [ ] Oberfläche anhand der bisherigen Ergebnisse verbessern.
- [ ] Separate Lokalisierungsaufgabe: i18n-Architektur mit getrennten Übersetzungswörterbüchern vorsehen, vorhandene Oberflächentexte aus Komponenten und API-Client auslagern und Englisch als Standardsprache einführen. Künftige Unterstützung für Englisch (`en`), Deutsch (`de`) und Russisch (`ru`) berücksichtigen; technische API-Werte und Identifikatoren unverändert lassen. Umsetzung noch ausstehend, derzeit nur dokumentiert.
- [ ] Tests erweitern und ausführen.

## Etappe 6 – Abschlussprüfung und Dokumentation: geplant

- [ ] Gesamte Anwendung und Zusammenspiel ihrer Komponenten prüfen.
- [ ] Dokumentation, Startanleitung und bekannte Einschränkungen abschließend aktualisieren.

Die Reihenfolge der Etappen 3 bis 6 ist vom Benutzer bestätigt. Automatische periodische Überwachung ist dadurch nicht zusätzlich freigegeben.

## Unmittelbarer nächster Schritt

Ergebnisse von Etappe 4 mit dem Benutzer prüfen; danach Umfang und Freigabe für Etappe 5 abstimmen. Keine Netzwerkprüfungen allein aufgrund eines gespeicherten Geräteeintrags ausführen.
