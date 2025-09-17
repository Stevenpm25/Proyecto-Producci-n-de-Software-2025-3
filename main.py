# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from db import init_db
from routers.users_router import router as users_router
from routers.works_router import router as works_router
from routers.subscriptions_router import router as subs_router
from routers.loans_router import router as loans_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa la base de datos al iniciar la app
    await init_db()
    yield
    # Aquí podrías cerrar conexiones u otras tareas de apagado


app = FastAPI(
    title="BIDA - Biblioteca Digital con Acceso Diferenciado",
    version="0.1.0",
    lifespan=lifespan,
)

# --- CORS (abierto para desarrollo local) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # En producción, restringe a tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static (opcional) ---
# Si creas una carpeta ./static, se servirá en /static
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    # Si no existe la carpeta, no montamos nada (no es crítico)
    pass

# --- Routers del proyecto ---
app.include_router(users_router,         prefix="/users",         tags=["users"])
app.include_router(works_router,         prefix="/works",         tags=["works"])
app.include_router(subs_router,          prefix="/subscriptions", tags=["subscriptions"])
app.include_router(loans_router,         prefix="/loans",         tags=["loans"])


# --- Health & Root ---
@app.get("/", tags=["health"])
async def root():
    return {
        "name": "BIDA API",
        "version": app.version,
        "docs": "/docs",
        "redoc": "/redoc",
        "routers": ["/users", "/works", "/subscriptions", "/loans"],
        "status": "ok",
    }

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


