"""
CreateCallbackContact - Create a callback contact.
https://docs.aws.amazon.com/connect/latest/APIReference/interactions-createcallbackcontact.html
"""
from dataclasses import dataclass
import uuid
from ..base import FlowBlock


@dataclass
class CreateCallbackContact(FlowBlock):
    """Create a callback contact."""

    def __post_init__(self):
        self.type = "CreateCallbackContact"

    @classmethod
    def from_dict(cls, data: dict) -> 'CreateCallbackContact':
        params = data.get("Parameters", {})
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
