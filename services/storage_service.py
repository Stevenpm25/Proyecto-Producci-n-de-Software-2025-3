# Subida de imágenes (Supabase opcional). No falla si no configuras claves.
from typing import Optional
from fastapi import UploadFile
import os

_SUPABASE_AVAILABLE = False
try:
    from supabase import create_client, Client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Optional["Client"] = create_client(SUPABASE_URL, SUPABASE_KEY)
        _SUPABASE_AVAILABLE = True
    else:
        supabase = None
except Exception:
    supabase = None

async def upload_image(file: UploadFile) -> Optional[str]:
    # Si tienes Supabase configurado:
    if _SUPABASE_AVAILABLE and supabase:
        bucket = os.getenv("SUPABASE_BUCKET", "covers")
        data = await file.read()
        path = f"{bucket}/{file.filename}"
        # SDK v2: storage desde client.storage
        supabase.storage.from_(bucket).upload(file=file.file, path=file.filename, file_options={"content-type": file.content_type})
        return supabase.storage.from_(bucket).get_public_url(file.filename)
    # Si no, devuelve URL “mock” para no romper el flujo
    return f"https://example.com/{file.filename}"
