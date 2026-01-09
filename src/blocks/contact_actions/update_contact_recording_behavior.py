"""
UpdateContactRecordingBehavior - Update contact recording behavior.
https://docs.aws.amazon.com/connect/latest/APIReference/contact-actions-updatecontactrecordingbehavior.html
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
import uuid
from ..base import FlowBlock


@dataclass
class UpdateContactRecordingBehavior(FlowBlock):
    """Update contact recording behavior."""
    recording_behavior: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        self.type = "UpdateContactRecordingBehavior"
        if self.recording_behavior and "RecordingBehavior" not in self.parameters:
            self.parameters["RecordingBehavior"] = self.recording_behavior

    def to_dict(self) -> dict:
        data = super().to_dict()
        if self.recording_behavior:
            data["Parameters"]["RecordingBehavior"] = self.recording_behavior
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'UpdateContactRecordingBehavior':
        params = data.get("Parameters", {})
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            recording_behavior=params.get("RecordingBehavior"),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
