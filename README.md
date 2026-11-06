# Network Monitor

Lernprojekt mit Python, FastAPI, React und Vite. Etappe 1 umfasst das Oberflächengrundgerüst und `GET /api/health` mit der Antwort `{"status":"ok"}`. Etappe 2 ergänzt SQLite-Gerätespeicherung und REST-API. Etappe 3 bietet die React-Oberfläche zum Anzeigen und Hinzufügen von Geräten. Ping und automatische Überwachung sind noch nicht implementiert.

## Projektdokumentation

- [Agentenregeln](AGENTS.md)
- [Entwicklungsplan](docs/ROADMAP.md)
- [Anforderungen und Architektur](docs/REQUIREMENTS.md)
- [Entwicklungsjournal](docs/DEVLOG.md)

## Voraussetzungen und bisherige Prüfungen

- Vorhandenes `.venv` mit Python `3.14.5`.
- Node.js `20.19+` oder `22.12+`; laut Paketdefinition `^20.19.0 || >=22.12.0`.
- Windows PowerShell und normale Benutzerrechte.

Die bisherige README meldete für den 5. November 2026: FastAPI `0.162.0`, Uvicorn `0.54.0` und `pip check` ohne Konflikte; React und React DOM `19.3.1`, Vite `8.3.6`, `@vitejs/plugin-react` `6.2.1`, Node.js `24.11.1` und npm `11.6.2`.

Laut diesem Bericht wurden beide Server, die API direkt und über den Vite-Proxy sowie die Erfolgs- und Fehleranzeige im Browser geprüft. `npm run build` war erfolgreich; die Testserver wurden anschließend beendet. Diese Prüfungen wurden bei der Dokumentationsarbeit am 6. November 2026 nicht wiederholt. Herkunft und Nachweisgrenzen stehen im Entwicklungsjournal.

## Vorbereitung in PowerShell

Alle Befehle gelten ab Projektwurzel, sofern nicht anders angegeben. Keine neue Umgebung ungefragt erstellen. Falls das vorhandene `.venv` fehlt oder anderswo liegt, zunächst den Pfad und die Zulässigkeit einer Installation klären.

```powershell
Set-Location C:\Users\CC-Student\PycharmProjects\Network-Monitor
Test-Path .\.venv\Scripts\python.exe
& .\.venv\Scripts\python.exe --version
node --version
npm --version
```

Erwartet werden `True` und Python `3.14.5`. Aktivierung und Änderung der ExecutionPolicy sind nicht erforderlich, da der Interpreter direkt aufgerufen wird.

## Abhängigkeiten

Die Abhängigkeiten des Grundgerüsts sind laut bisherigem Bericht installiert. Erneute Installationen und Erweiterungen benötigen gesonderte Benutzerfreigabe. Folgende Befehle dienen nur als Anleitung nach einer solchen Freigabe:

```powershell
& .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
& .\.venv\Scripts\python.exe -m pip check
Push-Location .\frontend
npm ci
Pop-Location
```

Die ursprüngliche Installation mit `npm install` erzeugte `frontend/package-lock.json`. Diese Datei ist in Git enthalten und ermöglicht reproduzierbare Folgeinstallationen mit `npm ci`.

## Backend starten

In einem eigenen PowerShell-Fenster:

```powershell
Set-Location C:\Users\CC-Student\PycharmProjects\Network-Monitor
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir .\backend --host 127.0.0.1 --port 8000 --reload
```

API: http://127.0.0.1:8000/api/health

Interaktive API-Dokumentation: http://127.0.0.1:8000/docs

## Frontend starten

In einem zweiten PowerShell-Fenster:

```powershell
Set-Location C:\Users\CC-Student\PycharmProjects\Network-Monitor\frontend
npm run dev
```

http://127.0.0.1:5173 öffnen. Vite leitet `/api` unter Beibehaltung des Pfades an `http://127.0.0.1:8000` weiter. Der Browser verwendet denselben Ursprung; zusätzliche CORS-Konfiguration ist derzeit nicht nötig. Der Proxy gilt für `npm run dev`; die Produktionsbereitstellung mit API ist noch nicht eingerichtet.

## Funktionsprüfung

Bei laufenden Servern in einem dritten PowerShell-Fenster:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:5173/api/health
```

Beide Anfragen sollen `status` mit dem Wert `ok` liefern. Die erste prüft FastAPI direkt, die zweite den Vite-Proxy. Die Oberfläche soll den Projektnamen und eine erfolgreiche Verbindung anzeigen. Ihre vorhandenen Meldungen sind russisch.

Backend mit Ctrl+C beenden und die Seite neu laden: Eine verständliche Verbindungsfehlermeldung soll erscheinen. Nach erneutem Backend-Start und Neuladen soll die Verbindung wieder als erfolgreich angezeigt werden.

Frontend-Build nach vorhandener oder genehmigter Installation:

```powershell
Set-Location C:\Users\CC-Student\PycharmProjects\Network-Monitor\frontend
npm run build
```

Jeden Server mit Ctrl+C im jeweiligen Fenster beenden. Automatisierte Modell- und Geräte-API-Tests sind vorhanden; Anleitung siehe unten.

## Struktur

```text
AGENTS.md                  # Dauerhafte Agentenregeln
docs/ROADMAP.md            # Etappen und nächster Schritt
docs/REQUIREMENTS.md       # Anforderungen und Architektur
docs/DEVLOG.md             # Entwicklung und Prüfnachweise
backend/
  app/__init__.py          # Python-Paket
  app/main.py              # FastAPI und Gesundheitsendpunkt
  requirements.txt        # Backend-Abhängigkeiten
