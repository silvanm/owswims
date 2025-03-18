import os
import json
from typing import Dict, List, Optional

# Directory containing profile JSON files
PROFILES_DIR = os.path.dirname(os.path.abspath(__file__))


def get_available_profiles() -> List[str]:
    """Return a list of available profile IDs (filenames without extension)"""
    profiles = []
    for filename in os.listdir(PROFILES_DIR):
        if filename.endswith(".json"):
            profiles.append(filename[:-5])  # Remove .json extension
    return profiles


def get_profile(profile_id: str) -> Optional[Dict]:
    """Load a profile by ID"""
    profile_path = os.path.join(PROFILES_DIR, f"{profile_id}.json")

    if not os.path.exists(profile_path):
        return None

    try:
        with open(profile_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None
