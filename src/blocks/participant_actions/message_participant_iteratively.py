"""
MessageParticipantIteratively - Play multiple messages in sequence (loop prompts).
https://docs.aws.amazon.com/connect/latest/APIReference/participant-actions-messageparticipantiteratively.html
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import uuid
from ..base import FlowBlock


@dataclass
class MessageParticipantIteratively(FlowBlock):
    """
    Play multiple messages in sequence.

    Each message in the list can have Text, PromptId, SSML, or Media.
    If InterruptFrequencySeconds is set, the action completes with
    'MessagesInterrupted' result when the timeout elapses.

    Results:
        - MessagesInterrupted: Returned when InterruptFrequencySeconds timeout elapses

    Errors:
        - NoMatchingError: If an error occurred and no other error matched

    Restrictions:
        - Supported in: Customer Queue, Customer Hold, Agent Hold flows
        - PromptId: Voice channel only
        - Chat channel: Action immediately takes error branch
    """
    messages: Optional[List[Dict[str, Any]]] = None
    interrupt_frequency_seconds: Optional[str] = None

    def __post_init__(self):
        self.type = "MessageParticipantIteratively"
        self._build_parameters()

    def _build_parameters(self):
        """Build parameters dict from typed attributes."""
        params = {}
        if self.messages is not None:
            params["Messages"] = self.messages
        if self.interrupt_frequency_seconds is not None:
            params["InterruptFrequencySeconds"] = self.interrupt_frequency_seconds
        self.parameters = params

    def to_dict(self) -> dict:
        self._build_parameters()
        return super().to_dict()

    @classmethod
    def from_dict(cls, data: dict) -> 'MessageParticipantIteratively':
        params = data.get("Parameters", {})
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            messages=params.get("Messages"),
            interrupt_frequency_seconds=params.get("InterruptFrequencySeconds"),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
