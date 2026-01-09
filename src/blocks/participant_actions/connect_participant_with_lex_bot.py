"""
ConnectParticipantWithLexBot - Connect participant to a Lex bot.
https://docs.aws.amazon.com/connect/latest/APIReference/participant-actions-connectparticipantwithlexbot.html
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, TYPE_CHECKING
import uuid
from ..base import FlowBlock
from ..types import Media, LexV2Bot, LexBot

if TYPE_CHECKING:
    from typing import Self
else:
    Self = object


@dataclass
class ConnectParticipantWithLexBot(FlowBlock):
    """
    Connect the participant to an Amazon Lex bot for conversational AI.

    Either LexV2Bot or LexBot must be specified (not both).
    Prompt parameters are mutually exclusive: use only one of text, prompt_id, ssml, or media.

    Results:
        - Success result is the Intent of the bot
        - Only EQUALS operator supported in conditions

    Errors:
        - InputTimeLimitExceeded: No response before LexTimeoutSeconds
        - NoMatchingError: An error occurred with no matching handler
        - NoMatchingCondition: No specified condition evaluated to True

    Restrictions:
        - Supported on all channels
        - Not supported in whisper flows or hold flows
        - LexInitializationData (InitialMessage): Chat channel only
    """
    # Prompt parameters (mutually exclusive)
    text: Optional[str] = None
    prompt_id: Optional[str] = None
    ssml: Optional[str] = None
    media: Optional[Media] = None

    # Bot configuration (one required)
    lex_v2_bot: Optional[LexV2Bot] = None
    lex_bot: Optional[LexBot] = None

    # Optional parameters
    lex_session_attributes: Optional[Dict[str, str]] = None
    lex_initialization_data: Optional[Dict[str, str]] = None  # {"InitialMessage": "..."}
    lex_timeout_seconds: Optional[Dict[str, str]] = None  # {"Text": "..."}

    def __post_init__(self):
        self.type = "ConnectParticipantWithLexBot"
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

        # Bot configuration
        if self.lex_v2_bot is not None:
            params["LexV2Bot"] = self.lex_v2_bot.to_dict()
        if self.lex_bot is not None:
            params["LexBot"] = self.lex_bot.to_dict()

        # Optional parameters
        if self.lex_session_attributes is not None:
            params["LexSessionAttributes"] = self.lex_session_attributes
        if self.lex_initialization_data is not None:
            params["LexInitializationData"] = self.lex_initialization_data
        if self.lex_timeout_seconds is not None:
            params["LexTimeoutSeconds"] = self.lex_timeout_seconds

        self.parameters = params

    def on_intent(self, intent_name: str, next_block: FlowBlock) -> 'Self':
        """Add a condition: when bot returns this intent, go to next_block."""
        if "Conditions" not in self.transitions:
            self.transitions["Conditions"] = []

        self.transitions["Conditions"].append({
            "NextAction": next_block.identifier,
            "Condition": {
                "Operator": "Equals",
                "Operands": [intent_name]
            }
        })
        return self

    def to_dict(self) -> dict:
        self._build_parameters()
        return super().to_dict()

    @classmethod
    def from_dict(cls, data: dict) -> 'ConnectParticipantWithLexBot':
        params = data.get("Parameters", {})

        # Parse nested objects
        media_data = params.get("Media")
        lex_v2_bot_data = params.get("LexV2Bot")
        lex_bot_data = params.get("LexBot")

        return cls(
            identifier=data.get("Identifier", str(uuid.uuid4())),
            text=params.get("Text"),
            prompt_id=params.get("PromptId"),
            ssml=params.get("SSML"),
            media=Media.from_dict(media_data) if media_data else None,
            lex_v2_bot=LexV2Bot.from_dict(lex_v2_bot_data) if lex_v2_bot_data else None,
            lex_bot=LexBot.from_dict(lex_bot_data) if lex_bot_data else None,
            lex_session_attributes=params.get("LexSessionAttributes"),
            lex_initialization_data=params.get("LexInitializationData"),
            lex_timeout_seconds=params.get("LexTimeoutSeconds"),
            parameters=params,
            transitions=data.get("Transitions", {})
        )
