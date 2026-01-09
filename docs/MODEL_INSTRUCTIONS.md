# CxBlueprint: AI Model Instructions

## CRITICAL RULES (READ FIRST)

### Rule 1: GetParticipantInput Contains Its Own Prompt
**NEVER** create a separate `play_prompt()` before a `get_input()`. The prompt text goes INSIDE the `get_input()` block.

```python
# WRONG - DO NOT DO THIS
prompt = flow.play_prompt("Press 1 for Sales, 2 for Support")
menu = flow.get_input("Please make your selection", timeout=10)
prompt.then(menu)

# CORRECT - DO THIS
menu = flow.get_input("Press 1 for Sales, 2 for Support", timeout=10)
```

The `get_input()` block plays its text parameter as audio to the caller, then waits for DTMF input. There is no need for a preceding prompt block.

### Rule 2: Always Handle All Error Cases
Every `get_input()` block MUST have error handlers:

```python
menu = flow.get_input("Press 1 or 2", timeout=10)
menu.when("1", option1) \
    .when("2", option2) \
    .otherwise(fallback) \
    .on_error("InputTimeLimitExceeded", fallback) \
    .on_error("NoMatchingCondition", fallback) \
    .on_error("NoMatchingError", fallback)
```

### Rule 3: Every Path Must End
All flow paths must terminate at either:
- `flow.disconnect()` - Ends the call
- `flow.end_flow()` - Ends flow without disconnecting
- A queue transfer or flow transfer

### Rule 4: Condition Values Are Strings
DTMF conditions are always strings, not integers:

```python
# WRONG
menu.when(1, sales)

# CORRECT
menu.when("1", sales)
```

---

## Library Overview

CxBlueprint generates Amazon Connect contact flow JSON from Python code.

```python
from flow_builder import ContactFlowBuilder

flow = ContactFlowBuilder("My Flow Name", debug=True)
# ... create and connect blocks ...
flow.compile_to_file("output/my_flow.json")
```

---

## Block Types and When to Use Them

### Customer-Facing Blocks

| Method | Use When | Example |
|--------|----------|---------|
| `flow.play_prompt(text)` | Play a message with NO user response expected | Announcements, confirmations, goodbye messages |
| `flow.get_input(text, timeout)` | Collect DTMF keypress from caller | Menus, PIN entry, confirmations |
| `flow.disconnect()` | End the call | Final block in most paths |

### Integration Blocks

| Method | Use When | Example |
|--------|----------|---------|
| `flow.invoke_lambda(arn)` | Call external logic/APIs | Account lookup, data validation |
| `flow.check_hours(id)` | Route by business hours | Open/closed routing |
| `flow.lex_bot(text, lex_v2_bot)` | Natural language input | Voice assistants |

### Data Blocks

| Method | Use When | Example |
|--------|----------|---------|
| `flow.update_attributes(**attrs)` | Store data for later | Customer type, session data |

### Flow Control Blocks

| Method | Use When | Example |
|--------|----------|---------|
| `flow.transfer_to_flow(id)` | Jump to another flow | Sub-flows, error flows |
| `flow.end_flow()` | End without disconnect | Module completion |

---

## Connection Methods

### `.then(block)` - Sequential Connection
Connects one block to the next in sequence:

```python
welcome = flow.play_prompt("Welcome!")
menu = flow.get_input("Press 1 or 2", timeout=10)
welcome.then(menu)
```

### `.when(value, block)` - Conditional Branch
Routes based on user input or block output:

```python
menu = flow.get_input("Press 1 for Sales, 2 for Support", timeout=10)
menu.when("1", sales_block)
menu.when("2", support_block)
```

### `.otherwise(block)` - Default Branch
Fallback when no conditions match:

```python
menu.otherwise(error_block)
```

### `.on_error(error_type, block)` - Error Handler
Handle specific error conditions:

```python
menu.on_error("InputTimeLimitExceeded", timeout_block)
menu.on_error("NoMatchingCondition", invalid_block)
menu.on_error("NoMatchingError", error_block)
```

