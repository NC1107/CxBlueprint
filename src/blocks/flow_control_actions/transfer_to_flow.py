"""
TransferToFlow - Transfer to another contact flow.
https://docs.aws.amazon.com/connect/latest/APIReference/flow-control-actions-transfertoflow.html
"""
from dataclasses import dataclass
import uuid
from ..base import FlowBlock


@dataclass
class TransferToFlow(FlowBlock):
    """Transfer to another contact flow."""
    contact_flow_id: str = ""

    def __post_init__(self):
        self.type = "TransferToFlow"
        if self.contact_flow_id and "ContactFlowId" not in self.parameters:
            self.parameters["ContactFlowId"] = self.contact_flow_id

    def to_dict(self) -> dict:
        data = super().to_dict()
        if self.contact_flow_id:
            data["Parameters"]["ContactFlowId"] = self.contact_flow_id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'TransferToFlow':
        params = data.get("Parameters", {})
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            contact_flow_id=params.get("ContactFlowId", ""),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
