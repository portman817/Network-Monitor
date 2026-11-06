# Entwicklungsjournal

## 5. November 2026 – Grundgerüst und erster Commit

### Durch Quellcode und Git belegte Angaben

- FastAPI-Grundgerüst mit `GET /api/health` und `{"status":"ok"}` erstellt.
- React-Oberfläche zur Backend-Verbindungsprüfung und Vite-Proxy für `/api` eingerichtet.
- Abhängigkeitsdateien, Frontend-Sperrdatei, `.gitignore` und Startanleitung aufgenommen.
- Erster lokaler Commit: `ea42fd0d408dcc23a99b2024943deaac85696b9a`.
- Commit-Zeit laut Git: 5. November 2026, 15:09:56 Uhr, UTC+01:00.
- Commit-Betreff: `feat: initialize Network Monitor project`.

Die genauen Zeitpunkte einzelner Implementierungs- und Installationsschritte sind nicht unabhängig belegt.

### Installationen und Prüfungen laut bisheriger README

Die vorhandene README datierte folgende Angaben auf den 5. November 2026:

- `.venv` mit Python `3.14.5`; FastAPI `0.162.0` und Uvicorn `0.54.0` installiert.
- `pip check` ohne gemeldete Konflikte.
- React und React DOM `19.3.1`, Vite `8.3.6`, `@vitejs/plugin-react` `6.2.1`, Node.js `24.11.1`, npm `11.6.2`.
- Beide Server gestartet; API direkt und über Vite geprüft.
- Erfolgsanzeige und Verbindungsfehler bei abgeschaltetem Backend im Browser geprüft.
- `npm run build` erfolgreich; Testserver anschließend beendet.

Diese Angaben sind übernommene historische Berichte, keine erneuten Prüfungen. Separate Ausführungsprotokolle liegen in der ausgewerteten Historie nicht vor. Automatisierte Modell- und API-Tests sind im Repository nicht vorhanden; ein erfolgreicher Testlauf wird nicht behauptet.

## 6. November 2026 – Analyse vor Etappe 2

- Projektstruktur, Quellcode, README und Git geprüft: Branch `master`, Arbeitsverzeichnis sauber.
- `AGENTS.md` und `docs/` fehlten; Gerätespeicherung und Geräte-API waren nicht vorhanden.
- Bestehende Umgebung lesend geprüft: Python `3.14.5`, SQLite `3.50.4`, FastAPI `0.162.0`, Uvicorn `0.54.0`, Pydantic `2.14.3`.
- SQLAlchemy, pytest, httpx und Alembic waren bei dieser Prüfung nicht installiert.
- Implementierungsplan vorgeschlagen; technische Details und zusätzliche Installationen noch nicht freigegeben.

## 6. November 2026 – Projektdokumentation

- Struktur, Quelldateien, README und Git-Historie erneut gelesen; Git-Status vor Änderungen weiterhin sauber.
- `AGENTS.md`, `docs/ROADMAP.md`, `docs/REQUIREMENTS.md` und `docs/DEVLOG.md` erstellt.
- README auf Deutsch übertragen und mit der Projektdokumentation verknüpft.
- Bestätigte Anforderungen von offenen Vorschlägen getrennt; fehlenden Gesamtplan nach Etappe 2 ausdrücklich gekennzeichnet.
- Keine Anwendungsquellen geändert, keine Abhängigkeiten installiert, keine Server gestartet und keine Builds oder Anwendungstests erneut ausgeführt.
- Keine Commits und keinen Push ausgeführt.

Aktueller Status: Etappe 1 abgeschlossen, Dokumentationsgrundlage erstellt, Etappe 2 nicht begonnen.

Nächster Schritt: Benutzerfreigabe für Etappe 2, technische Details und gesonderte Abhängigkeitsinstallation einholen; weiteren Gesamtplan abgleichen.


## 6. November 2026 – Etappe 2 umgesetzt und geprüft

