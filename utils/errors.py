from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse({"error": "Invalid request", "details": exc.errors()}, status_code=422)
