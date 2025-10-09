# GraphQL API Anleitung für LLM-Agents: Event-Management System

## Einführung

Dieses Dokument erklärt, wie ein LLM-Agent über die GraphQL-Schnittstelle Schwimm-Events (Open Water Swimming Events) im System abfragen und bearbeiten kann.

## Datenmodell-Struktur

Das System verwendet ein hierarchisches Datenmodell mit vier Hauptentitäten:

```
Event (Haupt-Entität)
├── Location (ForeignKey, CASCADE)
├── Organizer (ForeignKey, SET_NULL)
└── Race[] (One-to-Many, CASCADE)
```

### 1. Event (Hauptentität)

Ein **Event** repräsentiert eine Schwimmveranstaltung und ist die zentrale Entität im System.

#### Pflichtfelder:
- `name` (String, max 100 Zeichen) - Name der Veranstaltung
- `date_start` (Date) - Startdatum der Veranstaltung
- `date_end` (Date) - Enddatum der Veranstaltung

#### Wichtige optionale Felder:
- `website` (URL, max 200 Zeichen) - Website der Veranstaltung
- `slug` (String, max 100 Zeichen) - URL-freundlicher Identifier
- `flyer_image` (ImageField) - Flyer oder Poster mit Event-Details
- `location` (ForeignKey zu Location) - Ort der Veranstaltung (CASCADE-Delete)
- `organizer` (ForeignKey zu Organizer) - Veranstalter (SET_NULL bei Löschung)
- `description` (Text, max 2048 Zeichen) - Öffentliche Beschreibung
- `internal_comment` (Text, max 2048 Zeichen) - Interne Notizen (nicht öffentlich)
- `water_temp` (Float) - Wassertemperatur in °C

#### Status-Felder:
- `needs_medical_certificate` (Boolean) - Ärztliches Attest erforderlich
- `needs_license` (Boolean) - Lizenz erforderlich
- `sold_out` (Boolean) - Ausverkauft
- `cancelled` (Boolean) - Abgesagt
- `invisible` (Boolean) - Versteckt vor der Öffentlichkeit
- `with_ranking` (Boolean) - Mit Rangliste

#### Qualität & Verifizierung:
- `entry_quality` (String) - "incomplete" oder "complete"
- `verified_at` (DateTime) - Zeitstempel der Admin-Verifizierung (NULL = nicht verifiziert)
- `source` (String, max 200 Zeichen) - Herkunft der Daten

#### Metadaten:
- `created_by` (ForeignKey zu User) - Ersteller
- `created_at` (DateTime) - Erstellungszeitpunkt
- `edited_by` (ForeignKey zu User) - Letzter Bearbeiter
- `edited_at` (DateTime) - Zeitpunkt der letzten Bearbeitung
- `previous_year_event` (ForeignKey zu Event) - Verlinkung zum Event des Vorjahres

#### Beziehungen:
- **1:N zu Race** - Ein Event kann mehrere Rennen (Races) haben
- **N:1 zu Location** - Jedes Event gehört zu einer Location
- **N:1 zu Organizer** - Jedes Event kann einem Organizer zugeordnet sein

### 2. Race (Rennen innerhalb eines Events)

Ein **Race** repräsentiert ein einzelnes Rennen bei einer Veranstaltung. Ein Event kann mehrere Races haben (z.B. 1km, 5km, 10km).

#### Pflichtfelder:
- `event` (ForeignKey zu Event) - Zugehöriges Event (CASCADE-Delete)
- `date` (Date) - Datum des Rennens (in lokaler Zeit)
- `distance` (Float) - Distanz in Kilometern

#### Wichtige optionale Felder:
- `race_time` (Time) - Startzeit des Rennens (in lokaler Zeit)
- `name` (String, max 50 Zeichen) - Name des Rennens
- `coordinates` (Array of [lat, lng] pairs) - GPS-Koordinaten der Strecke
- `wetsuit` (String) - Neopren-Regelung:
  - `"compulsory"` - Pflicht
  - `"optional"` - Optional
  - `"prohibited"` - Verboten
- `price_value` (Decimal) - Preis als Betrag
- `price_currency` (String) - Währung (ISO-Code wie EUR, USD, CHF)

#### Sortierung:
Races werden automatisch sortiert nach: `date` → `race_time` → `distance`

### 3. Location (Veranstaltungsort)

Eine **Location** repräsentiert einen physischen Ort, an dem Schwimm-Events stattfinden.

