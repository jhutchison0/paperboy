"""
Text-to-Speech interface — pluggable audio generation.

Currently provides:
  - NotebookLMExporter: Formats briefings for NotebookLM upload
  - TTSProvider (abstract): Interface for future ElevenLabs integration

The TTS layer is intentionally minimal right now. The pipeline
outputs markdown briefings that you upload to NotebookLM manually.
When you're ready for ElevenLabs, implement ElevenLabsTTS and
the pipeline will handle voice generation and audio stitching.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.models import BriefingDocument


class TTSProvider(ABC):
    """
    Abstract base for text-to-speech providers.

    Implement this interface to add new TTS backends
    (ElevenLabs, OpenAI TTS, edge-tts, etc.)
    """

    @abstractmethod
    def synthesize(self, text: str, voice_id: str) -> bytes:
        """
        Convert text to audio bytes.

        Args:
            text: The text to speak.
            voice_id: Provider-specific voice identifier.

        Returns:
            Audio data as bytes (typically MP3).
        """
        pass

    @abstractmethod
    def available_voices(self) -> list[dict]:
        """
        List available voices.

        Returns:
            List of dicts with at least 'id' and 'name' keys.
        """
        pass


@dataclass
class VoiceConfig:
    """Configuration for a podcast voice."""
    role: str  # "guide" or "challenger"
    voice_id: str
    name: str
    description: str = ""


class ElevenLabsTTS(TTSProvider):
    """
    ElevenLabs TTS integration (stub — ready for implementation).

    When you're ready to add ElevenLabs:
    1. uv pip install elevenlabs
    2. Set ELEVENLABS_API_KEY in .env
    3. Implement synthesize() and available_voices()
    4. Add voice stitching in PodcastAudioGenerator

    Estimated cost at $22/month (100k chars):
      ~3-4 episodes per month at 27k chars/episode.
    For daily use, the $99/month Scale plan covers ~18 episodes.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        # Future: from elevenlabs import ElevenLabs
        # self.client = ElevenLabs(api_key=api_key)

    def synthesize(self, text: str, voice_id: str) -> bytes:
        raise NotImplementedError(
            "ElevenLabs TTS is not yet implemented. "
            "Use NotebookLM for audio generation, or implement this method. "
            "See the docstring for setup instructions."
        )

    def available_voices(self) -> list[dict]:
        raise NotImplementedError("ElevenLabs TTS is not yet implemented.")


class NotebookLMExporter:
    """
    Prepares briefing documents for Google NotebookLM upload.

    NotebookLM generates a ~15-20 minute podcast from uploaded documents.
    The briefing's structure (sections, challenges, questions) is designed
    to steer NotebookLM toward 3Blue1Brown-style dialogue.

    Usage:
        exporter = NotebookLMExporter()
        markdown = exporter.export(briefing)
        # Then upload the markdown file to NotebookLM manually
    """

    def export(self, briefing: BriefingDocument) -> str:
        """
        Format the briefing for optimal NotebookLM consumption.

        Currently returns the briefing as-is, since the distiller
        already optimizes for NotebookLM. Future versions could
        add NotebookLM-specific formatting hints.
        """
        return briefing.content

    def export_to_file(self, briefing: BriefingDocument, output_path: Path) -> Path:
        """Save the briefing as a file ready for NotebookLM upload."""
        content = self.export(briefing)
        output_path.write_text(content, encoding="utf-8")
        return output_path


class PodcastAudioGenerator:
    """
    Future: Generate two-voice podcast audio from a briefing.

    This would:
    1. Parse the briefing into speaker segments (guide vs challenger)
    2. Generate audio for each segment using different TTS voices
    3. Stitch segments together with pydub
    4. Add intro/outro music (optional)
    5. Export as MP3

    Not implemented yet — use NotebookLM for audio generation.
    """

    def __init__(self, tts_provider: TTSProvider, guide_voice: VoiceConfig, challenger_voice: VoiceConfig):
        self.tts = tts_provider
        self.guide_voice = guide_voice
        self.challenger_voice = challenger_voice

    def generate(self, briefing: BriefingDocument) -> bytes:
        """Generate full podcast audio from a briefing."""
        raise NotImplementedError(
            "Two-voice audio generation is not yet implemented. "
            "Use NotebookLM for podcast generation."
        )
