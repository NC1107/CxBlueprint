"""
Amazon Connect Flow Blocks
https://docs.aws.amazon.com/connect/latest/APIReference/contact-actions.html
"""
# Base class
from .base import FlowBlock

# Shared types
from .types import (
    Media,
    LexV2Bot,
    LexBot,
    ViewResource,
    PhoneNumberValidation,
    CustomValidation,
    InputValidation,
    InputEncryption,
    DTMFConfiguration,
)

# Participant Actions
from .participant_actions import (
    DisconnectParticipant,
    GetParticipantInput,
    MessageParticipant,
    MessageParticipantIteratively,
    ConnectParticipantWithLexBot,
    ShowView,
)

# Flow Control Actions
from .flow_control_actions import (
    CheckHoursOfOperation,
    CheckMetricData,
    Compare,
    DistributeByPercentage,
    EndFlowExecution,
    TransferToFlow,
    Wait,
)

# Contact Actions
from .contact_actions import (
    CreateTask,
    TransferContactToQueue,
    UpdateContactAttributes,
    UpdateContactCallbackNumber,
    UpdateContactEventHooks,
    UpdateContactRecordingBehavior,
    UpdateContactRoutingBehavior,
    UpdateContactTargetQueue,
)

# Interactions
from .interactions import (
    CreateCallbackContact,
    InvokeLambdaFunction,
)

__all__ = [
    # Base
    "FlowBlock",
    # Types
    "Media",
    "LexV2Bot",
    "LexBot",
    "ViewResource",
    "PhoneNumberValidation",
    "CustomValidation",
    "InputValidation",
    "InputEncryption",
    "DTMFConfiguration",
    # Participant Actions
    "DisconnectParticipant",
    "GetParticipantInput",
    "MessageParticipant",
    "MessageParticipantIteratively",
    "ConnectParticipantWithLexBot",
    "ShowView",
    # Flow Control Actions
    "CheckHoursOfOperation",
    "CheckMetricData",
    "Compare",
    "DistributeByPercentage",
    "EndFlowExecution",
    "TransferToFlow",
    "Wait",
    # Contact Actions
    "CreateTask",
    "TransferContactToQueue",
    "UpdateContactAttributes",
    "UpdateContactCallbackNumber",
    "UpdateContactEventHooks",
    "UpdateContactRecordingBehavior",
    "UpdateContactRoutingBehavior",
    "UpdateContactTargetQueue",
    # Interactions
    "CreateCallbackContact",
    "InvokeLambdaFunction",
]
