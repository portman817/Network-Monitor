# Network Monitor

Lokale Lernanwendung mit Python, FastAPI, SQLAlchemy, SQLite, React und Vite. Die sechs vereinbarten Entwicklungsetappen sind umgesetzt und geprüft. Geräte lassen sich dauerhaft speichern, anzeigen und manuell per ICMP prüfen. Die Oberfläche unterstützt Englisch, Deutsch und Russisch.

## Dokumentation

- [Agentenregeln](AGENTS.md)
- [Entwicklungsplan](docs/ROADMAP.md)
- [Anforderungen und Architektur](docs/REQUIREMENTS.md)
- [Entwicklungsjournal und Prüfnachweise](docs/DEVLOG.md)

## Voraussetzungen

- Windows mit systemeigenem Windows PowerShell und `.NET Ping` für ICMP.
- Vorhandenes `.venv` mit Python `3.14.5`; Backend-Abhängigkeiten in `backend/requirements.txt`, Testabhängigkeiten in `backend/requirements-dev.txt`.
- Node.js gemäß Paketdefinition `^20.19.0 || >=22.12.0`; vorhandene Frontend-Pakete und `frontend/package-lock.json` verwenden.
- Normale Benutzerrechte; keine Änderung von ExecutionPolicy oder Firewall erforderlich.

Keine neue Umgebung ungefragt erstellen. Abhängigkeiten nur nach gesonderter Benutzerfreigabe installieren. Folgende Befehle sind nur für eine genehmigte Einrichtung vorgesehen:

```powershell
& .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements-dev.txt
Push-Location .\frontend
npm ci
Pop-Location
```

## Backend starten

Ab Projektwurzel in einem eigenen PowerShell-Fenster:

```powershell
Set-Location C:\Users\CC-Student\PycharmProjects\Network-Monitor
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir .\backend --host 127.0.0.1 --port 8000 --reload
```

