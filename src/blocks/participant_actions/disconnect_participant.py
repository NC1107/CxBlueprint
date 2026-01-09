"""
DisconnectParticipant - Disconnect/hang up the participant.
https://docs.aws.amazon.com/connect/latest/APIReference/participant-actions-disconnectparticipant.html
"""
from dataclasses import dataclass
import uuid
from ..base import FlowBlock


@dataclass
class DisconnectParticipant(FlowBlock):
    """
    Disconnect the participant from the contact and stop the flow.

    Parameters:
        None - No parameters expected.

    Results:
        None - Conditions are not supported.

    Errors:
        None.

    Restrictions:
        - Supported on all channels
        - Supported in: Contact flows, Transfer flows, Customer queue flows
    """

    def __post_init__(self):
        self.type = "DisconnectParticipant"

    @classmethod
    def from_dict(cls, data: dict) -> 'DisconnectParticipant':
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            parameters=data.get("Parameters", {}),
            transitions=data.get("Transitions", {})
        )
