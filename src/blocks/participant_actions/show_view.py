"""
ShowView - Display a view in the agent workspace.
https://docs.aws.amazon.com/connect/latest/APIReference/participant-actions-showview.html
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, TYPE_CHECKING
import uuid
from ..base import FlowBlock
from ..types import ViewResource

if TYPE_CHECKING:
    from typing import Self
else:
    Self = object


@dataclass
class ShowView(FlowBlock):
    """
    Show a view resource in the agent workspace UI.

    Results:
        - Returns the result that the user selects when interacting with the View
        - Available conditions depend on the View resource specified

    Errors:
        - NoMatchingError: If no other error matches
        - NoMatchingCondition: If no other condition matches
        - TimeLimitExceeded: No response before InvocationTimeLimitSeconds

    Restrictions:
        - Chat channel only
        - Supported in: Inbound flows, Customer queue flows
        - Combined inputs and contact attributes must be <= 16KB
    """
    view_resource: Optional[ViewResource] = None
    invocation_time_limit_seconds: Optional[str] = None  # Default: 400
    view_data: Optional[Dict[str, Any]] = None
    sensitive_data_configuration: Optional[Dict[str, List[str]]] = None  # {"HideResponseOn": ["TRANSCRIPT"]}

    def __post_init__(self):
        self.type = "ShowView"
        self._build_parameters()

    def _build_parameters(self):
        """Build parameters dict from typed attributes."""
        params = {}

        if self.view_resource is not None:
            params["ViewResource"] = self.view_resource.to_dict()
        if self.invocation_time_limit_seconds is not None:
            params["InvocationTimeLimitSeconds"] = self.invocation_time_limit_seconds
        if self.view_data is not None:
            params["ViewData"] = self.view_data
        if self.sensitive_data_configuration is not None:
            params["SensitiveDataConfiguration"] = self.sensitive_data_configuration

        self.parameters = params

    def on_action(self, action_name: str, next_block: FlowBlock) -> 'Self':
        """Add a condition: when user selects this action, go to next_block."""
        if "Conditions" not in self.transitions:
            self.transitions["Conditions"] = []

        self.transitions["Conditions"].append({
            "NextAction": next_block.identifier,
            "Condition": {
                "Operator": "Equals",
                "Operands": [action_name]
            }
        })
        return self

    def to_dict(self) -> dict:
        self._build_parameters()
        return super().to_dict()

    @classmethod
    def from_dict(cls, data: dict) -> 'ShowView':
        params = data.get("Parameters", {})

        # Parse nested objects
        view_resource_data = params.get("ViewResource")

        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            view_resource=ViewResource.from_dict(view_resource_data) if view_resource_data else None,
            invocation_time_limit_seconds=params.get("InvocationTimeLimitSeconds"),
            view_data=params.get("ViewData"),
            sensitive_data_configuration=params.get("SensitiveDataConfiguration"),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
