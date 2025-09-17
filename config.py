
import os
from dotenv import load_dotenv

load_dotenv()

# Construir la URL de conexión usando las variables de Clever Cloud
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{os.getenv('POSTGRESQL_ADDON_USER')}:{os.getenv('POSTGRESQL_ADDON_PASSWORD')}@{os.getenv('POSTGRESQL_ADDON_HOST')}:{os.getenv('POSTGRESQL_ADDON_PORT')}/{os.getenv('POSTGRESQL_ADDON_DB')}"
)

# También puedes usar directamente POSTGRESQL_ADDON_URI añadiendo el driver asyncpg
# DATABASE_URL = os.getenv('POSTGRESQL_ADDON_URI', '').replace('postgresql://', 'postgresql+asyncpg://')

JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
JWT_ALG = "HS256"