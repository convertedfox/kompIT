# Empfehlungen für das IT-Team

## Einordnung

Die Auswertung basiert auf Selbsteinschätzungen und ist daher als Orientierungsinstrument zu lesen, nicht als objektive Leistungsbewertung. Für Management-Entscheidungen ist sie trotzdem belastbar genug, um operative Risiken und Entwicklungsprioritäten sichtbar zu machen.

- Der Gesamtdurchschnitt des Teams liegt aktuell bei `3,23`.
- `8 von 12` Unterkategorien sind mindestens doppelt abgesichert.
- `4 von 12` Unterkategorien sind weiterhin Flaschenhälse.
- Es gibt auf Ebene der Unterkategorien keine Themen ohne Expert:innen, aber mehrere kritische Themen hängen weiterhin operativ an nur einer Person.

Die wichtigste Erkenntnis bleibt daher bestehen: Das Hauptproblem ist kein genereller Kompetenzmangel, sondern eine **ungleich verteilte Abdeckung**. Mit dem neuen Mitarbeitenden `F` ist das Team breiter geworden, aber die betriebsrelevanten Netzwerk- und Authentifizierungsthemen hängen weiterhin stark an Person `E`.

Gleichzeitig ist wichtig, zwei Dinge sauber zu trennen:

- Die neu niedrigeren Durchschnittswerte sind teilweise ein normaler Effekt des Onboardings von `F`.
- Die strukturellen Redundanzrisiken bestanden bereits vorher und sind weiterhin die eigentliche Management-Aufgabe.

## Management-Empfehlungen

### 1. Abhängigkeit von Person E gezielt reduzieren

Die höchste Priorität bleibt der Abbau von Wissensmonopolen. Alle vier identifizierten Flaschenhälse liegen weiterhin bei Person `E`:

- `VPN`
- `Firewall & Routing`
- `Core-Switching`
- `Authentifizierung`

Das ist operativ riskant, weil Ausfall, Wechsel oder Überlastung einer Person direkt die Handlungsfähigkeit in sicherheits- und betriebsrelevanten Themen senkt.

**Empfehlung:**

- Für jedes dieser vier Themen innerhalb der nächsten 8 bis 12 Wochen mindestens eine zweite arbeitsfähige Person auf Niveau `4` entwickeln.
- Person `E` nicht primär als Einzelbearbeiter:in einsetzen, sondern als Multiplikator:in.
- Wissenstransfer verbindlich strukturieren:
  - Shadowing im Tagesgeschäft
  - kurze Runbooks und Checklisten
  - gemeinsame Störungsbearbeitung
  - Abschluss mit praktischer Übergabe statt nur Dokumentation

**Konkrete Backup-Pfade:**

- `A` ist der naheliegendste erste Backup-Kandidat für `VPN`, `Firewall & Routing` und `Core-Switching`.
- In `Authentifizierung` sind `A` und `D` die plausibelsten Entwicklungspfade.
- `B` und `F` sollten kurzfristig nicht als primäre Entlastung für diese vier Flaschenhälse geplant werden.

**Zielbild:**
Jedes betriebsrelevante Thema braucht mindestens zwei sicher arbeitsfähige Personen.

### 2. Netzwerk bleibt das erste Entwicklungsfeld

Das Kompetenzfeld `Netzwerk` ist im Team weiterhin am schwächsten ausgeprägt und hat sich mit dem aktuellen Datenstand eher verschärft:

- Durchschnitt: `3,00`
- Anteil schwacher Bewertungen: `41,4 %`
- Bus-Faktor: `1`

Besonders kritisch sind:

- `VPN` mit Durchschnitt `2,52` und `61,9 %` schwachen Bewertungen
- `Firewall & Routing` mit Durchschnitt `2,93`
- `Core-Switching` mit Durchschnitt `3,00`

Diese Themen sind infrastrukturell zentral. Hier sollte zuerst investiert werden, bevor weitere Optimierungen in bereits robuster abgesicherten Bereichen erfolgen.

