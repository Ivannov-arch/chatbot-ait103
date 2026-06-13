# placeholder_admin_directory.py
# modules/admin_directory.py
#
# Module 1 — Administrative & Campus Directory
#
# Knowledge scope:
#   - International & Student Affairs: office location, hours, email
#   - Registration & Payment: official links, anti-scam tips
#   - Accommodation Services: housing office location & hours
#
# This module provides helper functions that query the Supabase
# `knowledge_items` table filtered by module = "admin_directory".
#
# TODO: implement get_office_info(office_name: str) -> dict
# TODO: implement get_registration_links() -> list[dict]
# TODO: implement get_accommodation_contact() -> dict

MODULE_NAME = "admin_directory"


def get_office_info(office_name: str) -> dict:
    """
    Return contact details for a campus office by name.

    Args:
        office_name: e.g. "International Affairs", "Student Affairs"

    Returns:
        Dict with keys: name, location, hours, email
    """
    # PLACEHOLDER
    return {
        "name": office_name,
        "location": "[PLACEHOLDER] Not yet implemented",
        "hours": "[PLACEHOLDER] Not yet implemented",
        "email": "[PLACEHOLDER] Not yet implemented",
    }


def get_registration_links() -> list[dict]:
    """
    Return official registration and payment links.

    Returns:
        List of dicts with keys: title, url, notes
    """
    # PLACEHOLDER
    return []


def get_accommodation_contact() -> dict:
    """
    Return housing office contact and operating hours.

    Returns:
        Dict with keys: location, hours, phone, email
    """
    # PLACEHOLDER
    return {}
