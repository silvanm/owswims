import base64
import logging
from collections import defaultdict

import click
from tqdm import tqdm
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from app.models import Event, Race
from app.services.geocoding_service import GeocodingService
from app.services.llm_service import LLMService
from app.services.smart_merge_models import MergeDecision

logger = logging.getLogger(__name__)


def _yn(val):
    """Format boolean-ish value as colored marker."""
    return "YES" if val else " - "


def format_event_for_llm(event, label):
    """Format event info for the LLM prompt (plain text)."""
    races = event.races.all()
    race_info = ", ".join(
        f"{r.distance}km" + (f" ({r.name})" if r.name else "")
        for r in races
    )
    return (
        f"Event {label}:\n"
        f"  ID: {event.id}\n"
        f"  Name: {event.name}\n"
        f"  Date: {event.date_start}\n"
        f"  Website: {event.website or 'N/A'}\n"
        f"  Description: {(event.description or 'N/A')[:200]}\n"
        f"  Organizer: "
        f"{event.organizer.name if event.organizer else 'N/A'}\n"
        f"  Races ({races.count()}): {race_info or 'none'}\n"
        f"  Verified: {'Yes' if event.is_verified() else 'No'}\n"
        f"  Has Flyer: {'Yes' if event.flyer_image else 'No'}\n"
        f"  Entry Quality: {event.entry_quality or 'N/A'}\n"
        f"  Created: {event.created_at}"
    )


def format_location_for_llm(location, label):
    """Format location info for the LLM prompt (plain text)."""
    return (
        f"Location {label}:\n"
        f"  ID: {location.id}\n"
        f"  Name: {location.water_name or 'N/A'}\n"
        f"  City: {location.city}, {location.country}\n"
        f"  Address: {location.address or 'N/A'}\n"
        f"  Water Type: {location.water_type or 'N/A'}\n"
        f"  Coordinates: {location.lat}, {location.lng}\n"
        f"  Verified: {'Yes' if location.is_verified() else 'No'}\n"
        f"  Has Image: {'Yes' if location.header_photo else 'No'}\n"
        f"  Events: {location.events.count()}"
    )


def format_comparison_table(stdout, style, event_a, event_b,
                            loc_a, loc_b):
    """Print a side-by-side comparison table to stdout."""
    races_a = event_a.races.all()
    races_b = event_b.races.all()
    race_str_a = ", ".join(
        f"{r.distance}km" for r in races_a
    ) or "none"
    race_str_b = ", ".join(
        f"{r.distance}km" for r in races_b
    ) or "none"

    w = 38  # column width

    def row(label, val_a, val_b):
        a = str(val_a)[:w].ljust(w)
        b = str(val_b)[:w].ljust(w)
        return f"  {label:<14s} {a} {b}"

    hdr_a = "A".center(w)
    hdr_b = "B".center(w)
    sep = "-" * 14 + "-+-" + "-" * w + "-+-" + "-" * w

    stdout.write(
        style.MIGRATE_HEADING(
            f"  {'':14s} {hdr_a} {hdr_b}"
        )
    )
    stdout.write(f"  {sep}")

    # Location section
    stdout.write(style.MIGRATE_LABEL("  LOCATION"))
    stdout.write(row(
        "Name",
        loc_a.water_name or "-",
        loc_b.water_name or "-",
    ))
    stdout.write(row(
        "City",
        f"{loc_a.city}, {loc_a.country}",
        f"{loc_b.city}, {loc_b.country}",
    ))
    stdout.write(row(
        "Address",
        loc_a.address or "-",
        loc_b.address or "-",
    ))
    stdout.write(row(
        "Water type",
        loc_a.water_type or "-",
        loc_b.water_type or "-",
    ))
    stdout.write(row(
        "Coords",
        f"{loc_a.lat:.5f}, {loc_a.lng:.5f}",
        f"{loc_b.lat:.5f}, {loc_b.lng:.5f}",
    ))
    stdout.write(row(
        "Verified",
        _yn(loc_a.is_verified()),
        _yn(loc_b.is_verified()),
    ))
    stdout.write(row(
        "Has image",
        _yn(loc_a.header_photo),
        _yn(loc_b.header_photo),
    ))
    stdout.write(row(
        "# Events",
        loc_a.events.count(),
        loc_b.events.count(),
    ))
    stdout.write(row("ID", loc_a.id, loc_b.id))

    stdout.write(f"  {sep}")

    # Event section
    stdout.write(style.MIGRATE_LABEL("  EVENT"))
    stdout.write(row("Name", event_a.name, event_b.name))
    stdout.write(row(
        "Organizer",
        event_a.organizer.name if event_a.organizer else "-",
        event_b.organizer.name if event_b.organizer else "-",
    ))
    stdout.write(row(
        "Races",
        f"{races_a.count()}: {race_str_a}",
        f"{races_b.count()}: {race_str_b}",
    ))
    stdout.write(row(
        "Website",
        event_a.website or "-",
        event_b.website or "-",
    ))
    stdout.write(row(
        "Verified",
        _yn(event_a.is_verified()),
        _yn(event_b.is_verified()),
    ))
    stdout.write(row(
        "Has flyer",
        _yn(event_a.flyer_image),
        _yn(event_b.flyer_image),
    ))
    stdout.write(row(
        "Description",
        (event_a.description or "-")[:w],
        (event_b.description or "-")[:w],
    ))
    stdout.write(row(
        "Quality",
        event_a.entry_quality or "-",
        event_b.entry_quality or "-",
    ))
    stdout.write(row("ID", event_a.id, event_b.id))


