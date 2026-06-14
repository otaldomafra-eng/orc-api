from fastapi import FastAPI

from app.api.admin import router as admin_router
from app.api.public import router as public_router
from app.errors import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="ORÇ_API", version="0.1.0")
    register_error_handlers(app)
    app.include_router(admin_router)
    app.include_router(public_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "orc-api"}

    return app


app = create_app()
