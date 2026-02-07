# Event Processing Guide

A practical guide for maintaining and growing the OWSwims event database year over year.

---

## Quick Reference: The Annual Workflow

```
Phase 1: Copy         copy_to_next_year 2027             (run ONCE)
Phase 2: Batch update update_crawl_sources 2027           (re-runnable)
Phase 3: Individual   update_next_year_events 2027        (re-runnable)
Phase 4: Discover     discover_event_urls + crawl_events  (re-runnable)
Phase 5: Manual       crawl_events --event/--crawl/--file (as needed)
Phase 6: Cleanup      merge_events + merge_locations      (re-runnable)
Phase 7: Data quality process_unverified_locations, etc.  (re-runnable)
```

---

## Phase 1: Copy Events from Previous Year

```bash
cd backend
python manage.py copy_to_next_year 2027
```

**What it does:** Clones all events from 2026 to 2027. Sets them as invisible + unverified. Links each copy via `previous_year_event`.

**CRITICAL: Run exactly once per year.** There is no duplicate check. Running it twice creates duplicate events for the entire year.

**Before running, verify no copies exist yet:**
```bash
python manage.py shell -c "
from app.models import Event
print(Event.objects.filter(date_start__year=2027, source='Copied from past year').count())
"
```
If the count is > 0, copies already exist. Do NOT run again.

**Result:** ~all recurring events exist as invisible templates for the target year.

---

## Phase 2: Batch-Update Series Events

Series events are groups of events from the same organizer on the same website (e.g., Oceanman, which has 10+ events listed on one page).

### 2a: Create CrawlSources (only needed for new series)

```bash
# Preview
python manage.py identify_crawl_sources 2026 --dry-run

# Create
python manage.py identify_crawl_sources 2026
```

This groups events by (hostname, organizer) and creates `CrawlSource` records for groups with 3+ events. Only needs to be run when new series emerge. Existing CrawlSources are preserved.

For third-party calendars (e.g., ffneaulibre.fr), create CrawlSource records manually in Django admin with `source_type=calendar`.

### 2b: Update events via CrawlSources

```bash
# Preview
python manage.py update_crawl_sources 2027 --dry-run

# Run
python manage.py update_crawl_sources 2027

# Force re-crawl a specific source
python manage.py update_crawl_sources 2027 --crawl-source 123 --force
```

**What it does:**
- **Series type:** Crawls homepage once, matches extracted events to DB events by date order, updates all at once.
- **Calendar type:** Crawls calendar page, filters already-known URLs, imports new events individually.

**Known issue:** Series matching by date order can assign wrong locations when the number of events changes year-over-year. Always preview with `--dry-run` first.

**Re-runnable:** Yes. Uses check interval (skips recently crawled sources). Use `--force` to override.

---

## Phase 3: Update Individual Events

```bash
# Preview
python manage.py update_next_year_events 2027 --dry-run

# Run
python manage.py update_next_year_events 2027

# Force re-check all
python manage.py update_next_year_events 2027 --force
```

**What it does:** Crawls each event's website individually to fetch updated info (dates, races, descriptions). Only targets events that:
- Are in the target year
- Are invisible + unverified
- Have a `previous_year_event` link
- Do **NOT** have a `crawl_source` (those were handled in Phase 2)

**Re-runnable:** Yes. Respects `last_auto_check_at` (default: skip if checked within 30 days). Use `--force` to override.

**Result:** Previously invisible events become visible with fresh data. Location and organizer are preserved.

---

## Phase 4: Discover New Events

This finds events that were NOT in last year's database.

### 4a: Search Google for new event URLs

```bash
# Search specific countries
python manage.py discover_event_urls --countries CH DE FR AT

# Limit for testing
python manage.py discover_event_urls --countries CH --limit 5 --dry-run
```

Searches Google in 20+ languages, validates URLs with GPT, and saves results to `discovered_event_urls.json`. Uses a URL cache to avoid re-validating known URLs across runs.

### 4b: Import discovered events

```bash
python manage.py crawl_events --discovered discovered_event_urls.json
```

**Duplicate check:** Checks location + date before creating. Skips if an event already exists at the same location on the same date.

**Re-runnable:** Yes. Both the URL cache and the location+date check prevent duplicates.

---

## Phase 5: Manual Imports

