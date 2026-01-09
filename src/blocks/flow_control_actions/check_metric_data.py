"""
CheckMetricData - Check queue metrics data.
https://docs.aws.amazon.com/connect/latest/APIReference/flow-control-actions-checkmetricdata.html
"""
from dataclasses import dataclass
import uuid
from ..base import FlowBlock


@dataclass
class CheckMetricData(FlowBlock):
    """Check queue metrics data."""

    def __post_init__(self):
        self.type = "CheckMetricData"

    @classmethod
    def from_dict(cls, data: dict) -> 'CheckMetricData':
        params = data.get("Parameters", {})
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
