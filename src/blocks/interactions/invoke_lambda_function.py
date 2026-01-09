"""
InvokeLambdaFunction - Invoke AWS Lambda function.
https://docs.aws.amazon.com/connect/latest/APIReference/interactions-invokelambdafunction.html
"""
from dataclasses import dataclass
from typing import Optional
import uuid
from ..base import FlowBlock


@dataclass
class InvokeLambdaFunction(FlowBlock):
    """Invoke AWS Lambda function."""
    lambda_function_arn: str = ""
    invocation_time_limit_seconds: str = "8"

    def __post_init__(self):
        self.type = "InvokeLambdaFunction"
        if not self.parameters:
            self.parameters = {}
        if self.lambda_function_arn:
            self.parameters["LambdaFunctionARN"] = self.lambda_function_arn
        if self.invocation_time_limit_seconds:
            self.parameters["InvocationTimeLimitSeconds"] = self.invocation_time_limit_seconds

    def to_dict(self) -> dict:
        data = super().to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'InvokeLambdaFunction':
        params = data.get("Parameters", {})
        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            lambda_function_arn=params.get("LambdaFunctionARN", ""),
            invocation_time_limit_seconds=params.get("InvocationTimeLimitSeconds", "8"),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
