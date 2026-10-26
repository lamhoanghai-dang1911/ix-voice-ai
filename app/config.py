import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIServiceSettings(BaseSettings):
    SERVICE_NAME: str = "IX.VOICE Speech AI Service"
    SERVICE_VERSION: str = "0.1.0"
    API_PORT: int = 5000
    API_HOST: str = "0.0.0.0"

    # Pipeline Mode: "mock" (offline fixtures) or "real" (faster-PhoWhisper-small)
    PIPELINE_MODE: str = os.getenv("PIPELINE_MODE", "mock")

    # Hardware & Inference Settings
    DEVICE: str = os.getenv("DEVICE", "cpu")  # "cpu" or "cuda"
    COMPUTE_TYPE: str = os.getenv("COMPUTE_TYPE", "int8")  # "int8" for CPU, "float16" for GPU
    HF_MODEL_ID: str = os.getenv("HF_MODEL_ID", "ntgiaky/faster-PhoWhisper-small")

    # Storage & Cache Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = Path(os.getenv("STORAGE_LOCAL_DIR", "./data/storage"))
    MODELS_CACHE_DIR: Path = Path(os.getenv("MODELS_CACHE_DIR", "./data/models"))
    FIXTURES_DIR: Path = BASE_DIR / "contracts" / "fixtures"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = AIServiceSettings()

# Ensure directories exist
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
