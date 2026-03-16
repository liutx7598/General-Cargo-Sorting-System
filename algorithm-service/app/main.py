from fastapi import FastAPI

from app.api.routes import router as solver_router
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title="Stowage Algorithm Service",
    version="0.1.0",
    description="General cargo intelligent stowage solver",
)
app.include_router(solver_router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Return service health."""
    return {"status": "ok", "service": settings.service_name}