**Empfehlung:**

- Ein fokussiertes Netzwerk-Befähigungsprogramm für 2 bis 3 Personen aufsetzen.
- Prioritätsreihenfolge:
  1. VPN
  2. Firewall & Routing
  3. Core-Switching
- Inhalte nicht breit, sondern betriebsnah trainieren:
  - typische Changes
  - Troubleshooting
  - Zertifikate
  - Routing-Grundlagen
  - sichere Standardkonfigurationen

### 3. Kritische Einzelaussagen in operative Lernmodule übersetzen

Die schwächsten Einzelaussagen zeigen sehr konkret, wo die Unsicherheit im Team sitzt. Die aktuell kritischsten Punkte sind:

- Verständnis von `EduVPN` (`1,67`)
- `Shibboleth` pflegen und betreiben (`2,00`)
- Unterschied zwischen Routing-Protokollen wie `OSPF` oder `BGP` (`2,00`)
- Webserver-Hardening (`2,17`)
- Zertifikate im VPN-Umfeld verwalten (`2,33`)
- VPN-Troubleshooting (`2,50`)
- Switchports sicher konfigurieren (`2,50`)
- VLAN-Konfiguration (`2,67`)

Besonders relevant: Beim Thema `OSPF/BGP` gibt es auf Aussageebene aktuell keine Expert:innen. Das heißt: Die Unterkategorie `Firewall & Routing` ist formal nicht unbesetzt, aber ein konkreter kritischer Baustein ist trotzdem nicht resilient abgedeckt.

**Empfehlung:**

- Diese Themen in kleine, kurze Lernmodule übersetzen.
- Keine langen Schulungsblöcke, sondern:
  - 60- bis 90-Minuten-Sessions
  - konkreter Praxisbezug
  - sofortige Anwendung an realen Beispielen
- Für jedes Thema definieren:
  - Was muss man verstehen?
  - Was muss man selbstständig durchführen können?
  - Woran erkennt man, dass die Person arbeitsfähig ist?

### 4. Webserver nicht mehr als stabilen Bereich behandeln

`Webserver` würde ich nicht mehr als unkritischen oder stabilen Bereich einordnen:

- Durchschnitt: `2,89`
- Anteil schwacher Bewertungen: `50,0 %`

Besonders schwach sind:

- Webserver-Hardening (`2,17`)
- Backup- und Patchmanagement (`2,50`)
- Monitoring und Logging (`2,67`)

Das ist kein Primärrisiko auf dem Niveau von `VPN`, aber aus Betriebs- und Security-Sicht zu relevant, um es nur mitlaufen zu lassen.

**Empfehlung:**

- `Webserver` als sekundäres Entwicklungsfeld aufnehmen.
- Nicht parallel zu allen anderen Themen ausrollen, aber gezielt nach dem Netzwerk-Track adressieren.
- Fokus auf sichere Standardbetriebsfähigkeit:
  - Hardening-Baselines
  - Logging/Monitoring
  - Backup- und Patch-Routinen

### 5. Entwicklung nach Mitarbeitendenprofil differenzieren

Ein einheitlicher Trainingsansatz wäre ineffizient. Die Daten sprechen für unterschiedliche Entwicklungslogiken:

- `A`: schnellster Hebel für Redundanzaufbau in kritischen Themen
- `D`: sinnvoll für punktuelle Vertiefung, vor allem in `Authentifizierung`
- `C`: breiter mitnehmen, aber nicht als erster Hebel für die kritischsten Themen priorisieren
- `B`: klarer Stabilisierungskandidat, noch kein realistisch kurzfristiger Backup-Hebel
- `F`: Onboarding-Fall, zunächst Grundlagenaufbau statt Spezialisierung

**Einordnung von B:**

- `B` hat aktuell den niedrigsten Gesamtscore im Team (`2,05`).
- Besonders schwach ist `Netzwerk` mit Durchschnitt `1,66`.
- Stabiler sind `Datenbanken` und `Skripte` mit jeweils `3,00`.