#### Pflichtfelder:
- `city` (String, max 50 Zeichen) - Stadt
- `country` (CountryField) - Land (ISO-Code)

#### Wichtige optionale Felder:
- `water_name` (String, max 50 Zeichen) - Name des Gewässers
- `water_type` (String) - Gewässer-Typ:
  - `"river"` - Fluss
  - `"sea"` - Meer
  - `"lake"` - See
  - `"pool"` - Schwimmbad
- `lat` (Float) - Breitengrad
- `lng` (Float) - Längengrad
- `address` (AddressField, max 200 Zeichen) - Vollständige Adresse
- `header_photo` (ImageField) - Header-Foto des Ortes
- `average_rating` (Float) - Durchschnittsbewertung aller Events an diesem Ort
- `verified_at` (DateTime) - Zeitstempel der Admin-Verifizierung

#### Beziehungen:
- **1:N zu Event** - Eine Location kann mehrere Events hosten

### 4. Organizer (Veranstalter)

Ein **Organizer** repräsentiert eine Organisation oder Person, die Events veranstaltet.

#### Pflichtfelder:
- `name` (String, max 100 Zeichen) - Name des Veranstalters
- `website` (URL, max 200 Zeichen) - Website des Veranstalters

#### Wichtige optionale Felder:
- `logo` (ImageField) - Logo des Veranstalters
- `slug` (String, max 100 Zeichen) - URL-freundlicher Identifier (auto-generiert)
- `internal_comment` (Text, max 10000 Zeichen) - Interne Notizen (nicht öffentlich)
- `contact_email` (Email, max 200 Zeichen) - Kontakt-E-Mail
- `contact_form_url` (URL, max 200 Zeichen) - Link zum Kontaktformular
- `contact_status` (String) - Status der Kontaktaufnahme:
  - `"pending"` - Ausstehend
  - `"contacted"` - Kontaktiert
  - `"responded"` - Antwort erhalten
  - `"completed"` - Abgeschlossen
  - `"failed"` - Fehlgeschlagen
  - `"needs_review"` - Überprüfung erforderlich
- `last_contact_attempt` (DateTime) - Zeitpunkt des letzten Kontaktversuchs
- `contact_notes` (Text, max 1000 Zeichen) - Notizen zur Kontaktaufnahme

#### Beziehungen:
- **1:N zu Event** - Ein Organizer kann mehrere Events veranstalten

## GraphQL-Abfragen (Queries)

### Events abfragen

#### Alle Events abrufen

```graphql
query {
  allEvents {
    edges {
      node {
        id
        name
        dateStart
        dateEnd
        website
        description
        location {
          id
          city
          waterName
          country
        }
        organizer {
          id
          name
        }
        races {
          edges {
            node {
              id
              distance
              date
              raceTime
              priceValue
              priceCurrency
            }
          }
        }
      }
    }
  }
}
```

#### Einzelnes Event nach ID abrufen

```graphql
query {
  event(id: "RXZlbnROb2RlOjE=") {
    id
    name
    dateStart
    dateEnd
    website
    description
    waterTemp
    needsMedicalCertificate
    needsLicense
    soldOut
    cancelled
    invisible
    withRanking
    entryQuality
    verifiedAt
    location {
      id
      city
      waterName
      waterType
      country
      lat
      lng
    }
    organizer {
      id
      name
      website
    }
    races {
      edges {
        node {
          id
          distance
          date
          raceTime
          name
          wetsuit
          priceValue
          priceCurrency
          coordinates
        }
      }
    }
  }
}
```

#### Events filtern

Die GraphQL-API unterstützt verschiedene Filter:

```graphql
query {
  # Nach Name filtern (exakt oder enthält)
  allEvents(nameIcontains: "Zurich") {
    edges {
      node {
        id
        name
      }
    }
  }

  # Nach Land filtern (über location__country)
  allEvents(locationCountry: "CH") {
    edges {
      node {
        id
        name
        location {
          city
          country
        }
      }
    }
  }

  # Nach Datum filtern (Events ab bestimmtem Datum)
  allEvents(dateFrom: "2025-06-01") {
    edges {
      node {
        id
        name
        dateStart
      }
    }
  }

  # Nach Datum filtern (Events bis bestimmtem Datum)
  allEvents(dateTo: "2025-12-31") {
    edges {
      node {
        id
        name
        dateEnd
      }
    }
  }

  # Kombinierte Filter
  allEvents(
    locationCountry: "CH",
    dateFrom: "2025-06-01",
    dateTo: "2025-12-31"
  ) {
    edges {
      node {
        id
        name
        dateStart
        dateEnd
        location {
          city
        }
      }
    }
  }

  # Nach Race-Distanz filtern
  allEvents(
    raceDistanceGte: 5.0,
    raceDistanceLte: 10.0
  ) {
    edges {
      node {
        id
        name
        races {
          edges {
            node {
              distance
            }
          }
        }
      }
    }
  }
}
```

