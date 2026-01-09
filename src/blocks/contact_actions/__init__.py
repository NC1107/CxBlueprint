"""
Contact Actions - blocks that manipulate contact data.
https://docs.aws.amazon.com/connect/latest/APIReference/contact-actions.html
"""
from .create_task import CreateTask
from .transfer_contact_to_queue import TransferContactToQueue
from .update_contact_attributes import UpdateContactAttributes
from .update_contact_callback_number import UpdateContactCallbackNumber
from .update_contact_event_hooks import UpdateContactEventHooks
from .update_contact_recording_behavior import UpdateContactRecordingBehavior
from .update_contact_routing_behavior import UpdateContactRoutingBehavior
from .update_contact_target_queue import UpdateContactTargetQueue

__all__ = [
    "CreateTask",
    "TransferContactToQueue",
    "UpdateContactAttributes",
    "UpdateContactCallbackNumber",
    "UpdateContactEventHooks",
    "UpdateContactRecordingBehavior",
    "UpdateContactRoutingBehavior",
    "UpdateContactTargetQueue",
]
