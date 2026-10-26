from pydantic import BaseModel
from typing import Any, TypeVar, Callable, Type, cast
from uuid import UUID


T = TypeVar("T")


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_float(x: Any) -> float:
    assert isinstance(x, (int, float))
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> list[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class QualityFlags(BaseModel):
    average_confidence: float | None = None
    low_confidence_segments_count: int | None = None
    snr_estimate_db: float | None = None

    @staticmethod
    def from_dict(obj: Any) -> 'QualityFlags':
        assert isinstance(obj, dict)
        average_confidence = from_union([from_float, from_none], obj.get("averageConfidence"))
        low_confidence_segments_count = from_union([from_int, from_none], obj.get("lowConfidenceSegmentsCount"))
        snr_estimate_db = from_union([from_float, from_none], obj.get("snrEstimateDb"))
        return QualityFlags(average_confidence, low_confidence_segments_count, snr_estimate_db)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.average_confidence is not None:
            result["averageConfidence"] = from_union([to_float, from_none], self.average_confidence)
        if self.low_confidence_segments_count is not None:
            result["lowConfidenceSegmentsCount"] = from_union([from_int, from_none], self.low_confidence_segments_count)
        if self.snr_estimate_db is not None:
            result["snrEstimateDb"] = from_union([to_float, from_none], self.snr_estimate_db)
        return result


class Word(BaseModel):
    end_ms: int
    start_ms: int
    word: str
    confidence: float | None = None

    @staticmethod
    def from_dict(obj: Any) -> 'Word':
        assert isinstance(obj, dict)
        end_ms = from_int(obj.get("endMs"))
        start_ms = from_int(obj.get("startMs"))
        word = from_str(obj.get("word"))
        confidence = from_union([from_float, from_none], obj.get("confidence"))
        return Word(end_ms, start_ms, word, confidence)

    def to_dict(self) -> dict:
        result: dict = {}
        result["endMs"] = from_int(self.end_ms)
        result["startMs"] = from_int(self.start_ms)
        result["word"] = from_str(self.word)
        if self.confidence is not None:
            result["confidence"] = from_union([to_float, from_none], self.confidence)
        return result


class Segment(BaseModel):
    confidence: float
    end_ms: int
    id: str
    speaker_id: str
    speaker_label: str
    start_ms: int
    text: str
    words: list[Word] | None = None

    @staticmethod
    def from_dict(obj: Any) -> 'Segment':
        assert isinstance(obj, dict)
        confidence = from_float(obj.get("confidence"))
        end_ms = from_int(obj.get("endMs"))
        id = from_str(obj.get("id"))
        speaker_id = from_str(obj.get("speakerId"))
        speaker_label = from_str(obj.get("speakerLabel"))
        start_ms = from_int(obj.get("startMs"))
        text = from_str(obj.get("text"))
        words = from_union([lambda x: from_list(Word.from_dict, x), from_none], obj.get("words"))
        return Segment(confidence, end_ms, id, speaker_id, speaker_label, start_ms, text, words)

    def to_dict(self) -> dict:
        result: dict = {}
        result["confidence"] = to_float(self.confidence)
        result["endMs"] = from_int(self.end_ms)
        result["id"] = from_str(self.id)
        result["speakerId"] = from_str(self.speaker_id)
        result["speakerLabel"] = from_str(self.speaker_label)
        result["startMs"] = from_int(self.start_ms)
        result["text"] = from_str(self.text)
        if self.words is not None:
            result["words"] = from_union([lambda x: from_list(lambda x: to_class(Word, x), x), from_none], self.words)
        return result


class TranscriptV01_Gen(BaseModel):
    """Canonical contract for timestamped and speaker-attributed Vietnamese transcripts"""

    job_id: UUID
    model_version: str
    quality_flags: QualityFlags
    segments: list[Segment]
    language: str | None = None

    @staticmethod
    def from_dict(obj: Any) -> 'TranscriptV01_Gen':
        assert isinstance(obj, dict)
        job_id = UUID(obj.get("jobId"))
        model_version = from_str(obj.get("modelVersion"))
        quality_flags = QualityFlags.from_dict(obj.get("qualityFlags"))
        segments = from_list(Segment.from_dict, obj.get("segments"))
        language = from_union([from_str, from_none], obj.get("language"))
        return TranscriptV01_Gen(job_id, model_version, quality_flags, segments, language)

    def to_dict(self) -> dict:
        result: dict = {}
        result["jobId"] = str(self.job_id)
        result["modelVersion"] = from_str(self.model_version)
        result["qualityFlags"] = to_class(QualityFlags, self.quality_flags)
        result["segments"] = from_list(lambda x: to_class(Segment, x), self.segments)
        if self.language is not None:
            result["language"] = from_union([from_str, from_none], self.language)
        return result


def transcript_v01_gen_from_dict(s: Any) -> TranscriptV01_Gen:
    return TranscriptV01_Gen.from_dict(s)


def transcript_v01_gen_to_dict(x: TranscriptV01_Gen) -> Any:
    return to_class(TranscriptV01_Gen, x)
