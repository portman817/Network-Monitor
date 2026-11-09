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

## Etappe 5 – Fehlerbehandlung, Oberflächenverbesserungen und Tests: abgeschlossen

- [x] Drei bestätigte P2-Befunde gezielt beheben: Lesen nach Commit, Nullzeichen im Gerätenamen und Überlauf der Geräte-ID; Regressionstests vor und nach den Korrekturen ausführen.
- [x] Weitere Fehlerbehandlung vervollständigen: strukturierte Datenbankfehler, Feldfehler, Anfragezeitrahmen und Wiederholung.
- [x] Oberfläche verbessern: unterscheidbare Statusanzeigen, Abkühlzeit, Erklärung verbotener Ziele und schmaler Bildschirm.
- [x] Separate Lokalisierungsaufgabe: i18n-Architektur mit getrennten Übersetzungswörterbüchern vorsehen, vorhandene Oberflächentexte aus Komponenten und API-Client auslagern und Englisch als Standardsprache einführen. Künftige Unterstützung für Englisch (`en`), Deutsch (`de`) und Russisch (`ru`) berücksichtigen; technische API-Werte und Identifikatoren unverändert lassen. Englisches Wörterbuch und Rückfall auf Englisch implementiert; vollständige deutsche und russische Übersetzungen sowie Sprachauswahl wurden anschließend in Etappe 6 umgesetzt.
- [x] Tests erweitern und ausführen: 91 Backend-Tests und 31 Frontend-Tests sowie Build erfolgreich. Browserprüfung und Prüfung der Änderungen nach ponytail-review durchgeführt.

## Etappe 6 – Vollständige Lokalisierung, Abschlussprüfung und Dokumentation: abgeschlossen

- [x] Vollständige deutsche (`de`) und russische (`ru`) Wörterbücher ergänzen; englisches Wörterbuch (`en`) beibehalten.
- [x] Sprachauswahl für English / Deutsch / Русский über Wörterbücher implementieren und Benutzerwahl lokal speichern.
- [x] Sprachpriorität umsetzen: gespeicherte gültige Auswahl, unterstützte Browsersprache, sonst Englisch. Regionale Sprachvarianten berücksichtigen.
- [x] Texte, Fehlermeldungen, Datum, Zahlen und HTML-Sprachattribut beim Sprachwechsel aktualisieren; technische API-Werte unverändert lassen.
- [x] Automatische Tests und Browserprüfungen für alle drei Sprachen einschließlich Sprachwahl und Speicherung durchführen.
- [x] Gesamte Anwendung und Zusammenspiel ihrer Komponenten prüfen.
- [x] Alle Tests, Frontend-Build und abschließendes Code-Review durchführen.
- [x] Dokumentation, Startanleitung und bekannte Einschränkungen abschließend aktualisieren.

Die erste lokale Version umfasst die abgeschlossenen Etappen 1 bis 6. Die folgende Weiterentwicklung in den Etappen 7 bis 12 wurde vom Benutzer als Planung bestätigt. Diese Planung erteilt noch keine Implementierungsfreigabe und erweitert keine erlaubten Netzwerkziele.

## Weiterentwicklung – vereinbarte Planung

Für jede Etappe vor Beginn den konkreten Umfang und die Umsetzung mit dem Benutzer abstimmen. Neue Abhängigkeiten und zusätzliche reale Netzwerkziele benötigen gesonderte Freigabe. Aktuell sind `127.0.0.1` und der ausdrücklich freigegebene Drucker `192.168.0.247` für ICMP erlaubt. Gespeicherte Geräte erhalten keine automatische Prüferlaubnis.

## Etappe 7 – Geräteverwaltung und Prüfberechtigungen: teilweise umgesetzt

- [ ] Geräte bearbeiten; Namen und Adressen weiterhin validieren und Duplikate behandeln.
- [x] Geräte mit Bestätigung und letztem Messwert löschen.
- [x] Manuelle Prüfungen für neu gespeicherte Geräte innerhalb ausdrücklich konfigurierter privater IPv4-Netze ermöglichen.
- [x] Geräte auf Benutzeranforderung in konfigurierten privaten IPv4-Netzen mit Präfix `/24` oder länger per ICMP suchen und Treffer einzeln übernehmen.
- [ ] Erlaubte Prüfziele ausdrücklich verwalten und von bloß gespeicherten Geräteadressen trennen.
- [ ] Erweiterung auf eigene Netzwerkadressen nur nach gesonderter Benutzerfreigabe planen; bisherige Loopback-Beschränkung bis dahin beibehalten.
- [ ] API, Oberfläche, Berechtigungen und Fehlerfälle testen; Übersetzungen und Dokumentation aktualisieren.

