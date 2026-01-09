# Flow Builder - Programmatic Flow Creation

## Status: Initial Implementation Complete

The flow builder enables creating Amazon Connect contact flows programmatically using Python with a clean, fluent API.

## Quick Start

```python
from flow_builder import ContactFlowBuilder

# Create a new flow
flow = ContactFlowBuilder("My Flow")

# Add blocks
welcome = flow.play_prompt("Hello, welcome to our service")
disconnect = flow.disconnect()

# Wire blocks using fluent API
welcome.then(disconnect).on_error("NoMatchingError", disconnect)

# Compile to JSON file
flow.compile_to_file("output/my_flow.json")
```

## ContactFlowBuilder API

### Constructor
- `ContactFlowBuilder(name: str)` - Create a new flow builder

### Block Creation Methods
- `play_prompt(text: str) -> MessageParticipant` - Play a text-to-speech prompt
- `get_input(text: str, timeout: int = 5) -> GetParticipantInput` - Get DTMF input from caller
- `disconnect() -> DisconnectParticipant` - Disconnect the contact

### Compilation Methods
- `compile() -> dict` - Compile flow to AWS Connect JSON structure
- `compile_to_json(indent: int = 2) -> str` - Compile to JSON string
- `compile_to_file(filepath: str)` - Compile and save to file

## Fluent Wiring API

All blocks support a fluent API for wiring:

### Basic Transitions
```python
block1.then(block2)  # Sets NextAction to block2
```

### Error Handling
```python
block1.on_error("NoMatchingError", error_handler)  # Adds error transition
```

### Chaining
```python
# Methods return self, so you can chain
block1.then(block2).on_error("NoMatchingError", fallback)
```

## Conditional Branching (GetParticipantInput)

The `get_input()` block has special methods for menu conditions:

```python
menu = flow.get_input("Press 1 or 2", timeout=8)

menu.when("1", option1) \
    .when("2", option2) \
    .otherwise(default_block) \
    .on_error("InputTimeLimitExceeded", timeout_handler) \
    .on_error("NoMatchingCondition", default_block)
```

### GetParticipantInput Methods
- `when(value, next_block, operator="Equals")` - Add condition for input value
- `otherwise(next_block)` - Set default action when no conditions match
- `then(next_block)` - Same as `otherwise()` (inherited from base)
- `on_error(error_type, next_block)` - Add error handler (inherited from base)

### Common Error Types
- `NoMatchingError` - General errors
- `InputTimeLimitExceeded` - User didn't provide input in time
- `NoMatchingCondition` - User input didn't match any condition

## Examples

### Simple Flow
```python
flow = ContactFlowBuilder("Simple Flow")

prompt = flow.play_prompt("Created from code")
disconnect = flow.disconnect()

prompt.then(disconnect).on_error("NoMatchingError", disconnect)

flow.compile_to_file("output/simple.json")
```

### Menu Flow with Clean Canvas Wiring
```python
flow = ContactFlowBuilder("Menu Flow")

welcome = flow.play_prompt("Thank you for calling")
menu = flow.get_input("Please press 1 or 2", timeout=8)
option1 = flow.play_prompt("Oranges")
option2 = flow.play_prompt("Apples")

# Create separate disconnect blocks for each branch
# This keeps the canvas wiring clean and easy to read
disconnect_welcome_error = flow.disconnect()
disconnect_option1 = flow.disconnect()
disconnect_option2 = flow.disconnect()
disconnect_menu_default = flow.disconnect()
disconnect_menu_timeout = flow.disconnect()
disconnect_menu_error = flow.disconnect()

welcome.then(menu).on_error("NoMatchingError", disconnect_welcome_error)

menu.when("1", option1) \
    .when("2", option2) \
    .otherwise(disconnect_menu_default) \
    .on_error("InputTimeLimitExceeded", disconnect_menu_timeout) \
    .on_error("NoMatchingCondition", disconnect_menu_default) \
    .on_error("NoMatchingError", disconnect_menu_error)

option1.then(disconnect_option1).on_error("NoMatchingError", disconnect_option1)
option2.then(disconnect_option2).on_error("NoMatchingError", disconnect_option2)

flow.compile_to_file("output/menu.json")
```

**Best Practice:** Create separate disconnect blocks for each branch instead of reusing a single disconnect. This prevents messy crisscrossing wires in the AWS Connect visual canvas.

See [examples/](examples/) folder for complete working examples.

## Features

- Auto-generates UUIDs for each block
- Auto-sets StartAction to first block
- Auto-generates block positions for UI visualization
- Fluent API for wiring blocks
- Type-specific helper methods (e.g., `when()` for menus)

## Validation

Generated flows can be validated against AWS Connect API:

```bash
./validate_flow.sh output/my_flow.json "Test Flow Name"
```

All examples validate successfully with AWS Connect.

## Next Steps

Planned enhancements:
- More block types (queues, lambdas, transfers, etc.)
- Flow validation before compilation
- YAML DSL support
- Auto error handling patterns
