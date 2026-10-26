from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional

from app.config import settings
from app.models.contracts import TranscriptV01, TranscribeRequest
from app.services.whisper_engine import whisper_engine

router = APIRouter(prefix="/api/v1/ai", tags=["Speech AI"])


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "pipelineMode": settings.PIPELINE_MODE,
        "device": settings.DEVICE,
        "computeType": settings.COMPUTE_TYPE,
        "modelId": settings.HF_MODEL_ID,
    }


@router.post("/transcribe", response_model=TranscriptV01)
def transcribe_json(payload: TranscribeRequest):
    """
    Transcribes audio file referenced by path (shared volume) or mock.
    """
    job_id = payload.jobId
    audio_path = payload.audioPath

    if settings.PIPELINE_MODE != "mock":
        if not audio_path:
            raise HTTPException(status_code=400, detail="audioPath is required in real mode")
        
        # Resolve path
        path_obj = Path(audio_path)
        if not path_obj.is_absolute():
            # If relative, check against STORAGE_DIR or BASE_DIR
            alt1 = settings.STORAGE_DIR / audio_path
            alt2 = settings.BASE_DIR / audio_path
            if alt1.exists():
                audio_path = str(alt1)
            elif alt2.exists():
                audio_path = str(alt2)

        if not Path(audio_path).exists():
            raise HTTPException(status_code=404, detail=f"Audio file not found: {audio_path}")

    try:
        transcript = whisper_engine.transcribe(audio_path or "", job_id)
        return transcript
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/transcribe-upload", response_model=TranscriptV01)
async def transcribe_upload(
    jobId: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Direct upload endpoint for testing or decoupled environments without shared volume.
    """
    save_dir = settings.STORAGE_DIR / jobId
    save_dir.mkdir(parents=True, exist_ok=True)
    temp_file = save_dir / (file.filename or "audio.wav")

    content = await file.read()
    with open(temp_file, "wb") as f:
        f.write(content)

    try:
        transcript = whisper_engine.transcribe(str(temp_file), jobId)
        return transcript
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
