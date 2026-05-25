"""Application exception handlers."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.utils.exceptions import AuthorizationException, AuthenticationException, ConflictError, DefectIQException, NotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DefectIQException)
    async def defectiq_exception_handler(request: Request, exc: DefectIQException):
        if isinstance(exc, AuthenticationException):
            status_code = 401
        elif isinstance(exc, AuthorizationException):
            status_code = 403
        elif isinstance(exc, NotFoundError):
            status_code = 404
        elif isinstance(exc, ConflictError):
            status_code = 409
        else:
            status_code = 400
        return JSONResponse(status_code=status_code, content={"detail": str(exc) or exc.__class__.__name__})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
