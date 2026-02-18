"""
Shared utilities for MCP tools.
"""
import math

from thefuzz import fuzz


def fuzzy_rank(items, key_func, query, cutoff=60):
    """
    Rank items by fuzzy match score against query.
    Returns items above cutoff, sorted by score descending.
    """
    scored = []
    for item in items:
        text = key_func(item)
        score = fuzz.WRatio(query, text) if text else 0
        if score >= cutoff:
            scored.append((score, item))
    scored.sort(key=lambda x: -x[0])
    return [item for _, item in scored]


def haversine_km(lat1, lng1, lat2, lng2):
    """
    Calculate the great-circle distance in km between two points
    on Earth using the Haversine formula.
    """
    R = 6371.0  # Earth radius in km
    lat1, lng1, lat2, lng2 = (math.radians(v) for v in (lat1, lng1, lat2, lng2))
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))
