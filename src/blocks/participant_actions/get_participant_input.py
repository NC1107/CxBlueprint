"""
GetParticipantInput - Gather customer input (DTMF or text).
https://docs.aws.amazon.com/connect/latest/APIReference/participant-actions-getparticipantinput.html
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, TYPE_CHECKING
import uuid
from ..base import FlowBlock
from ..types import Media, InputValidation, InputEncryption, DTMFConfiguration

if TYPE_CHECKING:
    from typing import Self
else:
    Self = object


@dataclass
class GetParticipantInput(FlowBlock):
    """
    Gather customer input with optional validation, encryption, and storage.

    For voice contacts, gathers DTMF input.
    For other channels, gathers text strings.

    Parameters are mutually exclusive for prompts: use only one of text, prompt_id, ssml, or media.
    InputValidation: PhoneNumberValidation XOR CustomValidation
    InputEncryption requires CustomValidation to be present.

    Results:
        - When StoreInput=False: Participant input returned for condition matching
        - When StoreInput=True: No run result

    Errors:
        - NoMatchingCondition: Required if StoreInput is False
        - NoMatchingError: Always required
        - InvalidPhoneNumber: If StoreInput=True and PhoneNumberValidation specified
        - InputTimeLimitExceeded: No response before InputTimeLimitSeconds

    Restrictions:
        - Voice channel only
        - Not supported in whisper flows or hold flows
    """
    # Prompt parameters (mutually exclusive)
    text: Optional[str] = None
    prompt_id: Optional[str] = None
    ssml: Optional[str] = None
    media: Optional[Media] = None

    # Required parameters
    input_time_limit_seconds: str = "5"
    store_input: str = "False"

    # Optional validation/encryption
    input_validation: Optional[InputValidation] = None
    input_encryption: Optional[InputEncryption] = None
    dtmf_configuration: Optional[DTMFConfiguration] = None

    def __post_init__(self):
        self.type = "GetParticipantInput"
        self._build_parameters()

    def _build_parameters(self):
        """Build parameters dict from typed attributes."""
        params = {}

        # Prompt parameters
        if self.text is not None:
            params["Text"] = self.text
        if self.prompt_id is not None:
            params["PromptId"] = self.prompt_id
        if self.ssml is not None:
            params["SSML"] = self.ssml
        if self.media is not None:
            params["Media"] = self.media.to_dict()

        # Required parameters
        params["InputTimeLimitSeconds"] = self.input_time_limit_seconds
        params["StoreInput"] = self.store_input

        # Optional parameters
        if self.input_validation is not None:
            params["InputValidation"] = self.input_validation.to_dict()
        if self.input_encryption is not None:
            params["InputEncryption"] = self.input_encryption.to_dict()
        if self.dtmf_configuration is not None:
            params["DTMFConfiguration"] = self.dtmf_configuration.to_dict()

        self.parameters = params

    def when(self, value: str, next_block: FlowBlock, operator: str = "Equals") -> 'Self':
        """Add a condition: when input matches value, go to next_block."""
        if "Conditions" not in self.transitions:
            self.transitions["Conditions"] = []

        self.transitions["Conditions"].append({
            "NextAction": next_block.identifier,
            "Condition": {
                "Operator": operator,
                "Operands": [value]
            }
        })
        return self

    def otherwise(self, next_block: FlowBlock) -> 'Self':
        """Set the default action when no conditions match."""
        self.transitions["NextAction"] = next_block.identifier
        return self

    def to_dict(self) -> dict:
        self._build_parameters()
        return super().to_dict()

    @classmethod
    def from_dict(cls, data: dict) -> 'GetParticipantInput':
        params = data.get("Parameters", {})

        # Parse nested objects
        media_data = params.get("Media")
        input_validation_data = params.get("InputValidation")
        input_encryption_data = params.get("InputEncryption")
        dtmf_config_data = params.get("DTMFConfiguration")

        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            text=params.get("Text"),
            prompt_id=params.get("PromptId"),
            ssml=params.get("SSML"),
            media=Media.from_dict(media_data) if media_data else None,
            input_time_limit_seconds=params.get("InputTimeLimitSeconds", "5"),
            store_input=params.get("StoreInput", "False"),
            input_validation=InputValidation.from_dict(input_validation_data) if input_validation_data else None,
            input_encryption=InputEncryption.from_dict(input_encryption_data) if input_encryption_data else None,
            dtmf_configuration=DTMFConfiguration.from_dict(dtmf_config_data) if dtmf_config_data else None,
            parameters=params,
            transitions=data.get("Transitions", {})
        )