### Chaining
All connection methods return the block, enabling chaining:

```python
menu.when("1", sales) \
    .when("2", support) \
    .otherwise(error) \
    .on_error("InputTimeLimitExceeded", error) \
    .on_error("NoMatchingCondition", error) \
    .on_error("NoMatchingError", error)
```

---

## Common Error Types

| Error Type | Trigger |
|------------|---------|
| `InputTimeLimitExceeded` | User didn't press any key within timeout |
| `NoMatchingCondition` | User pressed a key not in any `.when()` condition |
| `NoMatchingError` | Catch-all for unexpected errors |

---

## Complete Flow Example

**Requirement:** "Create an IVR where callers press 1 for account balance, 2 for payments, or 3 for an agent. Handle invalid input and timeout."

```python
from flow_builder import ContactFlowBuilder

flow = ContactFlowBuilder("Account Services IVR", debug=True)

# Create all blocks first
welcome = flow.play_prompt("Thank you for calling Account Services.")

main_menu = flow.get_input(
    "Press 1 for account balance, 2 for payments, or 3 to speak with an agent.",
    timeout=10
)

balance_msg = flow.play_prompt("Your current balance is $150.00.")
payment_msg = flow.play_prompt("Transferring you to our payment system.")
agent_msg = flow.play_prompt("Please hold while we connect you to an agent.")
error_msg = flow.play_prompt("I didn't understand your selection. Goodbye.")

disconnect = flow.disconnect()

# Connect the flow
welcome.then(main_menu)

main_menu.when("1", balance_msg) \
    .when("2", payment_msg) \
    .when("3", agent_msg) \
    .otherwise(error_msg) \
    .on_error("InputTimeLimitExceeded", error_msg) \
    .on_error("NoMatchingCondition", error_msg) \
    .on_error("NoMatchingError", error_msg)

balance_msg.then(disconnect)
payment_msg.then(disconnect)
agent_msg.then(disconnect)
error_msg.then(disconnect)

# Generate the flow JSON
flow.compile_to_file("output/account_services.json")
```

---

## Pattern: Multi-Level Menu

When creating nested menus, each `get_input()` contains its own prompt:

```python
flow = ContactFlowBuilder("Department Menu")

# Main menu - prompt is IN the get_input
main = flow.get_input("Press 1 for Sales, 2 for Support", timeout=10)

# Sub-menus - each has its own prompt IN the get_input
sales_menu = flow.get_input("Sales: Press 1 for New Accounts, 2 for Existing", timeout=10)
support_menu = flow.get_input("Support: Press 1 for Technical, 2 for Billing", timeout=10)

# Result messages
new_acct = flow.play_prompt("Connecting to New Accounts")
existing = flow.play_prompt("Connecting to Existing Accounts")
technical = flow.play_prompt("Connecting to Technical Support")
billing = flow.play_prompt("Connecting to Billing")
error = flow.play_prompt("Invalid selection")

disconnect = flow.disconnect()

# Wire main menu
main.when("1", sales_menu) \
    .when("2", support_menu) \
    .otherwise(error) \
    .on_error("InputTimeLimitExceeded", error) \
    .on_error("NoMatchingCondition", error)

# Wire sales sub-menu
sales_menu.when("1", new_acct) \
    .when("2", existing) \
    .otherwise(error) \
    .on_error("InputTimeLimitExceeded", error) \
    .on_error("NoMatchingCondition", error)

# Wire support sub-menu
support_menu.when("1", technical) \
    .when("2", billing) \
    .otherwise(error) \
    .on_error("InputTimeLimitExceeded", error) \
    .on_error("NoMatchingCondition", error)

# All endpoints to disconnect
new_acct.then(disconnect)
existing.then(disconnect)
technical.then(disconnect)
billing.then(disconnect)
error.then(disconnect)

flow.compile_to_file("output/department_menu.json")
```

---

## Pattern: Retry Logic

To allow retries on invalid input:

