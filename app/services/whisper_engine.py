import os
import json
import logging
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models.contracts import TranscriptV01, TranscriptSegment, QualityFlags, WordSegment

logger = logging.getLogger("ix-voice-ai")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class WhisperEngine:
    _instance: Optional["WhisperEngine"] = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WhisperEngine, cls).__new__(cls)
        return cls._instance

    def _get_model(self):
        if self._model is None and settings.PIPELINE_MODE == "real":
            try:
                from faster_whisper import WhisperModel
                logger.info(
                    f"[WhisperEngine] Loading model '{settings.HF_MODEL_ID}' "
                    f"on device={settings.DEVICE}, compute_type={settings.COMPUTE_TYPE}..."
                )
                self._model = WhisperModel(
                    settings.HF_MODEL_ID,
                    device=settings.DEVICE,
                    compute_type=settings.COMPUTE_TYPE,
                    download_root=str(settings.MODELS_CACHE_DIR),
                )
                logger.info("[WhisperEngine] Model loaded successfully.")
            except Exception as e:
                logger.error(f"[WhisperEngine] Failed to load model '{settings.HF_MODEL_ID}': {e}")
                raise e
        return self._model

    def transcribe(self, audio_path: str, job_id: str) -> TranscriptV01:
        """
        Transcribes the given audio file and returns a canonical TranscriptV01.
        """
        if settings.PIPELINE_MODE == "mock":
            return self._transcribe_mock(job_id)
        else:
            return self._transcribe_real(audio_path, job_id)

    def _transcribe_mock(self, job_id: str) -> TranscriptV01:
        logger.info(f"[WhisperEngine] [MOCK MODE] Loading canonical fixture for job {job_id}")
        fixture_path = settings.FIXTURES_DIR / "mock_transcript.json"

        if not fixture_path.exists():
            # Fallback path if running in Docker
            alt_path = Path("/app/contracts/fixtures/mock_transcript.json")
            if alt_path.exists():
                fixture_path = alt_path

        if fixture_path.exists():
            with open(fixture_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["jobId"] = job_id
            return TranscriptV01(**data)

        # Default minimal fallback
        return TranscriptV01(
            jobId=job_id,
            modelVersion="Mock-PhoWhisper-v0.1",
            language="vi",
            qualityFlags=QualityFlags(snrEstimateDb=20.0, averageConfidence=0.95),
            segments=[
                TranscriptSegment(
                    id="seg-001",
                    startMs=0,
                    endMs=4500,
                    speakerId="SPEAKER_01",
                    speakerLabel="Tư vấn viên",
                    text="Dạ em chào anh, em là tư vấn viên từ Integrix IX.Voice.",
                    confidence=0.98,
                )
            ],
        )

    def _transcribe_real(self, audio_path: str, job_id: str) -> TranscriptV01:
        logger.info(f"[WhisperEngine] [REAL MODE] Transcribing file: {audio_path} for job {job_id}")
        p = Path(audio_path)
        if not p.exists():
            raise FileNotFoundError(f"Audio file not found at: {audio_path}")

        model = self._get_model()
        segments_generator, info = model.transcribe(
            str(p),
            language="vi",
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        segments = []
        seg_idx = 1
        total_conf = 0.0
        low_conf_count = 0

        for s in segments_generator:
            start_ms = int(s.start * 1000)
            end_ms = int(s.end * 1000)
            text = s.text.strip()
            # Calculate segment average confidence
            conf = 0.95
            words_list = []
            if s.words:
                word_confs = [w.probability for w in s.words if w.probability is not None]
                if word_confs:
                    conf = round(sum(word_confs) / len(word_confs), 3)
                words_list = [
                    WordSegment(
                        word=w.word.strip(),
                        startMs=int(w.start * 1000),
                        endMs=int(w.end * 1000),
                        confidence=round(w.probability, 3) if w.probability is not None else None,
                    )
                    for w in s.words
                ]

            if conf < 0.7:
                low_conf_count += 1
            total_conf += conf

            # Basic speaker alternating heuristic (until Pyannote pipeline integration)
            speaker_id = f"SPEAKER_{(seg_idx % 2) + 1:02d}"
            speaker_label = "Tư vấn viên" if speaker_id == "SPEAKER_01" else "Khách hàng"

            segments.append(
                TranscriptSegment(
                    id=f"seg-{seg_idx:03d}",
                    startMs=start_ms,
                    endMs=end_ms,
                    speakerId=speaker_id,
                    speakerLabel=speaker_label,
                    text=text,
                    confidence=conf,
                    words=words_list if words_list else None,
                )
            )
            seg_idx += 1

        avg_conf = round(total_conf / len(segments), 3) if segments else 1.0

        return TranscriptV01(
            jobId=job_id,
            modelVersion=f"{settings.HF_MODEL_ID} ({settings.DEVICE}/{settings.COMPUTE_TYPE})",
            language=info.language if hasattr(info, "language") and info.language else "vi",
            qualityFlags=QualityFlags(
                snrEstimateDb=25.0,
                lowConfidenceSegmentsCount=low_conf_count,
                averageConfidence=avg_conf,
            ),
            segments=segments,
        )


whisper_engine = WhisperEngine()