- Benutzerfreigabe für die Implementierung erhalten; gesonderte Freigabe für Installation in das bestehende `.venv` erhalten.
- SQLAlchemy `2.0.57`, pytest `9.2.0`, httpx `0.28.1` und deren Abhängigkeiten installiert. Die erste Installation scheiterte an der Netzwerkisolation; die freigegebene Wiederholung war erfolgreich.
- SQLite-Modell, Sitzungen pro Anfrage, Anwendungsfabrik und Tabelleninitialisierung implementiert.
- `GET /api/devices` und `POST /api/devices` mit Normalisierung, Syntaxprüfung und datenbankgestützter Eindeutigkeit implementiert. `/api/health` behält Antwort und Pfad.
- 40 Tests über `.venv/Scripts/python.exe -m pytest -q` erfolgreich: Modellvorgaben, Datenbank-Eindeutigkeit, API, ungültige Eingaben, parallele Duplikate, Fehlerbehandlung und Persistenz über zwei Anwendungsinstanzen.
- Persistenz wurde ohne externe Serverprozesse durch Schließen und erneutes Öffnen derselben temporären Datenbank geprüft. Es wurde kein manueller Neustart eines Uvicorn-Prozesses durchgeführt.
- Testausgabe: `40 passed, 1 warning`. StarletteDeprecationWarning: TestClient kündigt die Verwendung von httpx ab und empfiehlt httpx2. Keine zusätzliche Bibliothek dafür installiert.
- `.venv/Scripts/python.exe -m pip check`: `No broken requirements found.`
- Keine Änderungen am Frontend, kein Ping, keine automatische Überwachung, kein Commit und kein Push.

Aktueller Status: Etappe 2 umgesetzt und automatisiert geprüft. Nächster Schritt: Benutzerprüfung und Abstimmung des weiteren Etappenplans.


## 6. November 2026 – Etappe 3: Geräteoberfläche

- Vor Beginn Agentenregeln, README, alle Projektdokumente, Quellcode und Git-Status gelesen. Arbeitsverzeichnis war sauber; Etappe 2 ist im Commit `721981f` gespeichert.
- Benutzerfreigabe für Etappe 3 und die Reihenfolge der weiteren Etappen 4 bis 6 erhalten; ROADMAP entsprechend ergänzt.
- API-Client, Formular und Gerätetabelle erstellt; Ladezustände, leere Liste, Fehler, Erfolgsmeldung und erneuten Abruf ergänzt.
- Nach Speicherung Liste aktualisiert; parallele Formularübermittlung und veraltete Abrufantworten verhindert.
- `npm run build` erfolgreich: Vite 8.3.6, 19 Module verarbeitet.
- `npm test`: neun API-Client-Tests erfolgreich, einschließlich POST-Inhalt, Abbruch, Netzwerkfehler, HTTP 409/422/502 und ungültiger Antworten.
- `.venv/Scripts/python.exe -m pytest -q`: 40 Tests erfolgreich, eine bereits bekannte StarletteDeprecationWarning zu httpx/TestClient.
- `.venv/Scripts/python.exe -m pip check`: keine beschädigten Abhängigkeiten gemeldet.
- Im Browser leere Liste, Geräteerstellung, Anzeige fehlender Messdaten, Duplikat und ungültige Adresse geprüft. Nach Neuladen blieb das Gerät sichtbar.
- Backend für Fehlerprüfung beendet: Listendaten blieben sichtbar, HTTP-502-Meldung erschien. Nach Backend-Neustart und erneuter Listenaktualisierung verschwand die Fehlermeldung.
- Für Browserprüfung eigene SQLite-Datei `.pytest_cache/ui-stage3.sqlite3` verwendet; Arbeitsdatenbank nicht mit Testgeräten befüllt. Beide Testserver anschließend beendet.
- Responsive CSS implementiert; keine gesonderte mobile Browserprüfung und keine automatisierten React-Komponententests durchgeführt.
- Keine Abhängigkeiten installiert, keine Backend-Quellen geändert, kein Ping, keine automatische Überwachung, kein Commit und kein Push.

Aktueller Status: Etappe 3 umgesetzt und geprüft. Nächster Schritt: Benutzerprüfung, danach Detailplanung und Freigabe für Etappe 4 einschließlich erlaubter Zieladressen.


