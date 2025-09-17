from typing import Optional
from fastapi import UploadFile
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET = os.getenv("SUPABASE_BUCKET", "covers")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def upload_image(file: UploadFile) -> Optional[str]:
    if not supabase:
        return f"https://example.com/{file.filename}"  # fallback si no configuras supabase
    data = await file.read()
    supabase.storage.from_(BUCKET).upload(
        file=file.filename,
        file_options={"content-type": file.content_type, "upsert": True}
    )
    return supabase.storage.from_(BUCKET).get_public_url(file.filename)


