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

### Sprachtrennung und Lokalisierung

- Kommunikation mit dem Benutzer, Berichte und Erklärungen ausschließlich auf Russisch.
- Markdown-Dokumentation in `AGENTS.md`, `README.md` und `docs/*.md` ausschließlich auf Deutsch; Dateinamen auf Englisch.
- Benutzeroberfläche standardmäßig auf Englisch. Die Oberflächensprache ist unabhängig von der Kommunikations- und Dokumentationssprache.
- Eine i18n-Architektur mit separaten Übersetzungswörterbüchern vorsehen. Künftig Englisch (`en`), Deutsch (`de`) und Russisch (`ru`) unterstützen; keine russischen Zeichenketten direkt in React-Komponenten hinzufügen.
- Technische API-Werte, Variablennamen und Identifikatoren bleiben englisch und unverändert, insbesondere `unknown`, `online`, `offline` und Fehlercodes. Ihre sichtbaren Beschriftungen dürfen über Wörterbücher übersetzt werden.
- Oberflächentexte sind seit Etappe 5 im separaten englischen Wörterbuch `frontend/src/i18n/en.js` hinterlegt. `i18n/index.js` übernimmt Übersetzung, Parameterersetzung und Formatierung. Englisch ist Standard und Rückfallsprache; vollständige deutsche und russische Wörterbücher sowie eine Sprachauswahl sind seit Etappe 6 implementiert.

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

Etappen 1 bis 6 sind umgesetzt. Die bestätigte weitere Reihenfolge lautet: Etappe 4 ICMP Ping, Latenzmessung und Statusaktualisierung; Etappe 5 Fehlerbehandlung, Oberflächenverbesserungen und Tests; Etappe 6 Abschlussprüfung und Dokumentation. Etappe 4 wurde mit Beschränkung auf die Loopback-Adresse freigegeben und umgesetzt.

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

`last_checked_at` blieb in Etappe 2 `NULL`. Seit Etappe 4 werden Messzeitpunkte in SQLite als UTC ohne Zeitzonenmetadaten gespeichert und beim Lesen mit UTC-Zeitzone versehen; die API liefert einen expliziten UTC-Zeitpunkt. Bestehende DATETIME-Spalten bleiben kompatibel; kein Schemawechsel erforderlich. IPv6-Zonenkennungen, URLs, Ports, Pfade und rein numerische ungültige IP-Schreibweisen werden abgelehnt. Zusätzliche Eingabefelder werden mit `422` abgelehnt. Die Datenbank erzwingt die Eindeutigkeit des normalisierten Adresswerts; bei Konflikten erfolgt ein Rollback und die API liefert `409`. IDN-Konvertierung verwendet den Python-Codec `idna`.

## Anforderungen und Entscheidungen zu Etappe 3

- Geräte mit Name, Adresse, Status, Latenz und letztem Prüfzeitpunkt anzeigen. Fehlende Messwerte als fehlend kennzeichnen; keine Messungen simulieren.
- Formular mit Pflichtfeldern und Namenslänge bis 100 Zeichen; vollständige Adressvalidierung im Backend belassen.
- Nach erfolgreichem POST die Antwort sofort in die Liste übernehmen und den aktuellen Gesamtstand abrufen. Fehler beim anschließenden Abruf ändern den erfolgreichen Speichervorgang nicht.
- Eingaben bei Fehlern erhalten; Formular während des Speicherns sperren und parallele Übermittlung zusätzlich über eine Referenz verhindern.
- Abrufe beim erneuten Laden oder Verlassen der Anwendung abbrechen; veraltete Antworten nicht übernehmen.
- Ladezustand, leere Liste, Fehler und Wiederholungsmöglichkeit anzeigen. Bereits angezeigte Geräte bei einem Abruffehler erhalten.
- In Etappe 3 wurden russische Oberflächentexte umgesetzt; für die weitere Entwicklung gilt die oben festgelegte englische Standardsprache mit i18n. Zugeordnete Formularbeschriftungen, Statusmeldungen und sichtbare Tastaturfokussierung bleiben erforderlich; auf schmalen Bildschirmen einspaltiges Formular und horizontal verschiebbare Tabelle.
- Keine zusätzlichen Abhängigkeiten, keine Backend- oder Datenbankschemaänderung. Keine Netzwerkprüfungen der Geräte und kein periodischer Abruf.

## Etappe 4 – manuelle ICMP-Prüfung

### Freigabe und Sicherheit

