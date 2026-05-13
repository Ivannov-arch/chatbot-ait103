# placeholder_campus_life.py
# modules/campus_life.py
#
# Module 2 — Daily Campus Life & Facilities
#
# Knowledge scope:
#   - Wi-Fi Connection: login guidance for campus network
#   - Canteen Guidance: locations, hours, food types (Chinese, Western, Halal, vegetarian)
#   - Accommodation Guidance: hostel rules, maintenance application SOP
#   - Library Services: hours, rules, borrow/return SOP
#
# This module provides helper functions that query the Supabase
# `knowledge_items` table filtered by module = "campus_life".
#
# TODO: implement get_wifi_guide() -> dict
# TODO: implement get_canteen_info(filter_type: str | None) -> list[dict]
# TODO: implement get_hostel_rules() -> list[str]
# TODO: implement get_library_info() -> dict

MODULE_NAME = "campus_life"


def get_wifi_guide() -> dict:
    """
    Return step-by-step Wi-Fi login instructions.

    Returns:
        Dict with keys: ssid, steps (list of str), notes
    """
    # PLACEHOLDER
    return {
        "ssid": "[PLACEHOLDER]",
        "steps": ["[PLACEHOLDER] Not yet implemented"],
        "notes": "",
    }


def get_canteen_info(filter_type: str | None = None) -> list[dict]:
    """
    Return canteen listings, optionally filtered by food type.

    Args:
        filter_type: e.g. "Halal", "Western", "Chinese", "vegetarian", or None for all.

    Returns:
        List of dicts with keys: name, location, hours, food_types
    """
    # PLACEHOLDER
    return []


def get_hostel_rules() -> list[str]:
    """
    Return the list of accommodation rules as plain strings.

    Returns:
        List of rule strings.
    """
    # PLACEHOLDER
    return ["[PLACEHOLDER] Hostel rules not yet implemented."]


def get_library_info() -> dict:
    """
    Return library hours, borrowing rules, and SOP.

    Returns:
        Dict with keys: location, hours (dict), borrow_sop (list), return_sop (list)
    """
    # PLACEHOLDER
    return {}