Für `B` ist daher kurzfristig nicht der Aufbau von Spezialwissen in Flaschenhals-Themen sinnvoll, sondern zuerst der Schritt von "unsicher" zu "zuverlässig im Standardbetrieb".

**Einordnung von F:**

- `F` liegt aktuell bei einem Gesamtscore von `2,58`.
- Das ist im Kontext eines neuen Mitarbeitenden eher als normaler Ramp-up-Stand zu lesen als als alarmierendes Signal.

Für `F` sollte das Ziel zunächst breiter Grundlagenaufbau sein, nicht die kurzfristige Übernahme von Spezial- oder Single-Point-of-Failure-Themen.

### 6. Starke Bereiche bewusst stabil halten und gezielt nutzen

Nicht alle Themen sind kritisch. Solide bis starke Abdeckung zeigen weiterhin zum Beispiel:

- `Lokale Dateien`
- `Virenscanner`
- `Datenbanken`
- `Servervirtualisierung`

**Empfehlung:**

- Diese Themen nicht priorisiert weiter ausbauen.
- Stattdessen als Quelle für interne Entlastung und Mentoring nutzen.
- Starke Personen aus stabileren Bereichen können begrenzt Kapazität für Wissenstransfer in kritischen Themen freimachen.

## Konkreter Maßnahmenplan für die nächsten 90 Tage

### Sofortmaßnahmen (0 bis 30 Tage)

- Für die vier Flaschenhälse je ein Thema-Owner und ein Thema-Backup festlegen.
- `E` je Thema als Expert:in und Multiplikator:in definieren.
- Für `VPN`, `Firewall & Routing` und `Core-Switching` primär `A` als Backup-Ziel benennen.
- Für `Authentifizierung` `A` und `D` als Entwicklungspfade festlegen.
- Die schwächsten Einzelaussagen in ein Mini-Trainingsprogramm überführen.
- Für `B` und `F` einen separaten Basisentwicklungsplan aufsetzen statt sie direkt in alle Spezialthemen zu ziehen.

### Kurzfristig (30 bis 60 Tage)

- Erste Praxisübergaben in `VPN`, `Firewall & Routing`, `Core-Switching` und `Authentifizierung` durchführen.
- Kleine Lernmodule zu `EduVPN`, `Shibboleth`, `Routing-Protokollen`, `VPN-Zertifikaten` und `Webserver-Hardening` umsetzen.
- Für `B` und `F` sichere Standardfälle definieren, die eigenständig übernommen werden können.

### Mittelfristig (60 bis 90 Tage)

- Erneute Selbsteinschätzung oder Review der betroffenen Themen durchführen.
- Erfolgskriterien prüfen:
  - Reduktion der Flaschenhälse von `4` auf höchstens `2`
  - zweite starke Person in mindestens zwei der vier kritischen Themen
  - sinkender Anteil schwacher Bewertungen im Feld `Netzwerk`
  - belastbare Grundfähigkeiten bei `B` und `F` in Standardthemen

## Strategische Empfehlung

Im Moment **nicht** primär auf allgemeine Weiterbildung setzen, sondern auf **gezielten Redundanzaufbau in betriebsrelevanten Themen** und einen zweiten, getrennten Entwicklungsstrang für weniger erfahrene Mitarbeitende.

Die richtige Stoßrichtung lautet:

1. Wissensmonopole abbauen
2. Netzwerkkompetenz verbreitern
3. `A` und punktuell `D` als Redundanzhebel nutzen
4. `B` und `F` systematisch in sichere Standardbetriebsfähigkeit entwickeln
5. `Webserver` als sekundäres Risiko aktiv mitbearbeiten

Wenn diese Punkte konsequent umgesetzt werden, steigt nicht nur das Kompetenzniveau, sondern vor allem die **Betriebssicherheit, Teamresilienz und Umsetzungsfähigkeit im Tagesgeschäft**.
