# Empfehlungen für das IT-Team

## Einordnung

Die Auswertung basiert auf Selbsteinschätzungen und ist daher als Orientierungsinstrument zu lesen, nicht als objektive Leistungsbewertung. Dennoch lassen sich daraus klare Management-Signale ableiten:

- Der Gesamtdurchschnitt des Teams liegt bei `3,36`.
- `8 von 12` Unterkategorien sind mindestens doppelt abgesichert.
- `4 von 12` Unterkategorien sind aktuell Flaschenhälse.
- Es gibt zwar keine Unterkategorie ganz ohne Expert:innen, aber mehrere Themen mit hoher Abhängigkeit von nur einer Person.

Die wichtigste Erkenntnis ist daher nicht ein genereller Kompetenzmangel, sondern eine **ungleich verteilte Abdeckung**: Einige Themen sind solide abgesichert, während kritische Netzwerk- und Authentifizierungsthemen stark an einzelnen Personen hängen.

## Management-Empfehlungen

### 1. Abhängigkeit von Person E gezielt reduzieren

Die höchste Priorität ist der Abbau von Wissensmonopolen. Aktuell liegen alle vier identifizierten Flaschenhälse bei Person `E`:

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

**Zielbild:**
Jedes betriebsrelevante Thema braucht mindestens zwei sicher arbeitsfähige Personen.

### 2. Netzwerk als erstes Entwicklungsfeld priorisieren

Das Kompetenzfeld `Netzwerk` ist im Team am schwächsten ausgeprägt:

- Durchschnitt: `3,13`
- Anteil schwacher Bewertungen: `37,9 %`
- Bus-Faktor: `1`

Besonders kritisch sind:

- `VPN` mit Durchschnitt `2,63` und `57,1 %` schwachen Bewertungen
- `Firewall & Routing` mit Durchschnitt `3,09`
- `Core-Switching` mit Durchschnitt `3,20`

Diese Themen sind infrastrukturell zentral. Hier sollte zuerst investiert werden, bevor weitere Optimierungen in bereits solideren Bereichen erfolgen.

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

### 3. Operative Einzelthemen mit besonders schwachen Werten direkt adressieren

Die schwächsten Einzelaussagen zeigen sehr konkret, wo die Unsicherheit im Team sitzt. Die kritischsten Punkte sind:

- Verständnis von `EduVPN` (`1,8`)
- `Shibboleth` pflegen und betreiben (`2,2`)
- Unterschied zwischen Routing-Protokollen wie `OSPF` oder `BGP` (`2,2`)
- Webserver-Hardening (`2,4`)
- VPN-Troubleshooting (`2,6`)
- VLAN-Konfiguration (`2,6`)

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

### 4. Starke Bereiche bewusst stabil halten, aber nicht überinvestieren

Nicht alle Themen sind kritisch. Solide bis starke Abdeckung zeigen zum Beispiel:

- `Lokale Dateien`
- `Datenbanken`
- `Virenscanner`
- Teile von `Servervirtualisierung`
- Teile von `Webserver`

**Empfehlung:**

- Diese Themen nicht priorisiert weiter ausbauen.
- Stattdessen als Quelle für interne Entlastung und Mentoring nutzen.
- Starke Personen aus stabilen Bereichen können begrenzt Kapazität für Wissenstransfer in kritischen Bereichen freimachen.

## Konkreter Maßnahmenplan für die nächsten 90 Tage

### Sofortmaßnahmen (0 bis 30 Tage)

- Für die vier Flaschenhälse je ein Thema-Owner und ein Thema-Backup festlegen.
- Mit Experten je Thema einen kompakten Wissenstransferplan aufsetzen.
- Die sechs schwächsten Einzelaussagen in ein Mini-Trainingsprogramm überführen.

### Kurzfristig (30 bis 60 Tage)

- Erste Praxisübergaben in `VPN`, `Firewall & Routing`, `Core-Switching` und `Authentifizierung` durchführen.

### Mittelfristig (60 bis 90 Tage)

- Erneute Selbsteinschätzung oder Review der betroffenen Themen.
- Erfolgskriterien prüfen:
  - Reduktion der Flaschenhälse von `4` auf höchstens `2`
  - zweite starke Person in mindestens zwei der vier kritischen Themen
  - sinkender Anteil schwacher Bewertungen im Feld `Netzwerk`

## Strategische Empfehlung

Im Moment **nicht** primär auf allgemeine Weiterbildung setzen, sondern auf **gezielten Redundanzaufbau in betriebsrelevanten Themen**.

Die richtige Stoßrichtung lautet:

1. Wissensmonopole abbauen
2. Netzwerkkompetenz verbreitern
3. schwächere Teammitglieder strukturiert entwickeln
4. stärkere Teammitglieder als Multiplikator:innen einsetzen

Wenn diese vier Punkte konsequent umgesetzt werden, steigt nicht nur das Kompetenzniveau, sondern vor allem die **Betriebssicherheit und Teamresilienz**.
