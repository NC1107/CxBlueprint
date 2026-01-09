"""
Contact Flow Builder - Programmatic flow generation
"""
from pathlib import Path
import json
from typing import List, Optional, Dict, Set, Tuple, TypeVar
from collections import deque
import uuid
from blocks.base import FlowBlock
from blocks.participant_actions import (
    MessageParticipant,
    DisconnectParticipant,
    GetParticipantInput,
    ConnectParticipantWithLexBot,
    ShowView,
)
from blocks.flow_control_actions import (
    TransferToFlow,
    CheckHoursOfOperation,
    EndFlowExecution,
)
from blocks.interactions import InvokeLambdaFunction
from blocks.contact_actions import UpdateContactAttributes
from blocks.types import LexV2Bot, LexBot, ViewResource, Media

T = TypeVar('T', bound=FlowBlock) # Generic FlowBlock type for method returns


class ContactFlowBuilder:
    """Build contact flows programmatically with BFS-based layout."""

    # The Amazon Connect Canvas X increases to the right and Y increases downwards.
    
    # Layout constants - Grid-based model (all positions are center-based)
    GRID_UNIT = 19.2
    
    BLOCK_WIDTH_STANDARD = 8 * GRID_UNIT              # 153.6
    BLOCK_HEIGHT_STANDARD = 4 * GRID_UNIT             # 76.8
    
    HORIZONTAL_CENTER_SPACING = 12.0833 * GRID_UNIT  # 232.0 (center to center)
    
    # Vertical spacing for conditionals
    VERTICAL_SPACING_COND_EMPTY = 8.4167 * GRID_UNIT      # 161.6
    VERTICAL_SPACING_COND_1_OPT = 10.1667 * GRID_UNIT     # 195.2
    VERTICAL_SPACING_PER_OPTION = 2 * GRID_UNIT           # ~38.4 per extra condition
    
    # General vertical spacing (non-conditional)
    VERTICAL_SPACING = VERTICAL_SPACING_COND_1_OPT
    
    COLLISION_PADDING = HORIZONTAL_CENTER_SPACING  # Minimum safe distance
    
    START_X = 150
    START_Y = 40
    
    def __init__(self, name: str, debug: bool = False):
        self.name = name
        self.version = "2019-10-30"
        self.blocks: List[FlowBlock] = []
        self._start_action: Optional[str] = None
        self.debug = debug
    
    def _register_block(self, block: T) -> T:
        """Register a block with the flow."""
        self.blocks.append(block)
        
        # Set start action to first block if not set
        if self._start_action is None:
            self._start_action = block.identifier
        
        return block
    
    def play_prompt(self, text: str) -> MessageParticipant:
        """Create a play prompt block."""
        block = MessageParticipant(
            identifier=str(uuid.uuid4()),
            text=text
        )
        return self._register_block(block)
    
    def get_input(self, text: str, timeout: int = 5) -> GetParticipantInput:
        """Create a get participant input block."""
        block = GetParticipantInput(
            identifier=str(uuid.uuid4()),
            text=text,
            input_time_limit_seconds=str(timeout),
            store_input="False"
        )
        return self._register_block(block)
    
    def disconnect(self) -> DisconnectParticipant:
        """Create a disconnect block."""
        block = DisconnectParticipant(
            identifier=str(uuid.uuid4())
        )
        return self._register_block(block)
    
    def transfer_to_flow(self, contact_flow_id: str) -> TransferToFlow:
        """Create a transfer to flow block."""
        block = TransferToFlow(
            identifier=str(uuid.uuid4()),
            contact_flow_id=contact_flow_id
        )
        return self._register_block(block)
    
    # Generic block registration
    
    def add(self, block: T) -> T:
        """Add a pre-configured block to the flow.
        
        Use this for specialized blocks that aren't covered by convenience methods.
        The block must already have an identifier set.
        
        Example:
            from blocks.participant_actions import ConnectParticipantWithLexBot
            from blocks.types import LexV2Bot
            
            lex = ConnectParticipantWithLexBot(
                identifier=str(uuid.uuid4()),
                text="How can I help you?",
                lex_v2_bot=LexV2Bot(alias_arn="arn:aws:lex:...")
            )
            flow.add(lex)
        """
        return self._register_block(block)
    
    # Convenience methods for common complex blocks
    
    def lex_bot(self, text: str = None, lex_v2_bot: LexV2Bot = None, 
                lex_bot: LexBot = None, **kwargs) -> ConnectParticipantWithLexBot:
        """Create a Lex bot interaction block.
        
        Args:
            text: Prompt text to play before bot interaction
            lex_v2_bot: Lex V2 bot configuration (recommended)
            lex_bot: Legacy Lex bot configuration
            **kwargs: Additional parameters (lex_session_attributes, etc.)
        """
        block = ConnectParticipantWithLexBot(
            identifier=str(uuid.uuid4()),
            text=text,
            lex_v2_bot=lex_v2_bot,
            lex_bot=lex_bot,
            **kwargs
        )
        return self._register_block(block)
    
    def invoke_lambda(self, function_arn: str, timeout_seconds: str = "8", **kwargs) -> InvokeLambdaFunction:
        """Create a Lambda function invocation block.
        
        Args:
            function_arn: ARN of the Lambda function (or template like {{LAMBDA_ARN}})
            timeout_seconds: Function timeout (default: 8)
            **kwargs: Additional parameters
        """
        block = InvokeLambdaFunction(
            identifier=str(uuid.uuid4()),
            lambda_function_arn=function_arn,
            invocation_time_limit_seconds=timeout_seconds,
            **kwargs
        )
        return self._register_block(block)
    
    def check_hours(self, hours_of_operation_id: str = None, **kwargs) -> CheckHoursOfOperation:
        """Create a business hours check block.
        
        Args:
            hours_of_operation_id: Hours of operation ID (or template)
            **kwargs: Additional parameters
        """
        params = {}
        if hours_of_operation_id:
            params["HoursOfOperationId"] = hours_of_operation_id
        params.update(kwargs)
        
        block = CheckHoursOfOperation(
            identifier=str(uuid.uuid4()),
            parameters=params
        )
        return self._register_block(block)
    
    def update_attributes(self, **attributes) -> UpdateContactAttributes:
        """Create a contact attributes update block.
        
        Args:
            **attributes: Attributes to update (passed as parameters)
        """
        block = UpdateContactAttributes(
            identifier=str(uuid.uuid4()),
            parameters=attributes
        )
        return self._register_block(block)
    
    def show_view(self, view_resource: ViewResource, **kwargs) -> ShowView:
        """Create an agent workspace view block.
        
        Args:
            view_resource: View resource configuration
            **kwargs: Additional parameters (view_data, etc.)
        """
        block = ShowView(
            identifier=str(uuid.uuid4()),
            view_resource=view_resource,
            **kwargs
        )
        return self._register_block(block)
    
    def end_flow(self) -> EndFlowExecution:
        """Create an end flow execution block."""
        block = EndFlowExecution(
            identifier=str(uuid.uuid4())
        )
        return self._register_block(block)
    
    # BFS-based layout algorithm
    
    def _get_block(self, block_id: str) -> Optional[FlowBlock]:
        """Get block by ID."""
        return next((b for b in self.blocks if b.identifier == block_id), None)
    
    def _has_collision(self, positions: Dict[str, dict], x: int, y: int, exclude_id: str = None) -> bool:
        """Check if position collides with existing blocks."""
        for block_id, pos in positions.items():
            if exclude_id and block_id == exclude_id:
                continue
            
            x_dist = abs(x - pos["x"])
            y_dist = abs(y - pos["y"])
            
            # Check if within collision zone
            if x_dist < self.COLLISION_PADDING and y_dist < self.COLLISION_PADDING:
                return True
        
        return False
    
    def _find_safe_position(self, positions: Dict[str, dict], start_x: int, start_y: int) -> Tuple[int, int]:
        """Find safe position starting from given coordinates, moving right."""
        x = start_x
        y = start_y
        
        # Keep moving right until we find a safe spot
        max_attempts = 50
        for _ in range(max_attempts):
            if not self._has_collision(positions, x, y):
                return (x, y)
            x += self.HORIZONTAL_CENTER_SPACING
        
        # If still colliding, try next row
        return (start_x, y + self.VERTICAL_SPACING)
    
    def _calculate_positions_bfs(self) -> Dict[str, dict]:
        """Calculate positions using breadth-first search.
        
        BFS ensures all blocks at same depth are positioned before going deeper.
        This creates a level-by-level layout.
        """
        if not self._start_action:
            return {}
        
        positions = {}
        visited = set()
        queued = set()  # Track what's already in queue
        
        # BFS queue: (block_id, suggested_x, level)
        queue = deque([(self._start_action, self.START_X, 0)])
        queued.add(self._start_action)
        
        while queue:
            # Process entire level at once
            level_size = len(queue)
            current_level = queue[0][2] if queue else 0
            level_y = self.START_Y + (current_level * self.VERTICAL_SPACING)
            
            for _ in range(level_size):
                block_id, suggested_x, level = queue.popleft()
                
                if block_id in visited:
                    continue
                
                visited.add(block_id)
                
                # Find safe position for this block
                x, y = self._find_safe_position(positions, suggested_x, level_y)
                
                # Round to grid unit (19.2)
                x = round(x / self.GRID_UNIT) * self.GRID_UNIT
                y = round(y / self.GRID_UNIT) * self.GRID_UNIT
                
                positions[block_id] = {"x": x, "y": y}
                
                # Get children for next level
                block = self._get_block(block_id)
                if not block:
                    continue
                
                transitions = block.transitions
                
                # Collect all unique children
                children = []
                if "NextAction" in transitions and transitions["NextAction"]:
                    child = transitions["NextAction"]
                    if child not in visited and child not in queued and child not in children:
                        children.append(child)
                
                if "Conditions" in transitions and transitions["Conditions"]:
                    for condition in transitions["Conditions"]:
                        if "NextAction" in condition:
                            child = condition["NextAction"]
                            if child not in visited and child not in queued and child not in children:
                                children.append(child)
                
                if "Errors" in transitions and transitions["Errors"]:
                    for error in transitions["Errors"]:
                        if "NextAction" in error:
                            child = error["NextAction"]
                            if child not in visited and child not in queued and child not in children:
                                children.append(child)
                
                # Queue children
                # NextAction goes horizontally (same level), others go vertically (next level)
                next_action = transitions.get("NextAction")
                for child_id in children:
                    if child_id == next_action:
                        # NextAction: Place horizontally to the right at same level
                        queue.append((child_id, x + self.HORIZONTAL_CENTER_SPACING, level))
                    else:
                        # Conditions/Errors: Place vertically on next level
                        queue.append((child_id, x, level + 1))
                    queued.add(child_id)
        
        if self.debug:
            self._print_debug_info(positions)
        
        return positions
    
    def _print_debug_info(self, positions: Dict[str, dict]):
        """Print debug information about the layout."""
        print("\n" + "="*60)
        print("BFS LAYOUT DEBUG INFO")
        print("="*60)
        
        print(f"\nTotal blocks positioned: {len(positions)}")
        
        # Position summary
        if positions:
            x_coords = [pos["x"] for pos in positions.values()]
            y_coords = [pos["y"] for pos in positions.values()]
            print(f"\nCanvas dimensions:")
            print(f"  X: {min(x_coords)} to {max(x_coords)} ({max(x_coords) - min(x_coords)}px)")
            print(f"  Y: {min(y_coords)} to {max(y_coords)} ({max(y_coords) - min(y_coords)}px)")
            
            # Check for collisions
            collision_count = 0
            block_ids = list(positions.keys())
            for i, id1 in enumerate(block_ids):
                for id2 in block_ids[i+1:]:
                    pos1 = positions[id1]
                    pos2 = positions[id2]
                    x_dist = abs(pos1["x"] - pos2["x"])
                    y_dist = abs(pos1["y"] - pos2["y"])
                    if x_dist < 200 and y_dist < 200:
                        collision_count += 1
            
            print(f"\nCollision check (<200px): {collision_count} potential overlaps")
        
        print("="*60 + "\n")
    
    # Compilation
    
    def _build_metadata(self) -> dict:
        """Build metadata including block positions."""
        metadata = {
            "entryPointPosition": {"x": 0, "y": 0},
            "snapToGrid": False,
            "ActionMetadata": {},
            "Annotations": []
        }
        
        # Calculate positions using BFS layout
        positions = self._calculate_positions_bfs()
        
        for block_id, position in positions.items():
            metadata["ActionMetadata"][block_id] = {
                "position": position
            }
        
        return metadata
    
    def compile(self) -> dict:
        """Compile flow to AWS Connect JSON format."""
        return {
            "Version": self.version,
            "StartAction": self._start_action or "",
            "Metadata": self._build_metadata(),
            "Actions": [block.to_dict() for block in self.blocks]
        }
    
    def compile_to_json(self, indent: int = 2) -> str:
        """Compile flow to JSON string."""
        return json.dumps(self.compile(), indent=indent)
    
    def compile_to_file(self, filepath: str):
        """Compile flow and save to file."""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(self.compile_to_json())
        
        print(f"Flow compiled to: {filepath}")