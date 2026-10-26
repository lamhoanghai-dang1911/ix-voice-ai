from typing import List, Optional
from pydantic import BaseModel, Field


class WordSegment(BaseModel):
    word: str
    startMs: int
    endMs: int
    confidence: Optional[float] = None


class TranscriptSegment(BaseModel):
    id: str
    startMs: int
    endMs: int
    speakerId: str
    speakerLabel: str
    text: str
    confidence: float
    words: Optional[List[WordSegment]] = None


class QualityFlags(BaseModel):
    snrEstimateDb: Optional[float] = None
    lowConfidenceSegmentsCount: Optional[int] = 0
    averageConfidence: Optional[float] = 1.0


class TranscriptV01(BaseModel):
    jobId: str
    modelVersion: str
    language: str = "vi"
    qualityFlags: QualityFlags
    segments: List[TranscriptSegment]


class TranscribeRequest(BaseModel):
    jobId: str
    audioPath: Optional[str] = None
