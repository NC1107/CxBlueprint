"""
Interactions - blocks with side effects that don't require a contact/participant.
https://docs.aws.amazon.com/connect/latest/APIReference/interactions.html
"""
from .create_callback_contact import CreateCallbackContact
from .invoke_lambda_function import InvokeLambdaFunction

__all__ = [
    "CreateCallbackContact",
    "InvokeLambdaFunction",
]
