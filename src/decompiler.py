import json
from typing import Dict, Type
from blocks import (
    FlowBlock,
    # Participant Actions
    DisconnectParticipant,
    MessageParticipant,
    MessageParticipantIteratively,
    GetParticipantInput,
    ConnectParticipantWithLexBot,
    ShowView,
    # Other blocks
    EndFlowExecution,
    UpdateContactRecordingBehavior,
    TransferToFlow,
    UpdateContactAttributes,
    UpdateContactTargetQueue,
    TransferContactToQueue,
    Compare,
    InvokeLambdaFunction,
    Wait,
    DistributeByPercentage,
    CheckHoursOfOperation,
    CheckMetricData,
    CreateCallbackContact,
    UpdateContactCallbackNumber,
    UpdateContactEventHooks,
    UpdateContactRoutingBehavior,
    CreateTask,
)
from contact_flow import ContactFlow


class FlowDecompiler:
    """Decompile AWS Connect JSON into FlowBlock objects."""
    
    # Map AWS block types to Python classes
    BLOCK_TYPE_MAP: Dict[str, Type[FlowBlock]] = {
        # Participant Actions
        "DisconnectParticipant": DisconnectParticipant,
        "MessageParticipant": MessageParticipant,
        "MessageParticipantIteratively": MessageParticipantIteratively,
        "GetParticipantInput": GetParticipantInput,
        "ConnectParticipantWithLexBot": ConnectParticipantWithLexBot,
        "ShowView": ShowView,
        # Other blocks
        "EndFlowExecution": EndFlowExecution,
        "UpdateContactRecordingBehavior": UpdateContactRecordingBehavior,
        "TransferToFlow": TransferToFlow,
        "UpdateContactAttributes": UpdateContactAttributes,
        "UpdateContactTargetQueue": UpdateContactTargetQueue,
        "TransferContactToQueue": TransferContactToQueue,
        "Compare": Compare,
        "InvokeLambdaFunction": InvokeLambdaFunction,
        "Wait": Wait,
        "DistributeByPercentage": DistributeByPercentage,
        "CheckHoursOfOperation": CheckHoursOfOperation,
        "CheckMetricData": CheckMetricData,
        "CreateCallbackContact": CreateCallbackContact,
        "UpdateContactCallbackNumber": UpdateContactCallbackNumber,
        "UpdateContactEventHooks": UpdateContactEventHooks,
        "UpdateContactRoutingBehavior": UpdateContactRoutingBehavior,
        "CreateTask": CreateTask,
    }

    @classmethod
    def decompile(cls, flow_json: dict) -> tuple[ContactFlow, bool]:
        """
        Parse AWS Connect JSON into a ContactFlow object.
        Returns tuple of (ContactFlow, has_unknown_blocks)
        """
        actions = []
        unknown_types = set()
        
        for action_data in flow_json.get("Actions", []):
            block_type = action_data.get("Type")
            
            if block_type not in cls.BLOCK_TYPE_MAP:
                unknown_types.add(block_type)
                print(f"[WARNING] Unknown block type: {block_type}")
                print(f"   Block data: {json.dumps(action_data, indent=2)}\n")
            
            block_class = cls.BLOCK_TYPE_MAP.get(block_type, FlowBlock)
            block = block_class.from_dict(action_data)
            actions.append(block)
        
        if unknown_types:
            print(f"[SUMMARY] Found {len(unknown_types)} unknown block type(s): {', '.join(sorted(unknown_types))}\n")
        
        flow = ContactFlow(
            version=flow_json.get("Version", "2019-10-30"),
            start_action=flow_json.get("StartAction", ""),
            metadata=flow_json.get("Metadata", {}),
            actions=actions
        )
        
        return flow, len(unknown_types) > 0

    @classmethod
    def decompile_from_file(cls, filepath: str) -> tuple[ContactFlow, bool]:
        """
        Load and decompile a contact flow from a JSON file.
        Returns tuple of (ContactFlow, has_unknown_blocks)
        """
        with open(filepath, 'r') as f:
            flow_json = json.load(f)
        return cls.decompile(flow_json)
