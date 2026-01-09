"""
UpdateContactAttributes - Set or update contact attributes.
https://docs.aws.amazon.com/connect/latest/APIReference/contact-actions-updatecontactattributes.html
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
import uuid
from ..base import FlowBlock


@dataclass
class UpdateContactAttributes(FlowBlock):
    """Set or update contact attributes."""
    attributes: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        self.type = "UpdateContactAttributes"
        if self.attributes and "Attributes" not in self.parameters:
            self.parameters["Attributes"] = self.attributes

    def to_dict(self) -> dict:
        data = super().to_dict()
        if self.attributes:
            data["Parameters"]["Attributes"] = self.attributes
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'UpdateContactAttributes':
        params = data.get("Parameters", {})
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            attributes=params.get("Attributes"),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
