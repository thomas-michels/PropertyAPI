from fastapi import FastAPI
from app.core.db import lifespan
from app.api.routes import property_router
from app.api.dependencies import startup
from starlette.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="PropertyAPI",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins="*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(property_router)

    return app