**Verfügbare Filter für Events:**
- `name` - Exakte Übereinstimmung
- `nameIcontains` - Name enthält (case-insensitive)
- `website` - Exakte Website-URL
- `location` - Exakte Location ID
- `locationCountry` - Ländercode über `location__country` (z.B. "CH", "DE")
- `locationCity` - Exakte Stadt über `location__city`
- `locationCityIcontains` - Stadt enthält über `location__city__icontains`
- `dateFrom` - Events die an oder nach diesem Datum starten (`date_start >= dateFrom`)
- `dateTo` - Events die an oder vor diesem Datum enden (`date_end <= dateTo`)
- `raceDistanceGte` - Events mit Races >= dieser Distanz
- `raceDistanceLte` - Events mit Races <= dieser Distanz
- `slug` - Exakter Slug
- `races` - Exakte Race ID

**Wichtig:**
- Datums-Filter verwenden `dateFrom` und `dateTo` (nicht `dateStartGte`/`dateEndLte`)
- `dateFrom` filtert nach `date_start >= dateFrom`
- `dateTo` filtert nach `date_end <= dateTo`

### Locations abfragen

```graphql
query {
  allLocations {
    edges {
      node {
        id
        city
        waterName
        waterType
        country
        lat
        lng
        address
        averageRating
        verifiedAt
        events {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    }
  }
}
```

### Organizers abfragen

```graphql
query {
  allOrganizers {
    edges {
      node {
        id
        name
        website
        slug
        numberOfEvents
        events {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    }
  }

  # Nur Organizers mit mehr als X Events
  allOrganizers(numberOfEventsGt: 5) {
    edges {
      node {
        id
        name
      }
    }
  }
}
```

**Wichtig:** Die Felder `contactEmail`, `contactStatus`, `contactNotes` sind NICHT im GraphQL-Schema exponiert (nur intern im Admin-Interface verfügbar).

### Races abfragen

```graphql
query {
  race(id: "UmFjZU5vZGU6MQ==") {
    id
    date
    raceTime
    distance
    name
    wetsuit
    priceValue
    priceCurrency
    coordinates
    event {
      id
      name
    }
  }
}
```

## GraphQL-Mutationen (Änderungen)

### Event Mutationen

#### Event erstellen

```graphql
mutation {
  createEvent(input: {
    name: "Zurich Lake Swim 2025",
    dateStart: "2025-07-15",
    dateEnd: "2025-07-15",
    website: "https://zurichlakeswim.com",
    description: "Annual open water swimming event",
    locationId: "TG9jYXRpb25Ob2RlOjE=",
    organizerId: "T3JnYW5pemVyTm9kZTox",
    waterTemp: 20.5,
    needsMedicalCertificate: false,
    soldOut: false
  }) {
    event {
      id
      name
      dateStart
      dateEnd
      location {
        city
      }
      organizer {
        name
      }
    }
  }
}
```

#### Event aktualisieren

```graphql
mutation {
  updateEvent(input: {
    id: "RXZlbnROb2RlOjEyMw==",
    name: "Zurich Lake Swim 2025 - Updated",
    soldOut: true,
    waterTemp: 21.0,
    description: "Updated description"
  }) {
    event {
      id
      name
      soldOut
      waterTemp
    }
  }
}
```

**Verfügbare Felder für updateEvent:**
- Basis: `name`, `website`, `slug`, `description`, `internal_comment`
- Daten: `dateStart`, `dateEnd`, `waterTemp`
- Status: `needsMedicalCertificate`, `needsLicense`, `soldOut`, `cancelled`, `invisible`, `withRanking`
- Qualität: `entryQuality`, `source`
- Beziehungen: `locationId`, `organizerId`, `previousYearEventId`

#### Event löschen

```graphql
mutation {
  deleteEvent(input: {
    id: "RXZlbnROb2RlOjEyMw=="
  }) {
    success
    deletedId
  }
}
```

