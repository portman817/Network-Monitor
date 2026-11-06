# Anforderungen und Architektur

Stand: 6. November 2026.

## Ziel und Technologien

Network Monitor ist ein Lernprojekt zur Verwaltung von Netzwerkgeräten und zur späteren Überwachung ihrer Erreichbarkeit.

| Bereich | Technologien | Stand |
| --- | --- | --- |
| Backend | Python, FastAPI, Uvicorn, Pydantic | Vorhanden |
| Frontend | React, React DOM, Vite | Vorhanden |
| Speicherung | SQLite, SQLAlchemy | Implementiert: SQLAlchemy 2.0.57 |
| Tests | pytest, httpx | Installiert: pytest 9.2.0, httpx 0.28.1 |

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
- `frontend/src/App.jsx` ruft `/api/health` auf und verwaltet zusätzlich den Gerätestand. `components/DeviceForm.jsx` erstellt Geräte; `components/DeviceList.jsx` zeigt sie an. `api/devices.js` kapselt Geräteanfragen und verständliche Fehlermeldungen.
- `frontend/vite.config.js` bindet Vite an `127.0.0.1:5173` und leitet `/api` an `http://127.0.0.1:8000` weiter.
- Der Entwicklungsproxy verwendet denselben Ursprung; zusätzliche CORS-Konfiguration ist derzeit nicht erforderlich.
- Die Produktionsbereitstellung mit Backend ist noch nicht eingerichtet.

### Implementierte Erweiterung in Etappe 2

Getrennte Module für Datenbank und Sitzungen, SQLAlchemy-Modell, Pydantic-Schemata und Geräte-Router; eine Sitzung pro Anfrage und eine dateibasierte SQLite-Datenbank. Die Anwendung erzeugt die Tabellen beim Start über lifespan und schließt den Engine beim Beenden. Tests verwenden eigene temporäre Dateien.

## Grenzen der ersten Version

Etappen 1 bis 3 sind umgesetzt. Die bestätigte weitere Reihenfolge lautet: Etappe 4 ICMP Ping, Latenzmessung und Statusaktualisierung; Etappe 5 Fehlerbehandlung, Oberflächenverbesserungen und Tests; Etappe 6 Abschlussprüfung und Dokumentation. Die Detailplanung von Etappe 4 steht noch aus.

Etappe 2 enthält kein Ping, keine automatische Überwachung und keine neuen React-Komponenten. Authentifizierung, Alarmierung, Messwerthistorie und produktive Bereitstellung sind bislang nicht als verbindlicher Funktionsumfang bestätigt.

## Bestätigte Entscheidungen

Python, FastAPI, React und Vite bilden die technische Grundlage. SQLite und SQLAlchemy sind für Etappe 2 vorgegeben. Die Gerätefelder, der Anfangsstatus, beide Geräte-Endpunkte und die genannten Arbeitsbeschränkungen sind bestätigt.

## Implementierungsentscheidungen der freigegebenen Etappe 2

- Synchrones SQLAlchemy; Tabellenanlage über `create_all`, zunächst ohne Alembic. `create_all` ersetzt keine Migration bestehender Tabellen.
- Datenbankpfad `backend/data/network_monitor.sqlite3`, unabhängig vom Arbeitsverzeichnis aufgelöst.
- Nur `name` und `address` als Eingabefelder; restliche Werte serverseitig, Messwerte anfangs `NULL`.
- IPv4, IPv6, IDN-Domänen und einteilige lokale Namen; kanonische IP-Schreibweise, Domänen in Kleinbuchstaben, abschließenden Punkt entfernen.
- Namen nach Entfernung äußerer Leerzeichen auf 100 Zeichen begrenzen.
- Normalisierte Adressen in SQLite eindeutig speichern; HTTP-Antworten `201`, `409` und `422`; Geräteliste nach `id` sortieren.
- SQLAlchemy `2.0.57`, pytest `9.2.0` und httpx `0.28.1` nach gesonderter Installationsfreigabe installiert und in den Abhängigkeitsdateien fixiert.

`last_checked_at` bleibt in Etappe 2 `NULL`; vor späteren Messungen ist die UTC-Konvention umzusetzen. IPv6-Zonenkennungen, URLs, Ports, Pfade und rein numerische ungültige IP-Schreibweisen werden abgelehnt. Zusätzliche Eingabefelder werden mit `422` abgelehnt. Die Datenbank erzwingt die Eindeutigkeit des normalisierten Adresswerts; bei Konflikten erfolgt ein Rollback und die API liefert `409`. IDN-Konvertierung verwendet den Python-Codec `idna`.

## Anforderungen und Entscheidungen zu Etappe 3

- Geräte mit Name, Adresse, Status, Latenz und letztem Prüfzeitpunkt anzeigen. Fehlende Messwerte als fehlend kennzeichnen; keine Messungen simulieren.
- Formular mit Pflichtfeldern und Namenslänge bis 100 Zeichen; vollständige Adressvalidierung im Backend belassen.
- Nach erfolgreichem POST die Antwort sofort in die Liste übernehmen und den aktuellen Gesamtstand abrufen. Fehler beim anschließenden Abruf ändern den erfolgreichen Speichervorgang nicht.
- Eingaben bei Fehlern erhalten; Formular während des Speicherns sperren und parallele Übermittlung zusätzlich über eine Referenz verhindern.
- Abrufe beim erneuten Laden oder Verlassen der Anwendung abbrechen; veraltete Antworten nicht übernehmen.
- Ladezustand, leere Liste, Fehler und Wiederholungsmöglichkeit anzeigen. Bereits angezeigte Geräte bei einem Abruffehler erhalten.
- Russische Oberflächentexte, zugeordnete Formularbeschriftungen, Statusmeldungen und sichtbare Tastaturfokussierung; auf schmalen Bildschirmen einspaltiges Formular und horizontal verschiebbare Tabelle.
- Keine zusätzlichen Abhängigkeiten, keine Backend- oder Datenbankschemaänderung. Keine Netzwerkprüfungen der Geräte und kein periodischer Abruf.
