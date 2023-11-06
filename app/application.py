from fastapi import FastAPI
from app.api.routes import property_router
from starlette.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="PropertyAPI")

    app.add_middleware(
        CORSMiddleware,
        allow_origins="*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(property_router)

    return app
