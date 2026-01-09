"""
Wait - Wait block for pausing flow execution.
https://docs.aws.amazon.com/connect/latest/APIReference/flow-control-actions-wait.html
"""
from dataclasses import dataclass
from typing import List, Optional
import uuid
from ..base import FlowBlock


@dataclass
class Wait(FlowBlock):
    """Wait block for pausing flow execution."""
    time_limit_seconds: str = "60"
    events: Optional[List[str]] = None

    def __post_init__(self):
        self.type = "Wait"
        if not self.parameters:
            self.parameters = {}
        if self.time_limit_seconds:
            self.parameters["TimeLimitSeconds"] = self.time_limit_seconds
        if self.events:
            self.parameters["Events"] = self.events

    def to_dict(self) -> dict:
        data = super().to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Wait':
        params = data.get("Parameters", {})
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            time_limit_seconds=params.get("TimeLimitSeconds", "60"),
            events=params.get("Events", []),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