**⚠️ Warnung:** Löscht CASCADE alle zugehörigen Races! Erfordert Login.

### Location Mutationen

#### Location erstellen

```graphql
mutation {
  createLocation(input: {
    city: "Zurich",
    country: "CH",
    waterName: "Lake Zurich",
    waterType: "lake",
    lat: 47.3769,
    lng: 8.5417
  }) {
    location {
      id
      city
      waterName
      country
    }
  }
}
```

#### Location aktualisieren

```graphql
mutation {
  updateLocation(input: {
    id: "TG9jYXRpb25Ob2RlOjE=",
    city: "Zürich",
    waterName: "Zürichsee",
    lat: 47.3667,
    lng: 8.5500
  }) {
    location {
      id
      city
      waterName
    }
  }
}
```

**Verfügbare Felder für updateLocation:**
- Basis: `city`, `country`, `waterName`, `waterType`
- Geo: `lat`, `lng`, `address`

#### Location löschen

```graphql
mutation {
  deleteLocation(input: {
    id: "TG9jYXRpb25Ob2RlOjE="
  }) {
    success
    deletedId
  }
}
```

**⚠️ Warnung:** Löscht CASCADE alle Events an dieser Location! Erfordert Login.

### Race Mutationen

#### Race erstellen

```graphql
mutation {
  createRace(input: {
    eventId: "RXZlbnROb2RlOjEyMw==",
    date: "2025-07-15",
    distance: 5.0,
    raceTime: "09:00:00",
    name: "5km Open Water",
    wetsuit: "optional",
    priceValue: 45.00,
    priceCurrency: "CHF",
    coordinates: [47.3769, 8.5417, 47.3770, 8.5420]
  }) {
    race {
      id
      distance
      name
      priceValue
      priceCurrency
    }
  }
}
```

#### Race aktualisieren

```graphql
mutation {
  updateRace(input: {
    id: "UmFjZU5vZGU6NDU2",
    distance: 10.0,
    name: "10km Open Water",
    priceValue: 60.00,
    wetsuit: "prohibited"
  }) {
    race {
      id
      distance
      name
      priceValue
      wetsuit
    }
  }
}
```

**Verfügbare Felder für updateRace:**
- `distance`, `raceTime`, `name`, `wetsuit`
- `priceValue`, `priceCurrency`
- `coordinates` (flaches Array: [lat1, lng1, lat2, lng2, ...])

**Hinweise zu Preisen:**
- Wenn sowohl `priceValue` als auch `priceCurrency` angegeben werden, werden beide aktualisiert
- Wenn nur `priceValue` angegeben wird, wird nur der Betrag aktualisiert (Währung bleibt)
- Wenn nur `priceCurrency` angegeben wird, wird nur die Währung aktualisiert (Betrag bleibt)

#### Race löschen

```graphql
mutation {
  deleteRace(input: {
    id: "UmFjZU5vZGU6NDU2"
  }) {
    success
    deletedId
  }
}
```

### Organizer Mutationen

#### Organizer erstellen

```graphql
mutation {
  createOrganizer(input: {
    name: "Zurich Swimming Club",
    website: "https://zurichswimming.com",
    contactEmail: "info@zurichswimming.com",
    contactStatus: "pending"
  }) {
    organizer {
      id
      name
      website
      slug
    }
  }
}
```

**Hinweis:** `contactEmail` und `contactStatus` werden in der Datenbank gespeichert, aber NICHT im GraphQL-Response zurückgegeben (nicht exponiert).

#### Organizer aktualisieren

```graphql
mutation {
  updateOrganizer(input: {
    id: "T3JnYW5pemVyTm9kZTox",
    name: "Zurich Swimming Club e.V.",
    website: "https://zurichswimming.ch",
    contactStatus: "contacted"
  }) {
    organizer {
      id
      name
      website
    }
  }
}
```

**Verfügbare Felder für updateOrganizer:**
- Basis: `name`, `website`, `internalComment`
- Kontakt: `contactEmail`, `contactFormUrl`, `contactStatus`, `contactNotes`

**Wichtig:** Contact-Felder werden gespeichert, aber nicht im Response zurückgegeben.

#### Organizer löschen

```graphql
mutation {
  deleteOrganizer(input: {
    id: "T3JnYW5pemVyTm9kZTox"
  }) {
    success
    deletedId
  }
}
```

**Hinweis:** Setzt `organizer` auf NULL bei allen Events (SET_NULL). Erfordert Login.

## Wichtige Hinweise für LLM-Agents

