import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router

logger = logging.getLogger("ix-voice-ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"=== Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION} ===")
    logger.info(f"Mode: {settings.PIPELINE_MODE} | Device: {settings.DEVICE} | Model: {settings.HF_MODEL_ID}")
    yield
    logger.info(f"=== Shutting down {settings.SERVICE_NAME} ===")


app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.SERVICE_VERSION,
    description="Dedicated Speech Processing Microservice using faster-PhoWhisper-small",
    openapi_url="/api/v1/ai/openapi.json",
    docs_url="/api/v1/ai/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "docs": "/api/v1/ai/docs",
        "health": "/api/v1/ai/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