## Etappe 8 – Automatische Überwachung: geplant

- [ ] Einstellbares Prüfintervall sowie Start und Stopp der Überwachung bereitstellen.
- [ ] Nur ausdrücklich erlaubte Ziele prüfen; Parallelität und Zeitrahmen begrenzen.
- [ ] Doppelte Überwachungsstarts verhindern und Verhalten bei mehreren Prozessen festlegen.
- [ ] Prüfstarts zeitlich leicht zufällig verteilen, um gleichzeitige Lastspitzen zu vermeiden.
- [ ] Laufende Prüfungen beim Stoppen kontrolliert abschließen oder beenden; Neustartverhalten definieren.
- [ ] Zeitsteuerung, Begrenzungen, Fehler und Beendigung mit simulierten Netzwerkaufrufen testen.

## Etappe 9 – Messwerthistorie: geplant

- [ ] Vor Änderungen am bestehenden Datenbankschema Migrationen einführen und Datenerhalt prüfen.
- [ ] Prüfergebnisse mit Zeitpunkten, Latenz und Zustandswechseln in einer eigenen Tabelle speichern.
- [ ] Beginn und Dauer von Störungen nachvollziehbar machen; technische Prüffehler von fehlenden ICMP-Antworten unterscheiden.
- [ ] Aufbewahrungsdauer und Bereinigung festlegen, damit die Datenbank nicht unbegrenzt wächst.
- [ ] Historienabruf, Migrationen und Bereinigung testen und dokumentieren.

## Etappe 10 – Zustandsübersicht: geplant

- [ ] Anzahl und Status der Geräte übersichtlich zusammenfassen.
- [ ] Suche, Filter und Sortierung ergänzen.
- [ ] Latenzverlauf und Anteil erfolgreicher Prüfungen darstellen; Zeitraum und Berechnungsgrundlage eindeutig anzeigen.
- [ ] Fehlende Messdaten und technische Fehler kenntlich machen; Darstellung in allen drei Sprachen und auf schmalen Bildschirmen prüfen.

## Etappe 11 – Benachrichtigungen: geplant

- [ ] Ereignisse zunächst innerhalb der Anwendung anzeigen.
- [ ] Nichterreichbarkeit erst nach einer festgelegten Anzahl aufeinanderfolgender Fehlschläge melden; Wiederherstellung gesondert anzeigen.
- [ ] Wiederholte Meldungen begrenzen und Fehlalarme reduzieren.
- [ ] Externe Benachrichtigungskanäle nur bei Bedarf nach gesonderter Auswahl und Freigabe hinzufügen; keine Nachrichten ohne ausdrücklichen Auftrag versenden.
- [ ] Auslösung, Entwarnung und Begrenzung von Meldungen testen.

## Etappe 12 – Einfacher Start und Versionsausgabe: geplant

- [ ] Start mit einem Befehl ermöglichen und kontrolliertes Beenden sicherstellen.
- [ ] Anwendungseinstellungen nachvollziehbar verwalten.
- [ ] Datenbank sichern und wiederherstellen; Wiederherstellung praktisch prüfen.
- [ ] Aktualisierungsanleitung einschließlich Datensicherung und Migrationen erstellen.
- [ ] Gesamtablauf, Tests, Build und abschließendes Code-Review durchführen; Start- und Bedienungsanleitung aktualisieren.

## Weitere Optionen – noch keiner Etappe zugeordnet

- [ ] TCP-Portprüfungen und HTTP-Dienstprüfungen bei Bedarf separat planen; erfolgreiche Dienste können trotz fehlender ICMP-Antwort verfügbar sein. Auch hierfür gelten ausdrückliche Zielberechtigungen.
- [ ] Vor einem Zugriff von anderen Computern eine eigene Etappe für Authentifizierung und Zugriffsschutz planen und umsetzen. Eine Netzwerkbereitstellung ist durch die vorstehende Planung nicht freigegeben.

## Prüfungen und Abschluss jeder weiteren Etappe

Implementierung und Dokumentation fertigstellen, passende Tests und Build ausführen, Änderungen mit ponytail-review prüfen, bestätigte Befunde beheben und betroffene Prüfungen wiederholen. Ein vollständiges Projektreview bei wesentlichen Meilensteinen ergänzen. Commit und Push bleiben gesondert genehmigungspflichtig.

## Unmittelbarer nächster Schritt

Erste lokale Version abnehmen und den konkreten Umfang von Etappe 7 planen. Danach ausdrückliche Implementierungsfreigabe einholen. Etappe 7 ist teilweise umgesetzt. Etappen 8 bis 12 sind geplant; reale ICMP-Prüfungen sind auf `127.0.0.1` und `192.168.0.247` beschränkt.