### 1. ID-Format (Global IDs)

GraphQL Relay verwendet **Base64-codierte Global IDs**. Diese IDs haben das Format:

```
TypeName:InternalID (Base64-codiert)
```

Beispiel:
- Interne ID: `123`
- Type: `EventNode`
- Global ID: `RXZlbnROb2RlOjEyMw==` (Base64 von "EventNode:123")

**Wichtig:** Bei Mutationen müssen immer die Global IDs verwendet werden, nicht die internen Datenbank-IDs.

### 2. Schema-Einschränkungen

**Nicht exponierte Felder:**

Folgende Felder sind in Mutationen verfügbar, aber NICHT in Queries zurückgegeben:
- **Organizer**: `contactEmail`, `contactStatus`, `contactNotes`, `internalComment`
- **Event**: `internalComment` wird nicht im Schema exponiert

**Preis-Felder bei Race:**
- Im Schema: `priceValue` (String) und `priceCurrency` (String)
- **NICHT** `price` verwenden!

### 3. Cascade-Verhalten

**Wichtig für Datenintegrität:**
- Wenn eine **Location** gelöscht wird, werden **alle zugehörigen Events** gelöscht (CASCADE)
- Wenn ein **Event** gelöscht wird, werden **alle zugehörigen Races** gelöscht (CASCADE)
- Wenn ein **Organizer** gelöscht wird, bleiben Events erhalten, aber `organizer` wird auf `null` gesetzt (SET_NULL)

### 4. Automatische Metadaten

Bei jedem Speichern eines Events werden automatisch aktualisiert:
- `edited_by` - Aktueller User
- `edited_at` - Aktueller Zeitstempel

Bei der Erstellung werden zusätzlich gesetzt:
- `created_by` - Aktueller User
- `created_at` - Zeitstempel der Erstellung

### 5. Verifizierung

Events und Locations können verifiziert werden:
- Ein verifiziertes Event/Location hat ein `verified_at`-Datum (nicht NULL)
- Ein nicht verifiziertes Event/Location hat `verified_at = NULL`

### 6. Sortierung

**Events** werden standardmäßig nach `date_start` sortiert.

**Races** werden automatisch sortiert nach:
1. `date` (Datum)
2. `race_time` (Startzeit)
3. `distance` (Distanz)

### 7. Authentifizierung

Folgende Mutationen erfordern Authentifizierung (`@login_required`):
- Alle **Location** Mutationen (create, update, delete)
- Alle **Organizer** Mutationen (create, update, delete)
- **Event** delete
- **Race** Mutationen erfordern KEINE Authentifizierung

**Für API-Zugriff:** Das System unterstützt API-Tokens (siehe `ApiToken`-Model und `my_api_tokens`-Query).

### 8. Enum-Werte Validierung

Folgende Felder haben feste Werte:

**Event:**
- `entryQuality`: `"incomplete"`, `"complete"`

**Race:**
- `wetsuit`: `"compulsory"`, `"optional"`, `"prohibited"`

**Location:**
- `waterType`: `"river"`, `"sea"`, `"lake"`, `"pool"`

**Organizer:**
- `contactStatus`: `"pending"`, `"contacted"`, `"responded"`, `"completed"`, `"failed"`, `"needs_review"`

## Praktische Beispiele für typische Aufgaben

### Beispiel 1: Vollständiges Event mit Races erstellen

```graphql
# Schritt 1: Location erstellen
mutation {
  createLocation(input: {
    city: "Geneva",
    country: "CH",
    waterName: "Lake Geneva",
    waterType: "lake",
    lat: 46.2044,
    lng: 6.1432
  }) {
    location {
      id  # Speichern: TG9jYXRpb25Ob2RlOjUwMA==
    }
  }
}

# Schritt 2: Organizer erstellen
mutation {
  createOrganizer(input: {
    name: "Geneva Swimming Association",
    website: "https://genevaswim.ch"
  }) {
    organizer {
      id  # Speichern: T3JnYW5pemVyTm9kZTo1MA==
    }
  }
}

# Schritt 3: Event erstellen
mutation {
  createEvent(input: {
    name: "Geneva Lake Marathon 2025",
    dateStart: "2025-08-10",
    dateEnd: "2025-08-10",
    locationId: "TG9jYXRpb25Ob2RlOjUwMA==",
    organizerId: "T3JnYW5pemVyTm9kZTo1MA==",
    website: "https://genevamarathon.ch",
    description: "Annual marathon swimming event",
    waterTemp: 22.0
  }) {
    event {
      id  # Speichern: RXZlbnROb2RlOjEwMDA=
    }
  }
}

# Schritt 4: Races hinzufügen
mutation {
  createRace(input: {
    eventId: "RXZlbnROb2RlOjEwMDA=",
    date: "2025-08-10",
    distance: 5.0,
    raceTime: "08:00:00",
    name: "5km Race",
    wetsuit: "optional",
    priceValue: 50.00,
    priceCurrency: "CHF"
  }) {
    race {
      id
    }
  }
}

mutation {
  createRace(input: {
    eventId: "RXZlbnROb2RlOjEwMDA=",
    date: "2025-08-10",
    distance: 10.0,
    raceTime: "10:00:00",
    name: "10km Marathon",
    wetsuit: "prohibited",
    priceValue: 75.00,
    priceCurrency: "CHF"
  }) {
    race {
      id
    }
  }
}
```

