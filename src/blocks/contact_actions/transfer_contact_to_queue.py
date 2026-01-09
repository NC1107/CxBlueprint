"""
TransferContactToQueue - Transfer contact to a queue.
https://docs.aws.amazon.com/connect/latest/APIReference/contact-actions-transfercontacttoqueue.html
"""
from dataclasses import dataclass
import uuid
from ..base import FlowBlock


@dataclass
class TransferContactToQueue(FlowBlock):
    """Transfer contact to a queue."""

    def __post_init__(self):
        self.type = "TransferContactToQueue"

    @classmethod
    def from_dict(cls, data: dict) -> 'TransferContactToQueue':
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            parameters=data.get("Parameters", {}),
            transitions=data.get("Transitions", {})
        )
