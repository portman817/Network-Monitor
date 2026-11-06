# Regeln für KI-Agenten

## Sprache

- Mit dem Benutzer ausschließlich auf Russisch kommunizieren. Dies gilt für Pläne, Rückfragen, Berichte, Erklärungen, Warnungen und Fehlermeldungen.
- Markdown-Dateinamen auf Englisch und sämtliche Dokumentationsinhalte auf Deutsch schreiben, einschließlich Überschriften, Tabellen, Checklisten und Statusangaben.
- Technische Bezeichner, Quellcode, Befehle, Pfade sowie Klassen- und Funktionsnamen unverändert lassen.
- Die Benutzeroberfläche verwendet standardmäßig Englisch. Kommunikationssprache, Dokumentationssprache und Oberflächensprache strikt voneinander trennen.
- Keine russischen Texte direkt in React-Komponenten einfügen. Oberflächentexte über eine Lokalisierungsarchitektur (i18n) mit getrennten Übersetzungswörterbüchern vorsehen; Englisch (`en`), Deutsch (`de`) und Russisch (`ru`) unterstützen. Gespeicherte Sprachwahl hat Vorrang vor unterstützter Browsersprache; Englisch bleibt Rückfallsprache.
- Technische API-Werte, Variablennamen und Identifikatoren bleiben englisch und werden nicht übersetzt. Nur ihre sichtbaren Beschriftungen werden lokalisiert.

## Vor jeder neuen Aufgabe

1. `AGENTS.md`, `README.md` und alle Dokumente in `docs/` lesen.
2. Projektstruktur, relevante Quelldateien und tatsächlichen Git-Status prüfen.
3. Bereits implementierte Funktionen von geplanten oder unbestätigten Entscheidungen unterscheiden.

## Arbeitsregeln

- Nur innerhalb des freigegebenen Aufgabenbereichs arbeiten; bei Analyseaufträgen keine Dateien ändern.
- Ohne ausdrückliche Benutzerfreigabe weder `git commit` noch `git push` ausführen.
- Abhängigkeiten nur nach gesonderter Freigabe installieren; das vorhandene `.venv` verwenden.
- Benutzeränderungen erhalten und bestehende Dokumente nicht löschen.
- Keine erfundenen Testergebnisse, Build-Ergebnisse, Daten oder Commit-Hashes dokumentieren. Frühere Berichte als solche kennzeichnen; unbekannte Angaben ausdrücklich benennen.
- Nach relevanten Änderungen die betroffenen Dokumente innerhalb derselben Aufgabe aktualisieren. Erledigte Punkte erst nach tatsächlicher Umsetzung abhaken.

## Dokumentationsaufgaben

- `README.md`: Projektbeschreibung, Voraussetzungen, Startanleitung und aktueller Funktionsumfang.
- `docs/ROADMAP.md`: Etappen, Checklisten, Status und nächster Schritt.
- `docs/REQUIREMENTS.md`: Anforderungen, Architektur, Grenzen und bestätigte Entscheidungen.
- `docs/DEVLOG.md`: datierte Änderungen, tatsächlich ausgeführte Prüfungen, Ergebnisse und offene Punkte; historische Angaben mit Herkunft kennzeichnen.
- Vorschläge nicht als genehmigte Entscheidungen darstellen und fehlende Planung nicht erfinden.

## Aktuelle Grenzen

- Etappen 1 bis 6 sind umgesetzt. Die Reihenfolge der Etappen 4 bis 6 ist in `docs/ROADMAP.md` bestätigt. Weitere Etappen benötigen eine neue Aufgabenfreigabe; zusätzliche Installationen bleiben gesondert genehmigungspflichtig.
- `GET /api/health` mit `{"status":"ok"}` unverändert erhalten.
- Etappe 2 umfasst SQLite-Gerätespeicherung und Geräte-API, jedoch kein Ping, keine automatische Überwachung und keine neuen React-Komponenten.
- Zukünftige Netzwerkprüfungen auf erlaubte Adressen beschränken. Ein gespeicherter Geräteeintrag allein bedeutet keine Prüferlaubnis.

- Für reale ICMP-Prüfungen ist derzeit ausschließlich `127.0.0.1` freigegeben. Alle anderen Adressen, Netze und Domänen sind verboten; die Freigabe darf nicht ohne Benutzerauftrag erweitert werden. Zustände: `unknown`, `online`, `offline`.