- Ausschließlich `127.0.0.1` ist für reale Prüfungen erlaubt. Alle anderen IPv4-/IPv6-Adressen, Netze und Domänen einschließlich `localhost` werden mit `403` vor jedem Prozessstart abgelehnt. Keine DNS-Auflösung; deshalb ist der zuvor vorgeschlagene DNS-Zeitrahmen von zwei Sekunden derzeit nicht erforderlich.
- `allowed_target` prüft das Ziel im API und erneut im Ping-Adapter. Auch das feste PowerShell-Programm erlaubt ausschließlich diese Adresse. Keine vom Client übergebene Zieladresse oder Zeitüberschreitung im Prüf-Endpunkt.
- Windows-Adapter über den Systempfad aus `GetSystemDirectoryW`; PowerShell ohne Profil, nicht interaktiv und ohne Fenster. Fester UTF-16LE-kodierter Programmtext; Ziel als JSON über Standardeingabe, keine Einfügung in Befehlsquelltext, `shell=False`.
- Keine neuen Pakete, keine erweiterten Benutzerrechte und keine Änderung von ExecutionPolicy oder Firewall. Andere Betriebssysteme liefern eine klare Nichtverfügbarkeitsmeldung.

### Ausführung und Grenzen

- `POST /api/devices/{id}/check`: eine manuelle Einzelprüfung, keine periodische Überwachung und keine Sammelprüfung.
- Genau ein Echo Request über `.NET Ping.Send` mit 1000 ms Antwortwartezeit. `RoundtripTime` ist die Latenz; Prozessstartzeit wird nicht als Netzwerklatenz ausgegeben. Null Millisekunden sind gültig.
- Äußerer Prozesszeitrahmen fünf Sekunden über `subprocess.run(timeout=5)`; bei Überschreitung beendet und wartet Python auf den Kindprozess. Die Betriebssystemphase der Prozesserzeugung ist nicht auf allen Plattformen unterbrechbar; es handelt sich um einen Prozesswartezeitrahmen, keine harte Echtzeitgarantie für die gesamte HTTP-Anfrage.
- Höchstens zwei aktive Prüfungen je Backend-Prozess, keine Warteschlange, kein paralleler Lauf für dieselbe Geräte-ID, fünf Sekunden Mindestabstand zwischen Prüfstarts. Abbruch oder Fehler gibt den aktiven Platz frei. Abkühlzeiten werden beim Neustart zurückgesetzt.
- Diese Begrenzung setzt einen einzelnen Uvicorn-Prozess voraus. Mehrere Worker benötigen vor ihrer Einführung eine gemeinsame Begrenzung. Datenbanklesesitzung vor Ping schließen; erst danach eine kurze Schreibtransaktion öffnen.

### Zustände, Speicherung und Antworten

- Zustände ausschließlich `unknown`, `online`, `offline`; `up` und `down` werden nicht eingeführt.
- Erfolgreicher Echo Reply: `online`, gemessene Latenz, UTC-Abschlusszeit. ICMP-Timeout oder bestätigte Nichterreichbarkeit: `offline`, Latenz `NULL`, UTC-Abschlusszeit. `offline` ist keine Aussage über Stromversorgung oder Erreichbarkeit anderer Dienste.
- Technische Fehler, verbotene Ziele und Datenbankfehler überschreiben vorherige Messdaten nicht. Speicherung von Status, Latenz und Zeit erfolgt in einer Transaktion.
- `200`: durchgeführte Prüfung mit Gerät; `403`: verbotenes Ziel; `404`: fehlendes Gerät; `409`: laufende Prüfung oder zwischenzeitlich geändertes Gerät; `429`: Begrenzung mit `Retry-After: 5`; `503`: Plattform-, Werkzeug- oder Speicherfehler; `504`: äußerer Prozesszeitrahmen überschritten.
- Fehler liefern einen maschinenlesbaren Wert in `detail.code`; rohe Prozessdiagnosen werden nicht an den Browser weitergegeben.
- React zeigt eine manuelle Schaltfläche pro Gerät und sperrt sie während der Anfrage. Erfolg aktualisiert die Zeile, Fehler erhalten bisherige Daten. Veraltete Listenabrufe überschreiben das neue Messergebnis nicht.

## Gezielte Korrekturen nach der Codeprüfung

- Gerätenamen dürfen kein Nullzeichen (`U+0000`) enthalten. Die Eingabe wird unabhängig von der Zeichenposition vor dem Datenbankzugriff mit `422` abgelehnt; die übrigen Namensregeln bleiben erhalten.
- `device_id` im Prüf-Endpunkt ist auf `1` bis `9223372036854775807` begrenzt. Werte außerhalb dieses Bereichs liefern `422` vor Datenbank- oder Ping-Zugriff. Eine gültige, nicht vorhandene ID liefert weiterhin `404`.
- Beim Erstellen und beim Speichern von Prüfergebnissen erfolgt zunächst `flush`, danach wird eine eigenständige Antwort aus den geladenen Werten aufgebaut. Erst nach erfolgreichem `commit` wird diese zurückgegeben. Nach dem Commit sind weder `refresh` noch erneutes Laden abgelaufener ORM-Attribute für die Antwort erforderlich. Ein fehlgeschlagener Lesezugriff nach erfolgreicher Speicherung kann dadurch keine irreführende Fehlermeldung mehr auslösen.

## Etappe 5 – Fehlerbehandlung und Oberfläche