## 6. November 2026 – Etappe 4: manuelle ICMP-Prüfung

- Dokumentation, relevante Quellen und Git geprüft; Arbeitsverzeichnis vor Beginn sauber.
- Benutzerfreigabe umgesetzt: Zustände `unknown`, `online`, `offline`; reale Prüfungen ausschließlich für `127.0.0.1`. Frühere Frontend-Bezeichnungen für `up`/`down` durch die freigegebenen Zustände ersetzt; vorherige Projektetappen erzeugten keine solchen Messergebnisse.
- `backend/app/ping.py` mit mehrstufiger Zielprüfung, Windows-PowerShell/.NET-Adapter, strukturierten Ergebnissen, Prozesszeitrahmen und Begrenzung paralleler Prüfungen erstellt.
- `POST /api/devices/{id}/check` ergänzt; kurze separate Datenbanksitzungen, atomare Ergebnisspeicherung und UTC-Verarbeitung ohne Schemaänderung implementiert.
- Manuelle Prüfschaltfläche und gerätebezogene Fehlermeldungen ergänzt; veraltete Listenantworten überschreiben keine neueren Prüfergebnisse.
- Erste reale Loopback-Prüfung lieferte `online`, zeigte aber einen Dekodierungsfehler im diagnostischen PowerShell-Ausgabestrom. UTF-8-Ausgabe, deaktivierte Fortschrittsmeldungen und robuste Dekodierung ergänzt. Wiederholung ohne diesen Fehler erfolgreich.
- Automatische Tests mit unterdrückten Netzwerkaufrufen: 79 Backend-Tests erfolgreich, eine bekannte StarletteDeprecationWarning zur httpx-Verwendung in TestClient. Unter anderem verbotene Ziele ohne DNS/Prozessstart, Zeitüberschreitung, ungültige Prozessantworten, Null-Latenz, Nichterreichbarkeit, Begrenzungen, parallele API-Aufrufe, technische Fehler, Speicherfehler, UTC und Persistenz geprüft.
- `npm test`: 16 Tests erfolgreich. `npm run build`: erfolgreich, 19 Module verarbeitet. `pip check`: `No broken requirements found.`
- Realer API-Test über TestClient und temporäre SQLite-Datei: ausschließlich `127.0.0.1`, HTTP `200`, `online`, `0.0` ms und UTC-Zeit mit `Z`. Erneutes Öffnen der Anwendung mit derselben Testdatei bestätigte Persistenz. Arbeitsdatenbank nicht verändert.
- Keine anderen Ziele geprüft, keine DNS-Auflösung, keine neuen Pakete, keine externen Server gestartet, kein Commit und kein Push. Keine neue Browserprüfung durchgeführt.

Aktueller Status: Etappe 4 implementiert und geprüft. Nächster Schritt: Benutzerprüfung und Abstimmung des Umfangs von Etappe 5. Die Loopback-Beschränkung bleibt verbindlich.


## 6. November 2026 – Drei bestätigte P2-Befunde korrigiert

- Vor Änderungen `AGENTS.md`, README und aktuelle Projektdokumentation gelesen und Git-Status geprüft.
- In `backend/tests/test_review_regressions.py` neun parametrisierte Prüfungen ergänzt. Vor der Korrektur: acht fehlgeschlagen, eine gültige ID-Grenzprüfung erfolgreich. Damit wurden alle drei Befunde vor ihrer Behebung reproduziert.
- Datenbankantworten für Geräteerstellung und Prüf-Ergebnis vor dem Commit vorbereitet; nach erfolgreichem Commit kein `refresh` oder implizites Nachladen mehr. Der Regressionstest simuliert einen ORM-Lesefehler nach dem Commit und prüft sowohl die erfolgreiche Antwort als auch die gespeicherten Werte.
- Nullzeichen am Anfang, in der Mitte oder am Ende eines Gerätenamens werden mit `422` abgelehnt; keine Datensätze angelegt.
- Geräte-ID für den Prüf-Endpunkt auf den positiven SQLite-INTEGER-Bereich begrenzt. Positive und negative Überläufe sowie Null liefern `422`; die maximal zulässige, nicht vorhandene ID liefert `404`.
- Nach der Korrektur: alle neun Regressionstests erfolgreich. Gesamter Backend-Testlauf: 88 erfolgreich, eine bekannte StarletteDeprecationWarning zu httpx/TestClient.
- Frontend: `npm test` mit 16 erfolgreichen Tests; `npm run build` erfolgreich. `pip check`: `No broken requirements found.`
- Keine Frontend-Quellen, keine Datenbankschemata und keine Ping-Freigaben verändert. Keine Abhängigkeiten installiert, keine realen Netzwerkprüfungen, kein Commit und kein Push.

