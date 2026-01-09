"""
UpdateContactRoutingBehavior - Update contact routing behavior.
https://docs.aws.amazon.com/connect/latest/APIReference/contact-actions-updatecontactroutingbehavior.html
"""
from dataclasses import dataclass
import uuid
from ..base import FlowBlock


@dataclass
class UpdateContactRoutingBehavior(FlowBlock):
    """Update contact routing behavior."""

    def __post_init__(self):
        self.type = "UpdateContactRoutingBehavior"

    @classmethod
    def from_dict(cls, data: dict) -> 'UpdateContactRoutingBehavior':
        params = data.get("Parameters", {})
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
