"""
Helper script to pre-download ntgiaky/faster-PhoWhisper-small from Hugging Face into local data/models directory.
"""
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("download_model")

MODEL_ID = "ntgiaky/faster-PhoWhisper-small"
MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def download_model():
    logger.info(f"Target download folder: {MODELS_DIR.resolve()}")
    logger.info(f"Downloading/Caching model: '{MODEL_ID}' from Hugging Face...")

    try:
        from faster_whisper import WhisperModel
        # Initialize model which automatically downloads and caches into download_root
        model = WhisperModel(MODEL_ID, device="cpu", compute_type="int8", download_root=str(MODELS_DIR))
        logger.info(f"Model '{MODEL_ID}' downloaded and verified successfully in: {MODELS_DIR}")
    except ImportError:
        logger.error("faster-whisper is not installed. Please run: pip install faster-whisper")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    download_model()