```python
flow = ContactFlowBuilder("Menu with Retry")

# First attempt
main_menu = flow.get_input("Press 1 for Sales, 2 for Support", timeout=10)

# Retry message (only played on retry path)
retry_msg = flow.play_prompt("I didn't catch that. Let me repeat the options.")

# Second attempt - same prompt
retry_menu = flow.get_input("Press 1 for Sales, 2 for Support", timeout=10)

# Destinations
sales = flow.play_prompt("Connecting to Sales")
support = flow.play_prompt("Connecting to Support")
final_error = flow.play_prompt("Unable to process your request. Goodbye.")
disconnect = flow.disconnect()

# First menu - on error, go to retry
main_menu.when("1", sales) \
    .when("2", support) \
    .otherwise(retry_msg) \
    .on_error("InputTimeLimitExceeded", retry_msg) \
    .on_error("NoMatchingCondition", retry_msg)

# Retry message leads to second attempt
retry_msg.then(retry_menu)

# Second menu - on error, give up
retry_menu.when("1", sales) \
    .when("2", support) \
    .otherwise(final_error) \
    .on_error("InputTimeLimitExceeded", final_error) \
    .on_error("NoMatchingCondition", final_error)

# Endpoints
sales.then(disconnect)
support.then(disconnect)
final_error.then(disconnect)

flow.compile_to_file("output/menu_with_retry.json")
```

---

## Pattern: Press 9 to Repeat Menu

```python
flow = ContactFlowBuilder("Repeating Menu")

# Menu introduction (only played once at start)
intro = flow.play_prompt("Welcome to our service.")

# The main menu
menu = flow.get_input("Press 1 for option A, 2 for option B, or 9 to hear this again", timeout=10)

option_a = flow.play_prompt("You selected option A")
option_b = flow.play_prompt("You selected option B")
error = flow.play_prompt("Invalid selection. Goodbye.")
disconnect = flow.disconnect()

# Wire it up
intro.then(menu)

menu.when("1", option_a) \
    .when("2", option_b) \
    .when("9", menu) \
    .otherwise(error) \
    .on_error("InputTimeLimitExceeded", error) \
    .on_error("NoMatchingCondition", error)

option_a.then(disconnect)
option_b.then(disconnect)
error.then(disconnect)

flow.compile_to_file("output/repeating_menu.json")
```

---

## Pattern: Business Hours Check

```python
flow = ContactFlowBuilder("Hours Check")

hours = flow.check_hours(hours_of_operation_id="${HOURS_OF_OPERATION_ID}")

# Open path
open_menu = flow.get_input("Press 1 for Sales, 2 for Support", timeout=10)

# Closed path
closed_msg = flow.play_prompt("We're currently closed. Our hours are 9 AM to 5 PM.")

sales = flow.play_prompt("Connecting to Sales")
support = flow.play_prompt("Connecting to Support")
disconnect = flow.disconnect()

# Hours check routing
hours.when("True", open_menu)   # In hours
hours.when("False", closed_msg) # After hours

# Menu routing
open_menu.when("1", sales).when("2", support)

# Endpoints
sales.then(disconnect)
support.then(disconnect)
closed_msg.then(disconnect)

flow.compile_to_file("output/hours_check.json")
```

---

## Pattern: Lambda Integration

```python
flow = ContactFlowBuilder("Account Lookup")

# Check account (Lambda returns customer type as attribute)
lookup = flow.invoke_lambda(function_arn="${ACCOUNT_LAMBDA_ARN}")

# Route based on Lambda response
premium = flow.play_prompt("Welcome Premium member. Connecting you to priority support.")
standard = flow.play_prompt("Connecting you to our support team.")
not_found = flow.play_prompt("We couldn't find your account. Please call back with your account number.")

disconnect = flow.disconnect()

# Lambda conditions (based on returned attributes)
lookup.when("Premium", premium) \
    .when("Standard", standard) \
    .on_error("NoMatchingCondition", not_found) \
    .on_error("NoMatchingError", not_found)

premium.then(disconnect)
standard.then(disconnect)
not_found.then(disconnect)

flow.compile_to_file("output/account_lookup.json")
```

