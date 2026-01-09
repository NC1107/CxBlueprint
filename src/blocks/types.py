"""
Shared types for Amazon Connect flow blocks.
https://docs.aws.amazon.com/connect/latest/APIReference/contact-actions.html
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Media:
    """
    External media source configuration.
    Used by MessageParticipant, GetParticipantInput, etc.

    https://docs.aws.amazon.com/connect/latest/APIReference/participant-actions-messageparticipant.html
    """
    uri: str
    source_type: str = "S3"      # Only S3 is supported
    media_type: str = "Audio"    # Only Audio is supported

    def to_dict(self) -> dict:
        return {
            "Uri": self.uri,
            "SourceType": self.source_type,
            "MediaType": self.media_type
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Media':
        return cls(
            uri=data["Uri"],
            source_type=data.get("SourceType", "S3"),
            media_type=data.get("MediaType", "Audio")
        )


@dataclass
class LexV2Bot:
    """
    LexV2 bot configuration.
    Used by ConnectParticipantWithLexBot.
    """
    alias_arn: str

    def to_dict(self) -> dict:
        return {"AliasArn": self.alias_arn}

    @classmethod
    def from_dict(cls, data: dict) -> 'LexV2Bot':
        return cls(alias_arn=data["AliasArn"])


@dataclass
class LexBot:
    """
    Legacy Lex bot configuration.
    Used by ConnectParticipantWithLexBot.
    """
    name: str
    region: str
    alias: str

    def to_dict(self) -> dict:
        return {
            "Name": self.name,
            "Region": self.region,
            "Alias": self.alias
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'LexBot':
        return cls(
            name=data["Name"],
            region=data["Region"],
            alias=data["Alias"]
        )


@dataclass
class ViewResource:
    """
    View resource configuration for ShowView block.
    """
    id: str
    version: str

    def to_dict(self) -> dict:
        return {
            "Id": self.id,
            "Version": self.version
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ViewResource':
        return cls(
            id=data["Id"],
            version=data["Version"]
        )


@dataclass
class PhoneNumberValidation:
    """Phone number validation for GetParticipantInput."""
    number_format: str  # "Local" or "E164"
    country_code: Optional[str] = None  # Required if format is "Local"

    def to_dict(self) -> dict:
        result = {"NumberFormat": self.number_format}
        if self.country_code:
            result["CountryCode"] = self.country_code
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'PhoneNumberValidation':
        return cls(
            number_format=data["NumberFormat"],
            country_code=data.get("CountryCode")
        )


@dataclass
class CustomValidation:
    """Custom validation for GetParticipantInput."""
    maximum_length: str

    def to_dict(self) -> dict:
        return {"MaximumLength": self.maximum_length}

    @classmethod
    def from_dict(cls, data: dict) -> 'CustomValidation':
        return cls(maximum_length=data["MaximumLength"])


@dataclass
class InputValidation:
    """Input validation configuration for GetParticipantInput."""
    phone_number_validation: Optional[PhoneNumberValidation] = None
    custom_validation: Optional[CustomValidation] = None

    def to_dict(self) -> dict:
        result = {}
        if self.phone_number_validation:
            result["PhoneNumberValidation"] = self.phone_number_validation.to_dict()
        if self.custom_validation:
            result["CustomValidation"] = self.custom_validation.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'InputValidation':
        return cls(
            phone_number_validation=PhoneNumberValidation.from_dict(data["PhoneNumberValidation"]) if "PhoneNumberValidation" in data else None,
            custom_validation=CustomValidation.from_dict(data["CustomValidation"]) if "CustomValidation" in data else None
        )


@dataclass
class InputEncryption:
    """Input encryption configuration for GetParticipantInput."""
    encryption_key_id: Optional[str] = None
    key: Optional[str] = None  # PEM public key

    def to_dict(self) -> dict:
        result = {}
        if self.encryption_key_id:
            result["EncryptionKeyId"] = self.encryption_key_id
        if self.key:
            result["Key"] = self.key
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'InputEncryption':
        return cls(
            encryption_key_id=data.get("EncryptionKeyId"),
            key=data.get("Key")
        )


@dataclass
class DTMFConfiguration:
    """DTMF configuration for GetParticipantInput."""
    input_termination_sequence: Optional[str] = None  # Up to 5 digits
    disable_cancel_key: Optional[str] = None  # "True" or "False"
    interdigit_time_limit_seconds: Optional[str] = None  # 1-20 seconds

    def to_dict(self) -> dict:
        result = {}
        if self.input_termination_sequence:
            result["InputTerminationSequence"] = self.input_termination_sequence
        if self.disable_cancel_key:
            result["DisableCancelKey"] = self.disable_cancel_key
        if self.interdigit_time_limit_seconds:
            result["InterdigitTimeLimitSeconds"] = self.interdigit_time_limit_seconds
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'DTMFConfiguration':
        return cls(
            input_termination_sequence=data.get("InputTerminationSequence"),
            disable_cancel_key=data.get("DisableCancelKey"),
            interdigit_time_limit_seconds=data.get("InterdigitTimeLimitSeconds")
        )
