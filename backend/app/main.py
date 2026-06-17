from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


LOCAL_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def create_app() -> FastAPI:
    app = FastAPI(title="Bilingual Meeting Copilot API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=LOCAL_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )
    app.include_router(router)
    return app


app = create_app()

