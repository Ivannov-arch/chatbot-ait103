# placeholder_academic_navigation.py
# modules/academic_navigation.py
#
# Module 3 — Academic Navigation
#
# Knowledge scope:
#   - AC System: login instructions and main feature overview
#   - Leave Application: how to apply (note: only accessible on campus Wi-Fi)
#   - Academic Calendar: how to download the school calendar
#
# This module provides helper functions that query the Supabase
# `knowledge_items` table filtered by module = "academic_navigation".
#
# TODO: implement get_ac_system_guide() -> dict
# TODO: implement get_leave_application_sop() -> dict
# TODO: implement get_academic_calendar_link() -> dict

MODULE_NAME = "academic_navigation"


def get_ac_system_guide() -> dict:
    """
    Return login steps and feature overview for the AC system.

    Returns:
        Dict with keys: url, login_steps (list), features (list)
    """
    # PLACEHOLDER
    return {
        "url": "[PLACEHOLDER]",
        "login_steps": ["[PLACEHOLDER] Not yet implemented"],
        "features": ["[PLACEHOLDER] Not yet implemented"],
    }


def get_leave_application_sop() -> dict:
    """
    Return the leave application procedure.

    Returns:
        Dict with keys: url, requires_campus_wifi (bool), steps (list)
    """
    # PLACEHOLDER
    return {
        "url": "[PLACEHOLDER]",
        "requires_campus_wifi": True,
        "steps": ["[PLACEHOLDER] Not yet implemented"],
    }


def get_academic_calendar_link() -> dict:
    """
    Return the academic calendar download information.

    Returns:
        Dict with keys: url, format, notes
    """
    # PLACEHOLDER
    return {
        "url": "[PLACEHOLDER]",
        "format": "PDF",
        "notes": "[PLACEHOLDER] Not yet implemented",
    }