[Gesundheitsendpunkt](http://127.0.0.1:8000/api/health): `{"status":"ok"}`.

[Interaktive API-Dokumentation](http://127.0.0.1:8000/docs).

Weiterhin nur einen Backend-Worker verwenden: Die Prüfbegrenzung gilt je Prozess.

## Frontend starten

In einem zweiten PowerShell-Fenster:

```powershell
Set-Location C:\Users\CC-Student\PycharmProjects\Network-Monitor\frontend
npm run dev
```

[Anwendung öffnen](http://127.0.0.1:5173). Vite leitet `/api` an `http://127.0.0.1:8000` weiter. Der Entwicklungsproxy benötigt keine zusätzliche CORS-Konfiguration. Beide Server jeweils mit Ctrl+C beenden.

## Geräte und ICMP

Ein Gerät mit Name und IP-Adresse oder Domänenname hinzufügen. Namen haben nach Entfernung äußerer Leerzeichen 1–100 Zeichen; Nullzeichen sind verboten. Adressen werden syntaktisch geprüft und normalisiert. Duplikate liefern `409`, ungültige Eingaben `422`.

Die SQLite-Datei `backend/data/network_monitor.sqlite3` wird beim Start erstellt; der absolute Pfad ist unabhängig vom Arbeitsverzeichnis. Geräte und Messwerte überstehen einen Neustart. Datenbankdateien sind von Git ausgeschlossen. `create_all` erstellt fehlende Tabellen, ersetzt aber keine Migration bestehender Schemata.

Standardmäßig sind für reale ICMP-Prüfungen nur `127.0.0.1` und der Drucker `192.168.0.247` freigegeben. Das API-Feld `check_allowed` steuert die Prüfschaltfläche. Gespeicherte Geräte erhalten keine Prüferlaubnis. IPv6-Adressen und Domänennamen werden für ICMP abgelehnt. Es erfolgt keine DNS-Auflösung.

Eine manuelle Prüfung sendet einen Echo Request mit 1000 ms Antwortwartezeit. Der äußere Prozesswartezeitrahmen beträgt fünf Sekunden. Höchstens zwei Prüfungen je Prozess, keine gleichzeitige Prüfung derselben Geräte-ID und mindestens fünf Sekunden zwischen Prüfstarts. Die Oberfläche berücksichtigt Abkühlzeit und `Retry-After`.

Statuswerte: `unknown`, `online`, `offline`. Erfolg speichert Latenz und UTC-Zeitpunkt; bei fehlendem ICMP-Reply ist die Latenz `null`. Technische Fehler erhalten vorherige Messdaten. `offline` bedeutet keinen erfolgreichen ICMP-Reply und beweist nicht, dass das Gerät ausgeschaltet ist.

| Methode | Pfad | Zweck |
| --- | --- | --- |
| GET | `/api/health` | Backend-Gesundheitsantwort |
| GET | `/api/devices` | Nach ID sortierte Geräteliste |
| POST | `/api/devices` | Gerät aus `name` und `address` erstellen |
| POST | `/api/devices/{id}/check` | Erlaubtes Gerät manuell prüfen |
| DELETE | `/api/devices/{id}` | Gerät und letzten Messwert löschen |

Beim Backend-Start ersetzt `NETWORK_MONITOR_ALLOWED_ADDRESSES` die Standardliste durch eine kommaseparierte Liste aus privaten IPv4- und IPv4-Loopback-Adressen. Mit `$env:NETWORK_MONITOR_ALLOWED_ADDRESSES = "127.0.0.1"` bleibt beispielsweise nur die Loopback-Adresse in der Einzelliste. Für Änderungen das Backend neu starten. Eine leere Liste deaktiviert alle Einzelfreigaben.

Private IPv4-Netze können unabhängig davon über `NETWORK_MONITOR_ALLOWED_SUBNETS` als kommaseparierte CIDR-Liste freigegeben werden. Um eine Adresse zu sperren, muss sie sowohl aus der Einzelliste als auch aus der Freigabe durch überlappende Netze entfallen. Ein neu gespeichertes Gerät innerhalb eines freigegebenen Netzes ist sofort manuell prüfbar.

In der Geräteliste lassen sich Name und Adresse bearbeiten. Eine Namensänderung erhält den letzten Messwert. Eine Adressänderung setzt den Zustand auf `unknown` und entfernt Latenz und Prüfzeitpunkt. Die Oberfläche fragt vor dem Löschen nach Bestätigung. Während einer laufenden Prüfung lehnt die API Änderungen und Löschungen mit `409` ab.

### Geräte im eigenen Netz finden

Ein freigegebenes privates IPv4-Netz mit Präfix `/24` oder länger konfigurieren. Für das eigene Netz `192.168.0.0/24` beispielsweise vor dem Backend-Start in PowerShell:

```powershell
$env:NETWORK_MONITOR_ALLOWED_SUBNETS = "192.168.0.0/24"
```

In der Oberfläche das Netz auswählen und die Suche starten. Die Suche zeigt IP-Adressen und Latenzen von Hosts mit ICMP-Antwort. Firewalls oder Energiesparmodi können Antworten verhindern. Gefundene Geräte lassen sich einzeln mit der IP-Adresse als Anfangsnamen speichern. Beim Stoppen wartet die Oberfläche auf die laufende Gruppe, bevor eine neue Suche gestartet werden kann. Bei einer Zeitüberschreitung des Ping-Prozesses wird die betroffene Adresse übersprungen und in der Oberfläche mitgezählt.

## Sprachen und Fehler

Die Sprachauswahl bietet Englisch, Deutsch und Russisch. Reihenfolge beim Öffnen: gespeicherte gültige Wahl, unterstützte Browsersprache, sonst Englisch. Regionale Varianten wie `de-DE` werden erkannt. Der Browser speichert die manuelle Auswahl lokal; bei blockiertem Speicher funktioniert sie für die laufende Sitzung weiter.

Texte stehen in getrennten Wörterbüchern unter `frontend/src/i18n/`. Sprachwechsel aktualisieren auch bereits sichtbare Fehler, Erfolgsmeldungen, Datum, Zahlen und das HTML-Sprachattribut. Eingegebene Namen und Adressen sowie technische API-Werte werden nicht übersetzt.

Anfragen einschließlich Antwortinhalt sind auf zehn Sekunden begrenzt. Bei unklarem Ergebnis eines Schreibvorgangs zuerst die Liste aktualisieren; Schreibanfragen werden nicht automatisch wiederholt. Fehler werden bei betroffenen Feldern angezeigt. Vorhandene Geräte bleiben bei Verbindungsfehlern sichtbar; Listenaktualisierung prüft die Backend-Verbindung erneut.

## Tests und Build

Ab Projektwurzel:

```powershell
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe -m pip check
Push-Location .\frontend
npm test
npm run build
Pop-Location
```

Automatische Backend-Tests verwenden temporäre SQLite-Dateien und ersetzen Ping-Aufrufe. Frontend-Tests prüfen API-Client, Zeitrahmen, i18n und statische React-Ausgabe. Interaktive Browserprüfungen werden gesondert dokumentiert.

Abschlussprüfung am 6. November 2026: 91 Backend-Tests und 38 Frontend-Tests erfolgreich, Frontend-Build erfolgreich, `pip check` ohne Konflikte. Bekannte StarletteDeprecationWarning zur Verwendung von httpx mit TestClient bleibt bestehen. Browserprüfung aller drei Sprachen, Fehlerübersetzung, Speicherung, Loopback-ICMP, Neustartpersistenz, Verbindungswiederherstellung und 390-Pixel-Ansicht erfolgreich; genaue Nachweise im Entwicklungsjournal.

## Grenzen der ersten Version

Die Anwendung ist für lokale Entwicklung vorgesehen. Automatische Überwachung, Messwerthistorie, Authentifizierung, weitere freigegebene Netzwerkziele und produktive Bereitstellung sind nicht umgesetzt. `npm run build` erstellt Frontend-Artefakte, richtet aber keine gemeinsame Produktionsbereitstellung mit API ein. Mehrere Backend-Worker benötigen eine gemeinsame Prüfbegrenzung.

## Struktur

```text
backend/app/              # Anwendung, Datenbank, Modelle, Schemata, Ping und API-Router
backend/tests/            # Modell-, API-, Sicherheits- und Regressionstests
backend/requirements.txt  # Laufzeitabhängigkeiten
backend/requirements-dev.txt # Testabhängigkeiten
frontend/src/api/         # API-Client und Tests
frontend/src/components/  # Geräteformular, Tabelle und Tests
frontend/src/i18n/        # Wörterbücher, Sprachverwaltung und Tests
frontend/src/App.jsx      # Anwendungszustand und Sprachauswahl
frontend/src/styles.css   # Darstellung und responsive Regeln
docs/                     # Anforderungen, Etappen und Entwicklungsjournal
AGENTS.md                 # Dauerhafte Agentenregeln
pytest.ini                # Backend-Testkonfiguration
```
