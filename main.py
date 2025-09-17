# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

import logging_conf  # configura logging básico

from db import init_db
from routers.users_router import router as users_router
from routers.works_router import router as works_router
from routers.subscriptions_router import router as subs_router
from routers.loans_router import router as loans_router
from routers.auth_router import router as auth_router

from utils.errors import http_exception_handler, validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from jobs.expiry import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa la base de datos y arranca el scheduler de expiración de préstamos
    await init_db()
    task = start_scheduler()
    try:
        yield
    finally:
        stop_scheduler(task)


app = FastAPI(
    title="BIDA - Biblioteca Digital con Acceso Diferenciado",
    version="0.1.0",
    lifespan=lifespan,
)

# --- Manejadores de errores globales ---
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# --- CORS (abierto para desarrollo; restringe en producción) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static (opcional) ---
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    # Si no existe la carpeta, se omite sin romper la app
    pass

# --- Routers del proyecto ---
app.include_router(auth_router,        prefix="/auth",          tags=["auth"])
app.include_router(users_router,       prefix="/users",         tags=["users"])
app.include_router(works_router,       prefix="/works",         tags=["works"])
app.include_router(subs_router,        prefix="/subscriptions", tags=["subscriptions"])
app.include_router(loans_router,       prefix="/loans",         tags=["loans"])

# --- Health & Root ---
@app.get("/", tags=["health"])
async def root():
    return {
        "name": "BIDA API",
        "version": app.version,
        "docs": "/docs",
        "redoc": "/redoc",
        "routers": ["/auth", "/users", "/works", "/subscriptions", "/loans"],
        "status": "ok",
    }

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
