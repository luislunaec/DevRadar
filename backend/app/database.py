from supabase import create_client, Client
import os


_SUPABASE_CLIENT: Client | None = None


def get_supabase() -> Client:
    """
    Retorna un cliente singleton de Supabase.
    """
    global _SUPABASE_CLIENT

    if _SUPABASE_CLIENT is None:
        _SUPABASE_CLIENT = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY"),
        )

    return _SUPABASE_CLIENT
