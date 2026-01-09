"""
Contact Flow Builder - Programmatic flow generation
"""
from pathlib import Path
import json
from typing import List, Optional, Dict, Set, Tuple, TypeVar
from collections import deque, defaultdict
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
    """Build contact flows programmatically with layered BFS layout."""

    # The Amazon Connect Canvas X increases to the right and Y increases downwards.
    # Block positions represent the top-left corner of the block.

    # Layout constants based on AWS Connect canvas analysis
    BLOCK_WIDTH = 200           # Estimated block width in pixels
    BLOCK_HEIGHT_BASE = 100     # Base block height (no conditions)
    BLOCK_HEIGHT_PER_BRANCH = 25  # Additional height per condition/error branch
    HORIZONTAL_SPACING = 280    # Pixels between columns (left edge to left edge)
    VERTICAL_SPACING_MIN = 180  # Minimum vertical spacing between rows
    START_X = 150               # X position of first column
    START_Y = 50                # Y position of first row
    
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
            attributes=attributes
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
    
    # Layered BFS Layout Algorithm
    #
    # This algorithm positions blocks in a grid layout:
    # - X axis (columns): determined by BFS level from start block
    # - Y axis (rows): determined by order of discovery, keeping related branches together
    # - Sequential flow (NextAction) goes horizontally (left to right)
    # - Branching (Conditions/Errors) fans out vertically (top to bottom)

    def _get_block(self, block_id: str) -> Optional[FlowBlock]:
        """Get block by ID."""
        return next((b for b in self.blocks if b.identifier == block_id), None)

    def _get_all_targets(self, block: FlowBlock) -> List[Tuple[str, str]]:
        """Get all target block IDs from a block's transitions.

        Returns list of (target_id, transition_type) tuples.
        transition_type is 'next', 'condition', or 'error'.
        """
        targets = []
        transitions = block.transitions

        # NextAction first (primary path)
        if transitions.get("NextAction"):
            targets.append((transitions["NextAction"], "next"))

        # Then conditions (in order)
        for cond in transitions.get("Conditions", []):
            if cond.get("NextAction"):
                targets.append((cond["NextAction"], "condition"))

        # Then errors (in order)
        for err in transitions.get("Errors", []):
            if err.get("NextAction"):
                targets.append((err["NextAction"], "error"))

        return targets

    def _assign_levels(self) -> Dict[str, int]:
        """Assign each block to a horizontal level (column) using BFS.

        Level 0 is the start block, level 1 is blocks reachable in 1 step, etc.
        Each block gets assigned to its shortest path level from start.
        """
        if not self._start_action:
            return {}

        levels = {}
        queue = deque([(self._start_action, 0)])

        while queue:
            block_id, level = queue.popleft()

            # Skip if already assigned (keep shortest path level)
            if block_id in levels:
                continue

            levels[block_id] = level

            block = self._get_block(block_id)
            if not block:
                continue

            # Add all targets to queue at next level
            for target_id, _ in self._get_all_targets(block):
                if target_id not in levels:
                    queue.append((target_id, level + 1))

        return levels

    def _build_parent_map(self) -> Dict[str, List[str]]:
        """Build a map of block_id -> list of parent block_ids."""
        parents = defaultdict(list)

        for block in self.blocks:
            for target_id, _ in self._get_all_targets(block):
                parents[target_id].append(block.identifier)

        return parents

    def _get_parent_row(self, block_id: str, rows: Dict[str, int],
                        parent_map: Dict[str, List[str]]) -> int:
        """Get the minimum row of this block's parents, or 0 if no parents have rows yet."""
        parent_ids = parent_map.get(block_id, [])
        parent_rows = [rows[pid] for pid in parent_ids if pid in rows]
        return min(parent_rows) if parent_rows else 0

    def _build_next_action_map(self) -> Dict[str, str]:
        """Build a map of block_id -> parent that reaches it via NextAction."""
        next_action_parent = {}

        for block in self.blocks:
            transitions = block.transitions
            if transitions.get("NextAction"):
                next_action_parent[transitions["NextAction"]] = block.identifier

        return next_action_parent

    def _assign_rows(self, levels: Dict[str, int]) -> Dict[str, int]:
        """Assign row (Y) positions to blocks within each level.

        Key insight: Blocks reached via NextAction should stay at the same row
        as their parent (horizontal flow). Only branching (conditions/errors)
        creates new rows (vertical fan-out).
        """
        parent_map = self._build_parent_map()
        next_action_parent = self._build_next_action_map()

        # Group blocks by level
        level_groups = defaultdict(list)
        for block_id, level in levels.items():
            level_groups[level].append(block_id)

        rows = {}
        used_rows_per_level = defaultdict(set)  # Track used rows at each level

        # Process levels in order
        for level in sorted(level_groups.keys()):
            blocks_at_level = level_groups[level]

            # Sort by parent's row to keep related branches together
            blocks_at_level.sort(key=lambda bid: self._get_parent_row(bid, rows, parent_map))

            for block_id in blocks_at_level:
                # Check if this block is reached via NextAction
                next_parent = next_action_parent.get(block_id)

                if next_parent and next_parent in rows:
                    # Try to use same row as NextAction parent (horizontal flow)
                    desired_row = rows[next_parent]
                    if desired_row not in used_rows_per_level[level]:
                        rows[block_id] = desired_row
                        used_rows_per_level[level].add(desired_row)
                        continue

                # For branching targets or if desired row is taken, find next available
                min_row = self._get_parent_row(block_id, rows, parent_map)

                # Find first unused row at this level at or after min_row
                row = min_row
                while row in used_rows_per_level[level]:
                    row += 1

                rows[block_id] = row
                used_rows_per_level[level].add(row)

        return rows

    def _compact_rows(self, rows: Dict[str, int]) -> Dict[str, int]:
        """Compact row assignments to remove gaps.

        Renumbers rows to be contiguous starting from 0.
        """
        if not rows:
            return rows

        # Get sorted unique row values
        unique_rows = sorted(set(rows.values()))

        # Create mapping from old row to new compact row
        row_map = {old: new for new, old in enumerate(unique_rows)}

        # Apply mapping
        return {block_id: row_map[row] for block_id, row in rows.items()}

    def _get_block_height(self, block: Optional[FlowBlock]) -> int:
        """Calculate the visual height of a block based on its branches.

        Blocks with more conditions/errors need more vertical space.
        """
        if not block:
            return self.BLOCK_HEIGHT_BASE

        transitions = block.transitions
        num_conditions = len(transitions.get("Conditions", []))
        num_errors = len(transitions.get("Errors", []))
        num_branches = num_conditions + num_errors

        # Base height + additional height per branch
        height = self.BLOCK_HEIGHT_BASE + (num_branches * self.BLOCK_HEIGHT_PER_BRANCH)
        return height

    def _calculate_positions(self) -> Dict[str, dict]:
        """Calculate block positions using layered BFS algorithm.

        Returns dict mapping block_id to {"x": int, "y": int}.
        """
        if not self._start_action:
            return {}

        # Phase 1: Assign levels (columns)
        levels = self._assign_levels()

        # Phase 2: Assign rows
        rows = self._assign_rows(levels)

        # Phase 3: Compact rows to remove gaps
        rows = self._compact_rows(rows)

        # Phase 4: Calculate Y positions based on cumulative heights
        # Group blocks by row to calculate Y offsets
        row_blocks = defaultdict(list)
        for block_id, row in rows.items():
            row_blocks[row].append(block_id)

        # Calculate the maximum height needed for each row
        row_heights = {}
        for row, block_ids in row_blocks.items():
            max_height = self.VERTICAL_SPACING_MIN
            for block_id in block_ids:
                block = self._get_block(block_id)
                block_height = self._get_block_height(block) + 80  # Add padding
                max_height = max(max_height, block_height)
            row_heights[row] = max_height

        # Calculate cumulative Y positions for each row
        row_y_positions = {}
        current_y = self.START_Y
        for row in sorted(row_heights.keys()):
            row_y_positions[row] = current_y
            current_y += row_heights[row]

        # Phase 5: Convert to pixel positions
        positions = {}
        for block_id in levels:
            level = levels[block_id]
            row = rows[block_id]

            x = self.START_X + level * self.HORIZONTAL_SPACING
            y = row_y_positions[row]

            positions[block_id] = {"x": int(x), "y": int(y)}

        if self.debug:
            self._print_debug_info(positions)

        return positions

    def _print_debug_info(self, positions: Dict[str, dict]):
        """Print debug information about the layout."""
        print("\n" + "="*60)
        print("LAYERED BFS LAYOUT DEBUG INFO")
        print("="*60)

        print(f"\nTotal blocks positioned: {len(positions)}")

        if positions:
            x_coords = [pos["x"] for pos in positions.values()]
            y_coords = [pos["y"] for pos in positions.values()]
            print(f"\nCanvas dimensions:")
            print(f"  X: {min(x_coords)} to {max(x_coords)} ({max(x_coords) - min(x_coords)}px)")
            print(f"  Y: {min(y_coords)} to {max(y_coords)} ({max(y_coords) - min(y_coords)}px)")

            # Count columns and rows
            unique_x = len(set(x_coords))
            unique_y = len(set(y_coords))
            print(f"  Columns: {unique_x}, Rows: {unique_y}")

            # Check for exact position collisions
            pos_set = set()
            collision_count = 0
            for block_id, pos in positions.items():
                pos_tuple = (pos["x"], pos["y"])
                if pos_tuple in pos_set:
                    collision_count += 1
                    print(f"  COLLISION at ({pos['x']}, {pos['y']})")
                pos_set.add(pos_tuple)

            if collision_count == 0:
                print(f"\nNo collisions detected!")
            else:
                print(f"\nWARNING: {collision_count} collisions detected!")

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

        # Calculate positions using layered BFS algorithm
        positions = self._calculate_positions()

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