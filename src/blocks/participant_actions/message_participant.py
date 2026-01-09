"""
MessageParticipant - Play prompt / send message to participant.
https://docs.aws.amazon.com/connect/latest/APIReference/participant-actions-messageparticipant.html
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
import uuid
from ..base import FlowBlock
from ..types import Media


@dataclass
class MessageParticipant(FlowBlock):
    """
    Send a message to the participant.

    For voice contacts, plays an audio prompt or text-to-speech.
    For other channels, sends a text message.

    Parameters are mutually exclusive: use only one of text, prompt_id, ssml, or media.

    Errors:
        - NoMatchingError: If an error occurred and no other error matched

    Restrictions:
        - PromptId and SSML: Voice channel only
        - Text: All channels
        - Not supported in hold flows
    """
    text: Optional[str] = None
    prompt_id: Optional[str] = None
    ssml: Optional[str] = None
    media: Optional[Media] = None

    def __post_init__(self):
        self.type = "MessageParticipant"
        self._build_parameters()

    def _build_parameters(self):
        """Build parameters dict from typed attributes."""
        # Clear and rebuild to ensure consistency
        params = {}
        if self.text is not None:
            params["Text"] = self.text
        if self.prompt_id is not None:
            params["PromptId"] = self.prompt_id
        if self.ssml is not None:
            params["SSML"] = self.ssml
        if self.media is not None:
            params["Media"] = self.media.to_dict()
        self.parameters = params

    def to_dict(self) -> dict:
        self._build_parameters()
        return super().to_dict()

    @classmethod
    def from_dict(cls, data: dict) -> 'MessageParticipant':
        params = data.get("Parameters", {})
        media_data = params.get("Media")
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            text=params.get("Text"),
            prompt_id=params.get("PromptId"),
            ssml=params.get("SSML"),
            media=Media.from_dict(media_data) if media_data else None,
            parameters=params,
            transitions=data.get("Transitions", {})
        )