Aktueller Status: Nur die drei beauftragten Fehlerkorrekturen aus Etappe 5 umgesetzt. Lokalisierung und weitere Verbesserungen bleiben offen.


## 6. November 2026 – Etappe 5 abgeschlossen

- Vor Beginn Agentenregeln, aktuelle Anforderungen, Entwicklungsplan, Journal, README, betroffene Quellen und sauberen Git-Status geprüft. Benutzerfreigabe für den vorgeschlagenen Umfang erhalten.
- Englisches Wörterbuch und i18n-Zugriff eingeführt; russische UI-Zeichenketten aus Komponenten und API-Client entfernt. Englische Standardsprache, Rückfall, Parameterersetzung und passende Datums-/Zahlenformatierung getestet. Deutsche/russische Vollübersetzungen und Sprachauswahl bleiben offen.
- Zehn Sekunden Anfragezeitrahmen einschließlich Antwortinhalt, strukturierte API-Fehler, Feldmeldungen und Retry-After-Verarbeitung ergänzt. Unklare Schreibresultate werden nicht automatisch wiederholt.
- Backend-Fehler bei Datenbankzugriffen vereinheitlicht und durch drei zusätzliche Tests abgesichert. Sicherheitsregeln und Gesundheitsendpunkt unverändert.
- Unterschiedliche Statusdarstellung, gesperrte verbotene Ziele und Abkühlzeit ergänzt. Listenaktualisierung prüft die Backend-Verbindung erneut.
- Automatische Prüfung: 91 Backend-Tests erfolgreich, eine bekannte StarletteDeprecationWarning. 31 Frontend-Tests erfolgreich, einschließlich API-Client, Zeitüberschreitungen, i18n und statischen React-Komponenten. Frontend-Build erfolgreich, 21 Module; pip check ohne Konflikte.
- Browser mit isolierter SQLite-Datei `.pytest_cache/stage5-ui.sqlite3`: englische Oberfläche, leere Liste, Feldfehler mit erhaltenen Eingaben, erfolgreiche Erstellung, reale ICMP-Prüfung ausschließlich zu `127.0.0.1` und deaktivierte externe Ziele bestätigt. Bei abgeschaltetem Backend blieben Daten sichtbar; nach Neustart und Aktualisierung erschienen wieder verbundener Status und Geräteliste.
- Darstellung bei 390 Pixel Breite geprüft: einspaltiges Formular und horizontal verschiebbare Tabelle. Temporäre Ansichtsgröße zurückgesetzt und beide Testserver beendet.
- Bei der Prüfung festgestellt: Feldfehlermeldung innerhalb eines Labels verändert dessen zugänglichen Namen. Meldungen außerhalb des Labels mit aria-describedby verknüpft; Frontend-Tests und Build danach erneut erfolgreich.
- Änderungen mit ponytail-review geprüft: API-Verträge, Aufrufer, Tests, Schreibantworten, Abbruch und Loopback-Grenze geprüft. Nach Korrektur keine weiteren konkreten blockierenden Befunde festgestellt. Keine automatisierten interaktiven Browsertests; Komponententests prüfen statische Ausgabe.
- Keine neuen Abhängigkeiten, keine automatische Überwachung, kein Commit und kein Push.

Nächster Schritt: Benutzerprüfung und Freigabe der Etappe 6 zur Abschlussprüfung und Dokumentation.