---

## Pattern: Store and Use Attributes

```python
flow = ContactFlowBuilder("Attribute Example")

menu = flow.get_input("Press 1 for Sales, 2 for Support", timeout=10)

# Store selection as attribute
set_sales = flow.update_attributes(department="sales", priority="normal")
set_support = flow.update_attributes(department="support", priority="normal")

sales_msg = flow.play_prompt("Routing to Sales")
support_msg = flow.play_prompt("Routing to Support")
disconnect = flow.disconnect()

menu.when("1", set_sales).when("2", set_support)
set_sales.then(sales_msg)
set_support.then(support_msg)
sales_msg.then(disconnect)
support_msg.then(disconnect)

flow.compile_to_file("output/attributes_example.json")
```

---

## Advanced Blocks (Use with flow.add())

For blocks not covered by convenience methods:

```python
import uuid
from blocks.contact_actions import TransferContactToQueue
from blocks.flow_control_actions import DistributeByPercentage, Wait

# Queue transfer
queue = TransferContactToQueue(
    identifier=str(uuid.uuid4()),
    queue_id="${QUEUE_ARN}"
)
flow.add(queue)

# A/B testing
ab_test = DistributeByPercentage(
    identifier=str(uuid.uuid4()),
    percentages=[50, 50]  # 50/50 split
)
flow.add(ab_test)

# Wait/pause
wait = Wait(
    identifier=str(uuid.uuid4()),
    seconds="5"
)
flow.add(wait)
```

---

## Terraform Variable Syntax

Use `${VARIABLE}` for values injected at deploy time:

```python
lambda_block = flow.invoke_lambda(function_arn="${LAMBDA_ARN}")
hours_block = flow.check_hours(hours_of_operation_id="${HOURS_ID}")
```

---

## Translation Checklist

When converting user requirements to code:

1. **Identify all blocks needed**
   - Prompts (play_prompt for announcements only)
   - Menus (get_input with the menu text INSIDE)
   - Endpoints (disconnect, queue, flow transfer)

2. **Identify flow structure**
   - Entry point (first block)
   - Decision points (get_input, check_hours, lambda)
   - Branches (where does each option go?)
   - Exit points (where do paths end?)

3. **Map connections**
   - Sequential: use `.then()`
   - Conditional: use `.when(value, block)`
   - Default: use `.otherwise(block)`
   - Errors: use `.on_error(type, block)`

4. **Verify completeness**
   - Every get_input has all error handlers
   - Every path ends at disconnect or transfer
   - No orphan blocks

---

## Quick Reference

```python
# Initialize
flow = ContactFlowBuilder("Name", debug=True)

# Basic blocks
msg = flow.play_prompt("text")           # Announcement only
menu = flow.get_input("prompt", timeout) # Menu WITH prompt
dc = flow.disconnect()                   # End call

# Integrations
lam = flow.invoke_lambda(arn)            # Lambda
hrs = flow.check_hours(id)               # Hours check
attrs = flow.update_attributes(k=v)      # Store data

# Connections
block.then(next)                         # Sequential
block.when("value", target)              # Conditional
block.otherwise(fallback)                # Default
block.on_error("Type", handler)          # Error

# Output
flow.compile_to_file("path.json")
```

---

## Common Mistakes

| Mistake | Correction |
|---------|------------|
| Separate play_prompt before get_input | Put prompt text IN get_input |
| Missing error handlers on get_input | Add all three: InputTimeLimitExceeded, NoMatchingCondition, NoMatchingError |
| Integer condition values | Use strings: "1" not 1 |
| No disconnect at end of paths | Every path must end |
| Blocks not connected | Use .then() to connect sequential blocks |

---

## Summary

1. **`get_input()` is self-prompting** - it plays its text then waits for input
2. **`play_prompt()` is for announcements** - messages where no response is expected
3. **Always handle errors** - timeout, no match, and catch-all
4. **Always end paths** - disconnect or transfer
5. **Use strings for DTMF** - "1" not 1
6. **Chain connections** - use method chaining for clean code