def build_llm_prompt(event_a, event_b, loc_a, loc_b, distance_m):
    """Build the text prompt for the LLM merge decision."""
    return (
        "You are helping merge duplicate open-water swimming events.\n"
        "Two events happen on the same date at nearby but distinct "
        f"locations ({distance_m:.0f}m apart).\n\n"
        "Decide:\n"
        "1. Which LOCATION to keep (prefer the one closer to a body "
        "of water visible on the satellite image, or with "
        "better/more complete data).\n"
        "2. Which EVENT to keep as primary (prefer verified, more "
        "races, richer data).\n"
        "3. What data to merge from the secondary event into the "
        "primary.\n\n"
        f"{format_location_for_llm(loc_a, 'A')}\n\n"
        f"{format_location_for_llm(loc_b, 'B')}\n\n"
        f"{format_event_for_llm(event_a, 'A')}\n\n"
        f"{format_event_for_llm(event_b, 'B')}\n"
    )


class Command(BaseCommand):
    help = (
        "Find same-date events at nearby (but different) locations, "
        "use LLM + satellite vision to pick the better location and event, "
        "then merge."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--distance",
            type=float,
            default=1500,
            help="Max distance in meters between locations (default: 1500)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show recommendations without making changes",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Max number of candidate groups to process",
        )
        parser.add_argument(
            "--auto",
            action="store_true",
            help="Auto-apply merges above the confidence threshold",
        )
        parser.add_argument(
            "--confidence-threshold",
            type=float,
            default=0.8,
            help="Min confidence for --auto mode (default: 0.8)",
        )
        parser.add_argument(
            "--no-vision",
            action="store_true",
            help="Skip satellite map, use text-only LLM decision",
        )
        parser.add_argument(
            "--country",
            type=str,
            default=None,
            help="Filter events by country code (e.g. CH, DE)",
        )

    def handle(self, *args, **options):
        distance_m = options["distance"]
        dry_run = options["dry_run"]
        limit = options["limit"]
        auto = options["auto"]
        confidence_threshold = options["confidence_threshold"]
        no_vision = options["no_vision"]
        country = options["country"]

        geo = GeocodingService(stdout=self.stdout, stderr=self.stderr)
        llm = LLMService()

        # Step 1: Find candidate groups
        candidates = self._find_candidates(geo, distance_m, country)

        if not candidates:
            self.stdout.write(self.style.SUCCESS("No candidate merge groups found."))
            return

        if limit:
            candidates = candidates[:limit]

        self.stdout.write(f"Found {len(candidates)} candidate merge group(s).\n")

        merged = 0
        skipped = 0
        deleted_ids = set()  # track already-merged events

        total = len(candidates)
        for i, (event_a, event_b, loc_a, loc_b, dist) in enumerate(
            candidates, 1
        ):
            # Skip if either event was already merged
            if event_a.id in deleted_ids or event_b.id in deleted_ids:
                skipped += 1
                continue

            # Header
            self.stdout.write("")
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    f"  [{i}/{total}]  "
                    f"{event_a.date_start}  "
                    f"{dist:.0f}m apart"
                )
            )

            # Side-by-side comparison
            format_comparison_table(
                self.stdout, self.style,
                event_a, event_b, loc_a, loc_b,
            )

            # Get LLM decision
            self.stdout.write("")
            self.stdout.write("  Asking LLM...")
            decision = self._get_merge_decision(
                llm, geo, event_a, event_b,
                loc_a, loc_b, dist, no_vision,
            )

            if decision is None:
                self.stdout.write(
                    self.style.WARNING("  LLM failed — skipped")
                )
                skipped += 1
                continue

            if decision.confidence < 0.3:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Low confidence "
                        f"({decision.confidence:.0%}) — skipped"
                    )
                )
                skipped += 1
                continue

            # Decision box
            conf_pct = f"{decision.confidence:.0%}"
            keep_e = decision.keep_event
            keep_l = decision.keep_location
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    f"  RECOMMENDATION  (confidence {conf_pct})"
                )
            )
            self.stdout.write(
                f"  Keep location {keep_l}  "
                f"{decision.location_reasoning}"
            )
            self.stdout.write(
                f"  Keep event    {keep_e}  "
                f"{decision.event_reasoning}"
            )

            flags = []
            if decision.merge_races:
                flags.append("races")
            if decision.merge_description:
                flags.append("description")
            if decision.merge_website:
                flags.append("website")
            if decision.merge_flyer:
                flags.append("flyer")
            if flags:
                self.stdout.write(
                    f"  Copy from secondary: {', '.join(flags)}"
                )

            if dry_run:
                self.stdout.write(
                    self.style.WARNING("  [dry-run] no changes")
                )
                continue

            # Confirm
            should_apply = False
            if auto and decision.confidence >= confidence_threshold:
                self.stdout.write(
                    self.style.SUCCESS("  Auto-applying")
                )
                should_apply = True
            else:
                should_apply = click.confirm(
                    "  Apply this merge?", default=True
                )

            if should_apply:
                deleted_event_id = self._execute_merge(
                    decision, event_a, event_b, loc_a, loc_b
                )
                deleted_ids.add(deleted_event_id)
                merged += 1
            else:
                self.stdout.write(
                    self.style.WARNING("  Skipped")
                )
                skipped += 1

        # Summary
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"  Done: {merged} merged, {skipped} skipped "
                f"(of {total} candidates)"
            )
        )

    def _find_candidates(self, geo, distance_m, country):
        """Find same-date events at nearby but different locations."""
        current_date = timezone.now().date()
        events = Event.objects.filter(
            date_start__gte=current_date,
            location__isnull=False,
            location__lat__isnull=False,
            location__lng__isnull=False,
        ).select_related("location", "organizer")

        if country:
            events = events.filter(location__country=country)

        # Group by date_start
        by_date = defaultdict(list)
        for event in events:
            by_date[event.date_start].append(event)

        multi_dates = {
            d: evts for d, evts in by_date.items() if len(evts) >= 2
        }

        candidates = []
        seen_pairs = set()

        for date, date_events in tqdm(
            multi_dates.items(),
            desc="Scanning dates",
            unit="date",
        ):
            for i, e1 in enumerate(date_events):
                for e2 in date_events[i + 1:]:
                    if e1.location_id == e2.location_id:
                        continue  # Same location — handled by merge_events

                    pair_key = tuple(sorted([e1.id, e2.id]))
                    if pair_key in seen_pairs:
                        continue

                    loc1, loc2 = e1.location, e2.location
                    dist = geo.get_distance_from_lat_lng_in_km(
                        loc1.lat, loc1.lng, loc2.lat, loc2.lng
                    ) * 1000

                    if dist <= distance_m:
                        seen_pairs.add(pair_key)
                        candidates.append((e1, e2, loc1, loc2, dist))

        # Sort by distance (closest first)
        candidates.sort(key=lambda x: x[4])
        return candidates

    def _get_merge_decision(
        self, llm, geo, event_a, event_b, loc_a, loc_b, dist, no_vision
    ):
        """Ask LLM for a merge decision, optionally with satellite map."""
        prompt_text = build_llm_prompt(event_a, event_b, loc_a, loc_b, dist)

        # Vision path
        if not no_vision:
            map_bytes = geo.generate_static_map(
                [
                    {"lat": loc_a.lat, "lng": loc_a.lng, "label": "A"},
                    {"lat": loc_b.lat, "lng": loc_b.lng, "label": "B"},
                ]
            )
            if not map_bytes:
                raise CommandError(
                    "Static Maps API failed. Enable it in Google "
                    "Cloud Console, or use --no-vision."
                )

            b64 = base64.b64encode(map_bytes).decode("utf-8")
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64}",
                            },
                        },
                    ],
                }
            ]
            try:
                return llm.parse_vision_completion(
                    messages=messages,
                    response_model=MergeDecision,
                    system_prompt=(
                        "You are an expert at analysing satellite "
                        "imagery and open-water swimming event "
                        "data. Pick the location closer to a "
                        "visible body of water."
                    ),
                )
            except Exception:
                logger.exception("Vision LLM call failed")
                return None

        # Text-only path (--no-vision)
        try:
            return llm.parse_completion(
                prompt=prompt_text,
                response_model=MergeDecision,
                system_prompt=(
                    "You are an expert at open-water swimming "
                    "event data. Decide which location and event "
                    "to keep when merging duplicates."
                ),
            )
        except Exception:
            logger.exception("Text-only LLM call failed")
            return None

    @transaction.atomic
    def _execute_merge(self, decision, event_a, event_b, loc_a, loc_b):
        """Execute the merge based on the LLM decision."""
        # Determine primary/secondary
        primary_event = event_a if decision.keep_event == "A" else event_b
        secondary_event = event_b if decision.keep_event == "A" else event_a
        keep_loc = loc_a if decision.keep_location == "A" else loc_b
        lose_loc = loc_b if decision.keep_location == "A" else loc_a

        actions = []

        # 1. Merge data from secondary event into primary
        if decision.merge_races:
            n = Race.objects.filter(event=secondary_event).count()
            Race.objects.filter(event=secondary_event).update(
                event=primary_event
            )
            if n:
                actions.append(f"transferred {n} race(s)")

        if decision.merge_description and not primary_event.description:
            if secondary_event.description:
                primary_event.description = secondary_event.description
                actions.append("copied description")

        if decision.merge_website and not primary_event.website:
            if secondary_event.website:
                primary_event.website = secondary_event.website
                actions.append("copied website")

        if decision.merge_flyer and not primary_event.flyer_image:
            if secondary_event.flyer_image:
                primary_event.flyer_image = secondary_event.flyer_image
                actions.append("copied flyer")

        if primary_event.location_id != keep_loc.id:
            primary_event.location = keep_loc
        primary_event.save()

        # Coalesce location fields from the losing location
        loc_fields = [
            "water_name", "water_type", "address", "header_photo",
        ]
        coalesced = []
        for field in loc_fields:
            keep_val = getattr(keep_loc, field)
            lose_val = getattr(lose_loc, field)
            if not keep_val and lose_val:
                setattr(keep_loc, field, lose_val)
                coalesced.append(field)
        if coalesced:
            keep_loc.save()
            actions.append(
                f"coalesced location: {', '.join(coalesced)}"
            )

        # 2. Delete secondary event
        secondary_id = secondary_event.id
        secondary_event.delete()
        actions.append(f"deleted event #{secondary_id}")

        # 3. Merge locations
        if lose_loc.id != keep_loc.id:
            remaining = Event.objects.filter(location=lose_loc).count()
            if remaining:
                Event.objects.filter(location=lose_loc).update(
                    location=keep_loc
                )
                actions.append(
                    f"moved {remaining} event(s) to loc #{keep_loc.id}"
                )
            lose_loc_id = lose_loc.id
            lose_loc.delete()
            actions.append(f"deleted location #{lose_loc_id}")

        self.stdout.write(
            self.style.SUCCESS(
                f"  Done: {'; '.join(actions)}"
            )
        )
        return secondary_id
