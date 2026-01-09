"""
CheckHoursOfOperation - Check if within hours of operation.
https://docs.aws.amazon.com/connect/latest/APIReference/flow-control-actions-checkhoursofoperation.html
"""
from dataclasses import dataclass
import uuid
from ..base import FlowBlock


@dataclass
class CheckHoursOfOperation(FlowBlock):
    """Check if within hours of operation."""

    def __post_init__(self):
        self.type = "CheckHoursOfOperation"

    @classmethod
    def from_dict(cls, data: dict) -> 'CheckHoursOfOperation':
        params = data.get("Parameters", {})
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
