"""
DistributeByPercentage - Distribute contacts by percentage for A/B testing.
https://docs.aws.amazon.com/connect/latest/APIReference/flow-control-actions-distributebypercentage.html
"""
from dataclasses import dataclass
import uuid
from ..base import FlowBlock


@dataclass
class DistributeByPercentage(FlowBlock):
    """Distribute contacts by percentage for A/B testing."""

    def __post_init__(self):
        self.type = "DistributeByPercentage"

    @classmethod
    def from_dict(cls, data: dict) -> 'DistributeByPercentage':
        params = data.get("Parameters", {})
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
