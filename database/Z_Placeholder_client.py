# placeholder_client.py
# database/client.py
#
# Supabase client singleton.
#
# Returns a single shared Supabase client instance so we don't
# create a new connection on every request.
#
# Usage:
#   from database.client import get_client
#   sb = get_client()
#   result = sb.table("knowledge_items").select("*").execute()
#
# Reads credentials from environment variables:
#   SUPABASE_URL          — project URL
#   SUPABASE_ANON_KEY     — public anon key (for normal queries)
#   SUPABASE_SERVICE_ROLE_KEY — service role key (for seeding only)
#
# TODO: implement get_client() using supabase-py create_client()
# TODO: implement get_admin_client() using service role key (seeding only)

from __future__ import annotations

_client = None        # lazy-initialised singleton
_admin_client = None  # service-role client (seeding only)


def get_client():
    """
    Return the shared Supabase anon client.
    Initialised once on first call (lazy singleton).

    Returns:
        supabase.Client instance
    """
    # PLACEHOLDER — replace with real implementation
    # from supabase import create_client
    # import os
    # global _client
    # if _client is None:
    #     _client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
    # return _client
    raise NotImplementedError("[PLACEHOLDER] get_client() not yet implemented.")


def get_admin_client():
    """
    Return a Supabase client authenticated with the service role key.
    Use ONLY for seeding / admin operations — never expose to end users.

    Returns:
        supabase.Client instance with service role privileges
    """
    # PLACEHOLDER
    raise NotImplementedError("[PLACEHOLDER] get_admin_client() not yet implemented.")