- Einheitliche maschinenlesbare Codes für Duplikate und Datenbankfehler; `422` behält die FastAPI-Feldinformationen in `detail`. SQLAlchemy-Fehler in Geräteabruf und Erstellung liefern `503` ohne interne Diagnosen. `/api/health` bleibt unverändert.
- API-Client begrenzt Anfragen einschließlich Antwortinhalt auf zehn Sekunden über AbortSignal. Nach einer Zeitüberschreitung kann ein Schreibvorgang bereits erfolgt sein; die Meldung fordert zur Listenaktualisierung auf. Keine automatischen Wiederholungen schreibender Anfragen.
- Feldfehler werden bei Name und Adresse angezeigt und mit `aria-describedby` verknüpft; Eingaben bleiben bei Fehlern erhalten. Ungültige erfolgreiche Geräteantworten werden vor der Anzeige abgelehnt.
- `Retry-After` wird als Sekundenwert oder HTTP-Datum ausgewertet; die Prüfschaltfläche zeigt eine Abkühlzeit. Nach erfolgreicher Prüfung wird vorsichtig fünf Sekunden gewartet. Die Backend-Begrenzung bleibt maßgeblich.
- Nicht freigegebene Ziele haben eine deaktivierte Prüfschaltfläche samt Erklärung. Die serverseitige Sicherheitsprüfung bleibt unverändert. Statuswerte haben unterschiedliche Farben und weiterhin Textbeschriftungen.
- Die Listenaktualisierung prüft auch die Backend-Verbindung erneut. Bereits angezeigte Daten bleiben bei Abruffehlern erhalten; nach erfolgreicher Geräteprüfung wird der aktuelle Gesamtstand erneut geladen.
- Formulare passen sich schmalen Bildschirmen an; die Tabelle ist horizontal verschiebbar und per Tastatur fokussierbar. Seit Etappe 6 verwenden Datum, Zahlen und HTML-Sprachattribut die aktive Sprache `en`, `de` oder `ru`.
- Keine neuen Abhängigkeiten. Frontend-Tests verwenden den vorhandenen Node-Testläufer, Vite zum Laden von JSX und React zur statischen Komponentenausgabe. Dies ersetzt keine automatisierten interaktiven Browsertests.


## Vereinbarte Erweiterung von Etappe 6

- Die erste Version soll vollständige Oberflächentexte für Englisch, Deutsch und Russisch in getrennten Wörterbüchern enthalten.
- Eine sichtbare Sprachauswahl anbieten und die manuelle Wahl im Browser speichern. Bei nicht verfügbarem Browserspeicher muss die Anwendung weiterhin bedienbar bleiben.
- Sprachpriorität: gespeicherte unterstützte Benutzerwahl vor unterstützter Browsersprache, andernfalls Englisch. Regionale Varianten wie `de-DE` und `ru-RU` den passenden Sprachen zuordnen. Die Betriebssystemsprache wird nicht direkt ausgewertet.
- Oberflächentexte einschließlich bereits sichtbarer Fehlermeldungen sowie Datum, Zahlen und HTML-Sprachattribut passend zur aktiven Sprache aktualisieren. Geräteeingaben und Messergebnisse beim Wechsel erhalten.
- Technische API-Werte, Fehlercodes und Identifikatoren nicht übersetzen. Russische Übersetzungen ausschließlich im separaten Wörterbuch ablegen, nicht in React-Komponenten.
- Alle drei Sprachen, Rückfall, Speicherung und Sprachwechsel automatisiert und im Browser prüfen, bevor die Abschlussprüfung und Dokumentation fertiggestellt werden.

Status: Umfang vom Benutzer bestätigt und vollständig implementiert; automatische Tests und Browserprüfung erfolgreich. Die ICMP-Freigabe bleibt ausschließlich auf `127.0.0.1` beschränkt.


## Abschließende Implementierungsentscheidungen

- `useSyncExternalStore` verbindet den Sprachzustand mit React. Der Sprachwechsel benötigt weder Seitenneuladen noch erneute API-Anfragen und lässt Formular- und Gerätedaten erhalten.
- Manuelle Auswahl wird unter `network-monitor-language` in localStorage gespeichert. Fehlender oder gesperrter Speicher verhindert die Bedienung nicht; nach Neuladen wird dann erneut die Browsersprache berücksichtigt.
- Fehlerzustände enthalten technische Codes und Feldschlüssel, Erfolgsmeldungen den Gerätenamen. Übersetzung erfolgt bei der Darstellung, sodass sichtbare Meldungen sofort die Sprache wechseln.
- Die getrennten Wörterbücher `en.js`, `de.js` und `ru.js` besitzen dieselben Schlüssel und Platzhalter. Fehlende Übersetzungen fallen auf Englisch zurück. Russische Texte stehen ausschließlich im russischen Wörterbuch; Eigennamen der Sprachen in anderen Wörterbüchern sind technisch als Unicode-Escapes hinterlegt.
- Die erste Version ist als lokale Entwicklungsanwendung mit einem Backend-Prozess geprüft. Produktionsbereitstellung, Mehrprozessbegrenzung und automatische Überwachung gehören nicht zur Abnahme dieser Version.
