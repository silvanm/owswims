"""
Tests for fuzzy search in MCP tools.

The pure fuzzy_rank tests need no DB. The MCP tool tests use mock objects
to simulate Django querysets, avoiding migration issues with the test DB.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from app.mcp.utils import fuzzy_rank, haversine_km


# ── Pure unit tests for fuzzy_rank (no DB) ──────────────────────────


class TestFuzzyRank:
    """Tests for the fuzzy_rank utility function."""

    def test_exact_match_ranked_first(self):
        items = ["Bodensee", "Zürichsee", "Thunersee"]
        result = fuzzy_rank(items, lambda x: x, "Bodensee")
        assert result[0] == "Bodensee"

    def test_accent_matching(self):
        """'zurich' should match 'Zürich'."""
        items = ["Zürich", "Berlin", "Wien"]
        result = fuzzy_rank(items, lambda x: x, "zurich")
        assert "Zürich" in result

    def test_compound_word_matching(self):
        """'zurich see' should match 'Zürichsee'."""
        items = ["Zürichsee", "Bodensee", "Lac Léman"]
        result = fuzzy_rank(items, lambda x: x, "zurich see")
        assert "Zürichsee" in result

    def test_accent_in_french(self):
        """'lac leman' should match 'Lac Léman'."""
        items = ["Lac Léman", "Bodensee", "Zürichsee"]
        result = fuzzy_rank(items, lambda x: x, "lac leman")
        assert "Lac Léman" in result

    def test_cutoff_filters_low_scores(self):
        items = ["Zürichsee", "completely unrelated xyz"]
        result = fuzzy_rank(items, lambda x: x, "zurich see", cutoff=60)
        assert "completely unrelated xyz" not in result

    def test_empty_query(self):
        items = ["Foo", "Bar"]
        result = fuzzy_rank(items, lambda x: x, "")
        assert result == []

    def test_empty_items(self):
        result = fuzzy_rank([], lambda x: x, "test")
        assert result == []

    def test_none_key_handled(self):
        """Items where key_func returns None should score 0."""
        items = ["valid", None]
        result = fuzzy_rank(items, lambda x: x, "valid")
        assert None not in result
        assert "valid" in result

    def test_sorted_by_score_descending(self):
        """Best match should come first."""
        items = ["Swiss Aquatics", "Swiss Swimming Federation", "Aquatics"]
        result = fuzzy_rank(items, lambda x: x, "swiss aquatics")
        assert result[0] == "Swiss Aquatics"

    def test_custom_cutoff(self):
        items = ["Zürichsee", "Bodensee"]
        result = fuzzy_rank(items, lambda x: x, "Zürichsee", cutoff=95)
        assert "Zürichsee" in result
        assert "Bodensee" not in result

    def test_key_func_with_objects(self):
        """key_func should work with arbitrary objects."""

        class FakeEvent:
            def __init__(self, name):
                self.name = name

        items = [FakeEvent("Zürich Marathon"), FakeEvent("Berlin Swim")]
        result = fuzzy_rank(items, lambda e: e.name, "zurich")
        assert len(result) >= 1
        assert result[0].name == "Zürich Marathon"


# ── MCP tool tests with mocked DB ───────────────────────────────────
#
# The @mcp.tool decorator wraps functions into FunctionTool objects.
# We access the underlying async function via .fn to call it directly.


def _fake_sync_to_async(f):
    """Replace sync_to_async: wrap sync function in an async wrapper."""
    async def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


# Helper to create fake model-like objects


def _make_location(**kwargs):
    defaults = dict(
        id=1, city="Unknown", country="XX", water_name=None,
        water_type=None, lat=None, lng=None, address=None,
        average_rating=None,
    )
    defaults.update(kwargs)
    loc = SimpleNamespace(**defaults)
    loc.__str__ = lambda self: f"{self.city}, {self.country}"
    return loc


def _make_organizer(**kwargs):
    defaults = dict(
        id=1, name="Unknown", website="", slug="unknown",
        contact_email=None, language=None, contact_status=None,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_event(location=None, organizer=None, **kwargs):
    defaults = dict(
        id=1, name="Unknown Event", date_start="2026-06-01",
        date_end="2026-06-01", website="", description="",
        cancelled=False, invisible=False,
    )
    defaults.update(kwargs)
    obj = SimpleNamespace(**defaults)
    obj.location = location
    obj.organizer = organizer
    return obj


def _make_race(event=None, **kwargs):
    defaults = dict(
        id=1, event_id=1, date="2026-06-01", race_time=None,
        distance=5.0, name="5km Race", wetsuit=None, price=None,
        coordinates=None,
    )
    defaults.update(kwargs)
    obj = SimpleNamespace(**defaults)
    obj.event = event or _make_event()
    obj.event_id = obj.event.id
    return obj


class TestSearchEventsTools:
    """Test search_events and list_events search param."""

    @pytest.mark.asyncio
    async def test_search_events_fuzzy_match(self):
        from app.mcp.tools.events import search_events

        loc = _make_location(id=1, city="Zürich", country="CH",
                             water_name="Zürichsee")
        org = _make_organizer(id=1, name="Swiss Aquatics")
        events = [
            _make_event(id=1, name="Zürich Swim Classic",
                        location=loc, organizer=org),
            _make_event(id=2, name="Berlin Open Water",
                        location=_make_location(id=2, city="Berlin",
                                                country="DE"),
                        organizer=None),
        ]

        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: events

        with patch("app.mcp.tools.events.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Event.objects", mock_qs):
                ctx = MagicMock()
                results = await search_events.fn(ctx, query="zurich swim")

        names = [r["name"] for r in results]
        assert "Zürich Swim Classic" in names

    @pytest.mark.asyncio
    async def test_search_events_no_match(self):
        from app.mcp.tools.events import search_events

        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: []

        with patch("app.mcp.tools.events.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Event.objects", mock_qs):
                ctx = MagicMock()
                results = await search_events.fn(ctx, query="xyznonexistent")

        assert results == []

    @pytest.mark.asyncio
    async def test_list_events_with_search(self):
        from app.mcp.tools.events import list_events

        loc = _make_location(id=1, city="Zürich", country="CH",
                             water_name="Zürichsee")
        events = [
            _make_event(id=1, name="Zürich Swim Classic", location=loc,
                        organizer=None),
        ]

        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: events

        with patch("app.mcp.tools.events.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Event.objects", mock_qs):
                ctx = MagicMock()
                results = await list_events.fn(ctx, search="zurich")

        names = [r["name"] for r in results]
        assert "Zürich Swim Classic" in names

    @pytest.mark.asyncio
    async def test_list_events_without_search(self):
        """Without search, events are returned in date order, no fuzzy."""
        from app.mcp.tools.events import list_events

        loc = _make_location(id=1, city="Zürich", country="CH")
        events = [
            _make_event(id=1, name="Event A", location=loc, organizer=None),
            _make_event(id=2, name="Event B", location=loc, organizer=None),
        ]

        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: events

        with patch("app.mcp.tools.events.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Event.objects", mock_qs):
                ctx = MagicMock()
                results = await list_events.fn(ctx, limit=10)

        assert len(results) == 2
        # order_by should have been called (date_start ordering)
        mock_qs.order_by.assert_called_with('date_start')


class TestSearchLocationsTools:
    """Test search_locations and list_locations search param."""

    @pytest.mark.asyncio
    async def test_search_locations_fuzzy(self):
        from app.mcp.tools.locations import search_locations

        locations = [
            _make_location(id=1, city="Zürich", country="CH",
                           water_name="Zürichsee", water_type="lake"),
            _make_location(id=2, city="Genève", country="CH",
                           water_name="Lac Léman", water_type="lake"),
        ]

        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: locations

        with patch("app.mcp.tools.locations.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Location.objects", mock_qs):
                ctx = MagicMock()
                results = await search_locations.fn(ctx, query="zurich see")

        cities = [r["city"] for r in results]
        assert "Zürich" in cities

    @pytest.mark.asyncio
    async def test_search_locations_french_accents(self):
        from app.mcp.tools.locations import search_locations

        locations = [
            _make_location(id=2, city="Genève", country="CH",
                           water_name="Lac Léman", water_type="lake"),
        ]

        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: locations

        with patch("app.mcp.tools.locations.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Location.objects", mock_qs):
                ctx = MagicMock()
                results = await search_locations.fn(ctx, query="lac leman")

        water_names = [r["water_name"] for r in results]
        assert "Lac Léman" in water_names

    @pytest.mark.asyncio
    async def test_list_locations_with_search(self):
        from app.mcp.tools.locations import list_locations

        locations = [
            _make_location(id=1, city="Zürich", country="CH",
                           water_name="Zürichsee", water_type="lake"),
        ]

        mock_qs = MagicMock()
        mock_qs.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: locations

        with patch("app.mcp.tools.locations.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Location.objects", mock_qs):
                ctx = MagicMock()
                results = await list_locations.fn(ctx, search="zurich")

        cities = [r["city"] for r in results]
        assert "Zürich" in cities


class TestSearchOrganizersTools:
    """Test search_organizers and list_organizers search param."""

    @pytest.mark.asyncio
    async def test_search_organizers_fuzzy(self):
        from app.mcp.tools.organizers import search_organizers

        organizers = [
            _make_organizer(id=1, name="Swiss Aquatics Federation",
                            website="https://swiss-aquatics.ch",
                            slug="swiss-aquatics-federation"),
        ]

        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: organizers

        with patch("app.mcp.tools.organizers.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Organizer.objects", mock_qs):
                ctx = MagicMock()
                results = await search_organizers.fn(ctx, query="swiss aquatic")

        names = [r["name"] for r in results]
        assert "Swiss Aquatics Federation" in names

    @pytest.mark.asyncio
    async def test_list_organizers_with_search(self):
        from app.mcp.tools.organizers import list_organizers

        organizers = [
            _make_organizer(id=2, name="Deutscher Schwimmverband",
                            website="https://dsv.de",
                            slug="deutscher-schwimmverband"),
        ]

        mock_qs = MagicMock()
        mock_qs.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: organizers

        with patch("app.mcp.tools.organizers.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Organizer.objects", mock_qs):
                ctx = MagicMock()
                results = await list_organizers.fn(ctx, search="schwimm")

        names = [r["name"] for r in results]
        assert "Deutscher Schwimmverband" in names


class TestSearchRacesTools:
    """Test search_races and list_races search param."""

    @pytest.mark.asyncio
    async def test_search_races_by_event_name(self):
        from app.mcp.tools.races import search_races

        loc = _make_location(id=1, city="Zürich", country="CH")
        event = _make_event(id=1, name="Zürich Swim Classic", location=loc)
        races = [
            _make_race(id=1, event=event, name="Elite 5km", distance=5.0),
        ]

        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: races

        with patch("app.mcp.tools.races.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Race.objects", mock_qs):
                ctx = MagicMock()
                results = await search_races.fn(ctx, query="zurich swim")

        event_names = [r["event_name"] for r in results]
        assert "Zürich Swim Classic" in event_names

    @pytest.mark.asyncio
    async def test_list_races_with_search(self):
        from app.mcp.tools.races import list_races

        loc = _make_location(id=1, city="Zürich", country="CH")
        event = _make_event(id=1, name="Zürich Swim Classic", location=loc)
        races = [
            _make_race(id=1, event=event, name="Elite 5km", distance=5.0),
        ]

        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: races

        with patch("app.mcp.tools.races.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Race.objects", mock_qs):
                ctx = MagicMock()
                results = await list_races.fn(ctx, search="elite")

        names = [r["name"] for r in results]
        assert "Elite 5km" in names

    @pytest.mark.asyncio
    async def test_list_races_without_search(self):
        """Without search, races use date ordering, no fuzzy."""
        from app.mcp.tools.races import list_races

        loc = _make_location(id=1, city="Zürich", country="CH")
        event = _make_event(id=1, name="Event A", location=loc)
        races = [
            _make_race(id=1, event=event, name="Race A"),
        ]

        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: races

        with patch("app.mcp.tools.races.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Race.objects", mock_qs):
                ctx = MagicMock()
                results = await list_races.fn(ctx, limit=10)

        assert len(results) == 1
        mock_qs.order_by.assert_called_with('date', 'race_time')


# ── Haversine + coordinate search tests ─────────────────────────────


class TestHaversineKm:
    """Tests for the haversine_km utility function."""

    def test_same_point_is_zero(self):
        assert haversine_km(47.3769, 8.5417, 47.3769, 8.5417) == 0.0

    def test_zurich_to_bern(self):
        # Zürich (47.3769, 8.5417) to Bern (46.9480, 7.4474) ≈ 95 km
        d = haversine_km(47.3769, 8.5417, 46.9480, 7.4474)
        assert 90 < d < 105

    def test_zurich_to_geneva(self):
        # Zürich to Geneva ≈ 224 km
        d = haversine_km(47.3769, 8.5417, 46.2044, 6.1432)
        assert 220 < d < 230

    def test_symmetry(self):
        d1 = haversine_km(47.3769, 8.5417, 46.9480, 7.4474)
        d2 = haversine_km(46.9480, 7.4474, 47.3769, 8.5417)
        assert abs(d1 - d2) < 0.001


class TestSearchLocationsByCoordinates:
    """Test search_locations_by_coordinates tool."""

    @pytest.mark.asyncio
    async def test_finds_nearby_locations(self):
        from app.mcp.tools.locations import search_locations_by_coordinates

        # Zürich center: 47.3769, 8.5417
        # Location ~5km away
        locations = [
            _make_location(id=1, city="Zürich", country="CH",
                           water_name="Zürichsee", water_type="lake",
                           lat=47.3540, lng=8.5510),
            _make_location(id=2, city="Bern", country="CH",
                           water_name="Aare", water_type="river",
                           lat=46.9480, lng=7.4474),
        ]

        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: locations

        with patch("app.mcp.tools.locations.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Location.objects", mock_qs):
                ctx = MagicMock()
                results = await search_locations_by_coordinates.fn(
                    ctx, lat=47.3769, lng=8.5417, radius_km=10.0,
                )

        # Only Zürich should be within 10km, not Bern
        assert len(results) == 1
        assert results[0]["city"] == "Zürich"
        assert "distance_km" in results[0]
        assert results[0]["distance_km"] < 10.0

    @pytest.mark.asyncio
    async def test_large_radius_finds_all(self):
        from app.mcp.tools.locations import search_locations_by_coordinates

        locations = [
            _make_location(id=1, city="Zürich", country="CH",
                           lat=47.3769, lng=8.5417),
            _make_location(id=2, city="Bern", country="CH",
                           lat=46.9480, lng=7.4474),
        ]

        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: locations

        with patch("app.mcp.tools.locations.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Location.objects", mock_qs):
                ctx = MagicMock()
                results = await search_locations_by_coordinates.fn(
                    ctx, lat=47.3769, lng=8.5417, radius_km=200.0,
                )

        assert len(results) == 2
        # Should be sorted by distance (Zürich first, then Bern)
        assert results[0]["city"] == "Zürich"
        assert results[1]["city"] == "Bern"

    @pytest.mark.asyncio
    async def test_no_results_outside_radius(self):
        from app.mcp.tools.locations import search_locations_by_coordinates

        locations = [
            _make_location(id=1, city="Tokyo", country="JP",
                           lat=35.6762, lng=139.6503),
        ]

        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: locations

        with patch("app.mcp.tools.locations.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Location.objects", mock_qs):
                ctx = MagicMock()
                results = await search_locations_by_coordinates.fn(
                    ctx, lat=47.3769, lng=8.5417, radius_km=50.0,
                )

        assert results == []

    @pytest.mark.asyncio
    async def test_water_type_filter(self):
        from app.mcp.tools.locations import search_locations_by_coordinates

        locations = [
            _make_location(id=1, city="Zürich", country="CH",
                           water_name="Zürichsee", water_type="lake",
                           lat=47.3540, lng=8.5510),
        ]

        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: locations

        with patch("app.mcp.tools.locations.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Location.objects", mock_qs):
                ctx = MagicMock()
                results = await search_locations_by_coordinates.fn(
                    ctx, lat=47.3769, lng=8.5417, radius_km=10.0,
                    water_type="lake",
                )

        assert len(results) == 1
        # Verify water_type filter was called
        mock_qs.filter.assert_any_call(water_type="lake")


class TestListLocationsWithCoordinates:
    """Test list_locations with lat/lng/radius_km params."""

    @pytest.mark.asyncio
    async def test_list_with_coordinates(self):
        from app.mcp.tools.locations import list_locations

        locations = [
            _make_location(id=1, city="Zürich", country="CH",
                           water_name="Zürichsee", water_type="lake",
                           lat=47.3540, lng=8.5510),
            _make_location(id=2, city="Bern", country="CH",
                           water_name="Aare", water_type="river",
                           lat=46.9480, lng=7.4474),
        ]

        mock_qs = MagicMock()
        mock_qs.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: locations

        with patch("app.mcp.tools.locations.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Location.objects", mock_qs):
                ctx = MagicMock()
                results = await list_locations.fn(
                    ctx, lat=47.3769, lng=8.5417, radius_km=10.0,
                )

        # Only Zürich within 10km
        assert len(results) == 1
        assert results[0]["city"] == "Zürich"
        assert "distance_km" in results[0]

    @pytest.mark.asyncio
    async def test_list_with_coordinates_sorted_by_distance(self):
        from app.mcp.tools.locations import list_locations

        locations = [
            _make_location(id=2, city="Bern", country="CH",
                           lat=46.9480, lng=7.4474),
            _make_location(id=1, city="Zürich", country="CH",
                           lat=47.3540, lng=8.5510),
        ]

        mock_qs = MagicMock()
        mock_qs.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.__getitem__ = lambda self, s: locations

        with patch("app.mcp.tools.locations.sync_to_async",
                   side_effect=_fake_sync_to_async):
            with patch("app.models.Location.objects", mock_qs):
                ctx = MagicMock()
                results = await list_locations.fn(
                    ctx, lat=47.3769, lng=8.5417, radius_km=200.0,
                )

        # Zürich should come first (closer), then Bern
        assert len(results) == 2
        assert results[0]["city"] == "Zürich"
        assert results[1]["city"] == "Bern"
        assert results[0]["distance_km"] < results[1]["distance_km"]