frontend/
  index.html              # HTML-Einstiegspunkt
  package.json            # Abhängigkeiten und npm-Befehle
  package-lock.json       # Fixierte Abhängigkeitsauflösung
  vite.config.js          # React, Entwicklungsserver und API-Proxy
  src/main.jsx            # React-Einbindung
  src/App.jsx             # Überschrift und Backend-Verbindungsprüfung
  src/styles.css          # Grundlegende Darstellung
.gitignore                # Git-Ausschlüsse
README.md                 # Projektbeschreibung und Startanleitung
```

## Geräteverwaltung und Speicherung

`GET /api/devices` liefert eine nach `id` sortierte Liste; eine leere Datenbank liefert `[]`.

`POST /api/devices` akzeptiert beispielsweise `{"name":"Router","address":"192.0.2.1"}` und liefert `201` mit `id`, `name`, `address`, `status`, `latency_ms` und `last_checked_at`. Anfangswerte sind `unknown`, `null` und `null`. Ungültige Eingaben liefern `422`, doppelte normalisierte Adressen `409`.

Namen werden außen von Leerzeichen befreit und auf 1 bis 100 Zeichen begrenzt. IPv4, IPv6, Domänen einschließlich IDN und lokale einteilige Namen sind zulässig. IP-Adressen werden kanonisiert, Domänen kleingeschrieben und ein abschließender Punkt entfernt. Die Validierung führt keine DNS- oder anderen Netzwerkprüfungen aus.

Die Anwendung erstellt beim Start `backend/data/network_monitor.sqlite3`. Der Pfad hängt nicht vom Arbeitsverzeichnis ab; Daten bleiben nach einem Neustart erhalten. Datenbankdateien sind von Git ausgeschlossen. `create_all` erstellt fehlende Tabellen, migriert jedoch keine bestehende Struktur. Gespeicherte Adressen sind keine automatische Erlaubnis für spätere Netzwerkprüfungen.

Neue Module: `backend/app/database.py`, `models.py`, `schemas.py` und `routers/devices.py`. Die Anwendung bietet `create_app` zur isolierten Erstellung von Testinstanzen.

## Automatisierte Tests

SQLAlchemy ist in `backend/requirements.txt` enthalten. Testabhängigkeiten stehen in `backend/requirements-dev.txt`. Installation nur nach gesonderter Freigabe:

```powershell
& .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements-dev.txt
```

Ab Projektwurzel ausführen:

```powershell
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe -m pip check
```

Tests verwenden temporäre SQLite-Dateien und TestClient ohne externe Server. Sie prüfen Modellvorgaben, Persistenz zwischen Anwendungsinstanzen, Adressvalidierung, Duplikate einschließlich konkurrierender Anfragen sowie `/api/health`. Am 6. November 2026: 40 Tests erfolgreich, `pip check` ohne Konflikte. Starlette meldet eine Abkündigungswarnung zur Verwendung von httpx mit TestClient; ein Wechsel zu httpx2 wurde nicht durchgeführt.

## Geräteoberfläche verwenden

Nach dem Start von Backend und Frontend zeigt die Seite die gespeicherten Geräte. Über das Formular Name und IP-Adresse oder Domänenname eingeben und das Gerät hinzufügen. Die Liste aktualisiert sich nach dem Speichern automatisch. Die Schaltfläche zur Listenaktualisierung ermöglicht einen erneuten Abruf bei Verbindungsproblemen.

Fehlende Latenz und Prüfzeit werden als fehlende Daten angezeigt; neue Geräte haben den unbekannten Status. Doppelte Adressen und ungültige Eingaben erzeugen verständliche Meldungen, ohne die Eingabefelder zu leeren. Während des Speicherns ist das Formular gesperrt.

Zusätzliche Frontend-Dateien: `src/api/devices.js`, `src/api/devices.test.js`, `src/components/DeviceForm.jsx` und `src/components/DeviceList.jsx`.

API-Client-Tests ohne zusätzliche Pakete im Verzeichnis `frontend` ausführen:

```powershell
npm test
npm run build
```

Am 6. November 2026: neun API-Client-Tests und 40 Backend-Tests erfolgreich; Frontend-Build erfolgreich. Browserprüfung: leere Liste, Erstellung, Duplikat, ungültige Adresse, erneutes Laden sowie Verbindungsfehler und Wiederherstellung geprüft. Testgeräte wurden ausschließlich in `.pytest_cache/ui-stage3.sqlite3` gespeichert. Die Testserver wurden danach beendet. Eine gesonderte mobile Browserprüfung und automatisierte React-Komponententests wurden nicht durchgeführt.