### Beispiel 2: Event-Status aktualisieren (Ausverkauft setzen)

```graphql
mutation {
  updateEvent(input: {
    id: "RXZlbnROb2RlOjEwMDA=",
    soldOut: true
  }) {
    event {
      id
      name
      soldOut
    }
  }
}
```

### Beispiel 3: Alle Schweizer Events im Sommer 2025 finden

```graphql
query {
  allEvents(
    locationCountry: "CH",
    dateFrom: "2025-06-01",
    dateTo: "2025-08-31"
  ) {
    edges {
      node {
        id
        name
        dateStart
        dateEnd
        location {
          city
          waterName
        }
        races {
          edges {
            node {
              distance
              priceValue
              priceCurrency
            }
          }
        }
      }
    }
  }
}
```

### Beispiel 4: Race-Preis anpassen

```graphql
mutation {
  updateRace(input: {
    id: "UmFjZU5vZGU6NzU=",
    priceValue: 55.00
  }) {
    race {
      id
      priceValue
      priceCurrency
    }
  }
}
```

### Beispiel 5: Event komplett mit allen Races löschen

```graphql
# Löscht automatisch alle zugehörigen Races (CASCADE)
mutation {
  deleteEvent(input: {
    id: "RXZlbnROb2RlOjEwMDA="
  }) {
    success
    deletedId
  }
}
```

## Fehlerbehandlung

Bei GraphQL-Anfragen können Fehler auftreten:

```json
{
  "errors": [
    {
      "message": "Event matching query does not exist.",
      "locations": [{"line": 2, "column": 3}],
      "path": ["event"]
    }
  ]
}
```

**Häufige Fehlerursachen:**
1. Ungültige ID (falsches Format oder nicht existierend)
2. Fehlende Authentifizierung bei geschützten Operationen
3. Ungültige Feldnamen (case-sensitive! z.B. `price` statt `priceValue`)
4. Fehlende Pflichtfelder bei Mutationen
5. Enum-Werte nicht korrekt (z.B. `"optional"` statt `"Optional"`)
6. Versuch, nicht exponierte Felder abzufragen (z.B. `contactEmail` bei Organizer)

## Testing

Ein interaktives Test-Skript ist verfügbar unter `backend/test_mutations.py`:

```bash
cd backend
python test_mutations.py
```

Das Skript testet alle CRUD-Operationen für alle Entitäten mit interaktiver Authentifizierung.

## Zusammenfassung: Verfügbare Mutationen

### Event (3 Mutationen)
- ✅ `createEvent` - Neue Events erstellen
- ✅ `updateEvent` - Events mit allen Feldern aktualisieren
- ✅ `deleteEvent` - Events löschen (CASCADE auf Races)

### Location (3 Mutationen)
- ✅ `createLocation` - Neue Locations erstellen
- ✅ `updateLocation` - Locations aktualisieren
- ✅ `deleteLocation` - Locations löschen (CASCADE auf Events)

### Race (3 Mutationen)
- ✅ `createRace` - Neue Races zu Events hinzufügen
- ✅ `updateRace` - Race-Details aktualisieren
- ✅ `deleteRace` - Einzelne Races löschen

### Organizer (3 Mutationen)
- ✅ `createOrganizer` - Neue Organizers erstellen
- ✅ `updateOrganizer` - Organizer-Informationen aktualisieren
- ✅ `deleteOrganizer` - Organizers löschen (SET_NULL auf Events)

**Total: 12 vollständige CRUD-Mutationen**