For events you find yourself or that users submit via the submission form.

```bash
# Single event from one or more URLs
python manage.py crawl_events --event https://example.com/swim-event

# Multiple URLs for the same event (e.g., event page + registration page)
python manage.py crawl_events --event https://example.com/event https://example.com/register

# Crawl a listing page with multiple events
python manage.py crawl_events --crawl https://example.com/events-2027

# Batch from a text file (one URL per line)
python manage.py crawl_events --file my_urls.txt

# With a specific crawl profile
python manage.py crawl_events --profile outdoorswimmer

# Dry run
python manage.py crawl_events --event https://example.com/event --dry-run
```

**Duplicate check:** Location + date matching. Use `--update-existing` to update instead of skip.

---

## Phase 6: Cleanup

### Merge duplicate events

```bash
# Preview
python manage.py merge_events --dry-run

# Interactive merge
python manage.py merge_events

# Check specific location
python manage.py merge_events --location 123
```

Finds future events at the same location + same date. Interactive: shows both events and asks which to keep.

### Merge duplicate locations

```bash
# Preview (500m default)
python manage.py merge_locations --dry-run

# Custom distance
python manage.py merge_locations --distance 1000
```

---

## Phase 7: Data Quality

```bash
# Geocode new locations + fetch images
python manage.py process_unverified_locations

# Geocode only (locations missing coordinates)
python manage.py geocode

# Fix currencies based on country
python manage.py fix_race_currencies
```

---

## Safety Checklist

| Command | Safe to re-run? | Notes |
|---------|:---:|-------|
| `copy_to_next_year` | **NO** | Creates duplicates if run twice |
| `identify_crawl_sources` | Yes | Uses get_or_create |
| `update_crawl_sources` | Yes | Check interval; use `--force` to override |
| `update_next_year_events` | Yes | Check interval; use `--force` to override |
| `discover_event_urls` | Yes | URL cache prevents re-validation |
| `crawl_events` | Yes | Location + date dedup |
| `merge_events` | Yes | Interactive, idempotent |
| `merge_locations` | Yes | Interactive, idempotent |

---

## How Events Flow Through the System

```
                     +-----------------------+
                     | Previous Year Events  |
                     | (visible, verified)   |
                     +-----------+-----------+
                                 |
                    copy_to_next_year (ONCE)
                                 |
                     +-----------v-----------+
                     | Next Year Templates   |
                     | invisible=True        |
                     | verified_at=None      |
                     +--+----------------+---+
                        |                |
            has crawl_source?    no crawl_source
                        |                |
          update_crawl_sources    update_next_year_events
                        |                |
                     +--v----------------v---+
                     | Updated Events        |
                     | invisible=False       |
                     | verified_at=None      |
                     +-----------------------+

    discover_event_urls ──> crawl_events ──> New Events (invisible=True)
    manual URLs ──────────> crawl_events ──> New Events (invisible=True)

    merge_events ──> Removes duplicates (same location + date)
```

---

## Tips

- **Always `--dry-run` first** for update_crawl_sources and update_next_year_events. Review the output before committing.
- **Phases 2 and 3 don't overlap.** update_next_year_events explicitly excludes events with a crawl_source, so there's no risk of double-updating.
- **Phase 4 can overlap with Phase 1.** A discovered event might already exist from copy_to_next_year, but the location+date check in crawl_events handles this.
- **Log files** are written to `backend/logs/` for update_next_year_events, update_crawl_sources, and send_marketing_emails. Check these after large batch runs.
- **Check interval** defaults: update_crawl_sources skips sources crawled this calendar year; update_next_year_events skips events checked within 30 days. Use `--force` to override both.

---

## Post-Processing: Marketing Emails

After the event database is updated and analytics are collected:

```bash
# Fetch Google Analytics data (run for previous year)
python manage.py fetch_analytics --year 2026

# Preview marketing emails
python manage.py send_marketing_emails --year 2026 --dry-run

# Send (skips already-emailed organizers)
python manage.py send_marketing_emails --year 2026

# Test with your own email
python manage.py send_marketing_emails --year 2026 --test-email silvan@open-water-swims.com --organizer-id 123
```

Note: `--year` defaults to the current year. In January, you typically want `--year` set to the previous year (where the analytics data is).

---

*Last updated: 2026-02-07 | git: e85d18a*
