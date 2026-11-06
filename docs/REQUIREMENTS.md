# Anforderungen und Architektur

Stand: 6. November 2026.

## Ziel und Technologien

Network Monitor ist ein Lernprojekt zur Verwaltung von Netzwerkgeräten und zur späteren Überwachung ihrer Erreichbarkeit.

| Bereich | Technologien | Stand |
| --- | --- | --- |
| Backend | Python, FastAPI, Uvicorn, Pydantic | Vorhanden |
| Frontend | React, React DOM, Vite | Vorhanden |
| Speicherung | SQLite, SQLAlchemy | Für Etappe 2 vorgegeben; nicht implementiert |
| Tests | pytest, httpx | Vorgeschlagen; nicht installiert |

## Funktionale Anforderungen

- Bestehend: `GET /api/health` liefert `{"status":"ok"}`; das Frontend zeigt Erfolg oder Fehler der Backend-Verbindung.
- Etappe 2: Geräte dauerhaft in SQLite speichern; Daten überstehen Backend-Neustarts.
- Gerätefelder: `id`, `name`, `address`, `status`, `latency_ms`, `last_checked_at`.
- Anfangsstatus: `unknown`.
- Geräte über `POST /api/devices` hinzufügen und über `GET /api/devices` abrufen.
- IP-Adressen und Domänennamen syntaktisch validieren sowie doppelte Adressen behandeln.
- Modell und API automatisiert testen; das Verhalten von `/api/health` erhalten.

## Nichtfunktionale Anforderungen

- Vorhandenes `.venv` verwenden; Installationen benötigen gesonderte Freigabe.
- Datenbankdateien nicht versionieren; Ausschlüsse sind in `.gitignore` vorhanden.
- Tests von Arbeitsdaten isolieren und ausschließlich tatsächliche Ergebnisse dokumentieren.
- Bei reiner Adressvalidierung keine Netzwerkzugriffe ausführen.
- Zukünftige Netzwerkprüfungen ausschließlich für erlaubte Adressen durchführen. Speicherung bedeutet keine Prüferlaubnis.
- Kommunikation auf Russisch, Dokumentation auf Deutsch, Markdown-Dateinamen auf Englisch.

## Architektur

### Bestehender Aufbau

- `backend/app/main.py` erstellt die FastAPI-Anwendung und definiert den Gesundheitsendpunkt.
- `frontend/src/App.jsx` ruft `/api/health` auf und zeigt das Ergebnis an.
- `frontend/vite.config.js` bindet Vite an `127.0.0.1:5173` und leitet `/api` an `http://127.0.0.1:8000` weiter.
- Der Entwicklungsproxy verwendet denselben Ursprung; zusätzliche CORS-Konfiguration ist derzeit nicht erforderlich.
- Die Produktionsbereitstellung mit Backend ist noch nicht eingerichtet.

### Vorschlag für Etappe 2

Getrennte Module für Datenbank und Sitzungen, SQLAlchemy-Modell, Pydantic-Schemata und Geräte-Router; eine Sitzung pro Anfrage und eine dateibasierte SQLite-Datenbank. Diese Detailarchitektur benötigt noch Bestätigung.

## Grenzen der ersten Version

Der unmittelbar bestätigte Aufgabenbereich umfasst das bestehende Grundgerüst und die Anforderungen an Etappe 2. Ein vollständiger Umfang einer späteren ersten Gesamtversion ist in der verfügbaren Historie nicht festgelegt.

Etappe 2 enthält kein Ping, keine automatische Überwachung und keine neuen React-Komponenten. Authentifizierung, Alarmierung, Messwerthistorie und produktive Bereitstellung sind bislang nicht als verbindlicher Funktionsumfang bestätigt.

## Bestätigte Entscheidungen

Python, FastAPI, React und Vite bilden die technische Grundlage. SQLite und SQLAlchemy sind für Etappe 2 vorgegeben. Die Gerätefelder, der Anfangsstatus, beide Geräte-Endpunkte und die genannten Arbeitsbeschränkungen sind bestätigt.

## Noch nicht bestätigte Vorschläge

- Synchrones SQLAlchemy; Tabellenanlage über `create_all`, zunächst ohne Alembic. `create_all` ersetzt keine Migration bestehender Tabellen.
- Datenbankpfad `backend/data/network_monitor.sqlite3`, unabhängig vom Arbeitsverzeichnis aufgelöst.
- Nur `name` und `address` als Eingabefelder; restliche Werte serverseitig, Messwerte anfangs `NULL`.
- IPv4, IPv6, IDN-Domänen und einteilige lokale Namen; kanonische IP-Schreibweise, Domänen in Kleinbuchstaben, abschließenden Punkt entfernen.
- Namen nach Entfernung äußerer Leerzeichen auf 100 Zeichen begrenzen.
- Normalisierte Adressen in SQLite eindeutig speichern; HTTP-Antworten `201`, `409` und `422`; Geräteliste nach `id` sortieren.
- Kompatible Versionen von SQLAlchemy, pytest und httpx auswählen und deren Installation gesondert freigeben lassen.
