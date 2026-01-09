# AI Model Instructions: CxBlueprint Library

## Purpose
This library generates Amazon Connect contact flows programmatically. Your role is to interpret human requests about call flows and produce working Python code using this library.

---

## Mental Model

**Human Intent → Flow Patterns → Python Code → Amazon Connect JSON**

When a user describes a call flow, identify:
1. **Flow pattern** (IVR menu, queue routing, hours check, etc.)
2. **Required blocks** (play prompt, get input, disconnect, etc.)
3. **Branching logic** (when conditions, error handlers)
4. **Connection pattern** (sequential, conditional, error handling)

---

## Core API

### Initialization

```python
from flow_builder import ContactFlowBuilder

flow = ContactFlowBuilder("Flow Name", debug=True)
```

### Basic Blocks

#### MessageParticipant (Play Prompt)
**Use when:** Playing audio/text to caller
```python
block = flow.play_prompt("Welcome to our service")
```

#### GetParticipantInput (Get DTMF Input)
**Use when:** Collecting button press from caller
```python
menu = flow.get_input("Press 1 for Sales, 2 for Support", timeout=10)
```

#### DisconnectParticipant
**Use when:** Ending the call
```python
disconnect = flow.disconnect()
```

#### InvokeLambdaFunction
**Use when:** Calling external logic, databases, APIs
```python
check_account = flow.invoke_lambda(
    function_arn="arn:aws:lambda:us-east-1:123456789:function:CheckAccount",
    timeout_seconds="8"
)
```

#### CheckHoursOfOperation
**Use when:** Business hours routing
```python
hours_check = flow.check_hours(hours_of_operation_id="12345678-1234-1234-1234-123456789012")
```

#### UpdateContactAttributes
**Use when:** Storing data for later use in flow
```python
set_customer_type = flow.update_attributes(CustomerType="Premium", AccountStatus="Active")
```

#### ConnectParticipantWithLexBot
**Use when:** Natural language understanding needed
```python
bot = flow.lex_bot(
    text="How can I help you?",
    lex_v2_bot=LexV2Bot(alias_arn="arn:aws:lex:...")
)
```

#### ShowView
**Use when:** Showing agent-side UI (agent workspace customization)
```python
from blocks.types import ViewResource
show_form = flow.show_view(view_resource=ViewResource(resource_name="CustomerForm"))
```

### Advanced Blocks

Use `flow.add()` for blocks not covered by convenience methods:

```python
from blocks.contact_actions import TransferContactToQueue
from blocks.flow_control_actions import DistributeByPercentage, Compare, Wait

queue_block = TransferContactToQueue(
    identifier=str(uuid.uuid4()),
    queue_id="arn:aws:connect:us-east-1:123456789:instance/abc/queue/def"
)
flow.add(queue_block)
```

**Available advanced blocks:**
- `TransferContactToQueue` - Queue routing
- `TransferToFlow` - Sub-flow transfers
- `DistributeByPercentage` - A/B testing
- `Compare` - Complex conditional logic
- `Wait` - Pause execution
- `CheckMetricData` - Queue metrics
- `EndFlowExecution` - End without disconnect
- `UpdateContactRecordingBehavior` - Recording control
- `UpdateContactRoutingBehavior` - Routing behavior
- `CreateTask` - Task creation
- `CreateCallbackContact` - Callback scheduling

---

## Connection Patterns

### Sequential (A → B)
```python
welcome = flow.play_prompt("Welcome")
menu = flow.get_input("Press 1 or 2", timeout=10)
welcome.then(menu)
```

### Conditional Branching
```python
menu = flow.get_input("Press 1 for Sales, 2 for Support", timeout=10)
sales = flow.play_prompt("Connecting to Sales")
support = flow.play_prompt("Connecting to Support")

menu.when("1", sales)
menu.when("2", support)
```

### Default/Fallback
```python
menu.otherwise(error_msg)  # When no condition matches
```

### Error Handling
```python
menu.on_error("InputTimeLimitExceeded", timeout_msg)
menu.on_error("NoMatchingCondition", error_msg)
```

### Chaining (Multiple connections at once)
```python
menu.when("1", sales) \
    .when("2", support) \
    .otherwise(error_msg) \
    .on_error("InputTimeLimitExceeded", timeout_msg)
```

---

## Common Flow Patterns

### Pattern 1: Simple IVR Menu

**User Request:** "Create a menu where users press 1 for sales or 2 for support"

```python
flow = ContactFlowBuilder("Simple Menu")

welcome = flow.play_prompt("Welcome")
menu = flow.get_input("Press 1 for Sales or 2 for Support", timeout=10)
sales = flow.play_prompt("Connecting to Sales")
support = flow.play_prompt("Connecting to Support")
error_msg = flow.play_prompt("Invalid selection")
disconnect = flow.disconnect()

welcome.then(menu)
menu.when("1", sales).when("2", support).otherwise(error_msg)
sales.then(disconnect)
support.then(disconnect)
error_msg.then(disconnect)

flow.compile_to_file("simple_menu.json")
```

### Pattern 2: Business Hours Check

**User Request:** "Route to voicemail after hours, otherwise go to menu"

```python
flow = ContactFlowBuilder("Hours Routing")

hours_check = flow.check_hours(hours_of_operation_id="{{HOURS_OF_OPERATION_ID}}")
menu = flow.get_input("Press 1 for Sales", timeout=10)
voicemail = flow.play_prompt("We're closed. Please leave a message")
disconnect = flow.disconnect()

hours_check.when("True", menu)  # In hours
hours_check.when("False", voicemail)  # After hours
menu.when("1", disconnect)
voicemail.then(disconnect)

flow.compile_to_file("hours_routing.json")
```

### Pattern 3: Lambda Integration

**User Request:** "Look up customer account, then route based on account type"

```python
flow = ContactFlowBuilder("Account Lookup")

welcome = flow.play_prompt("Looking up your account")
lookup = flow.invoke_lambda(function_arn="{{ACCOUNT_LOOKUP_LAMBDA}}")
premium = flow.play_prompt("Routing to Premium Support")
standard = flow.play_prompt("Routing to Standard Support")
error_msg = flow.play_prompt("Unable to find account")
disconnect = flow.disconnect()

welcome.then(lookup)
lookup.when("Premium", premium)
lookup.when("Standard", standard)
lookup.on_error("NoMatchingCondition", error_msg)
premium.then(disconnect)
standard.then(disconnect)
error_msg.then(disconnect)

flow.compile_to_file("account_routing.json")
```

### Pattern 4: Multi-Level Menu

**User Request:** "Main menu with sub-menus for each department"

```python
flow = ContactFlowBuilder("Multi-Level Menu")

welcome = flow.play_prompt("Welcome to Acme Corp")
main_menu = flow.get_input("Press 1 for Sales, 2 for Support", timeout=10)

# Sales sub-menu
sales_menu = flow.get_input("Sales: Press 1 for New Customer, 2 for Existing", timeout=10)
new_customer = flow.play_prompt("New Customer Sales")
existing = flow.play_prompt("Existing Customer Sales")

# Support sub-menu
support_menu = flow.get_input("Support: Press 1 for Technical, 2 for Billing", timeout=10)
technical = flow.play_prompt("Technical Support")
billing = flow.play_prompt("Billing Support")

disconnect = flow.disconnect()

welcome.then(main_menu)
main_menu.when("1", sales_menu).when("2", support_menu)
sales_menu.when("1", new_customer).when("2", existing)
support_menu.when("1", technical).when("2", billing)

new_customer.then(disconnect)
existing.then(disconnect)
technical.then(disconnect)
billing.then(disconnect)

flow.compile_to_file("multi_level_menu.json")
```

### Pattern 5: Queue Routing with Metrics

**User Request:** "Check queue depth, if too many waiting offer callback"

```python
from blocks.flow_control_actions import CheckMetricData
from blocks.interactions import CreateCallbackContact

flow = ContactFlowBuilder("Smart Queue Routing")

check_queue = CheckMetricData(
    identifier=str(uuid.uuid4()),
    parameters={"Queue": "{{QUEUE_ARN}}", "Metric": "CONTACTS_IN_QUEUE"}
)
flow.add(check_queue)

offer_callback = flow.play_prompt("Queue is busy. Would you like a callback? Press 1 for Yes")
callback_menu = flow.get_input("Press 1 for callback", timeout=10)

callback = CreateCallbackContact(identifier=str(uuid.uuid4()))
flow.add(callback)

transfer_to_queue = flow.play_prompt("Transferring to agent")
disconnect = flow.disconnect()

check_queue.when("LessThan5", transfer_to_queue)
check_queue.when("GreaterThan5", offer_callback)
offer_callback.then(callback_menu)
callback_menu.when("1", callback)
callback.then(disconnect)
transfer_to_queue.then(disconnect)

flow.compile_to_file("smart_queue.json")
```

---

## Decision Tree: Block Selection

**User says → Use this block:**

- "play a message" / "say" / "tell caller" → `flow.play_prompt()`
- "press a button" / "menu" / "select option" / "DTMF" → `flow.get_input()`
- "hang up" / "end call" / "disconnect" → `flow.disconnect()`
- "call Lambda" / "check database" / "external logic" → `flow.invoke_lambda()`
- "business hours" / "open/closed" / "hours of operation" → `flow.check_hours()`
- "store data" / "set attribute" / "remember value" → `flow.update_attributes()`
- "natural language" / "AI bot" / "understand speech" → `flow.lex_bot()`
- "transfer to queue" / "connect to agent" → `TransferContactToQueue` + `flow.add()`
- "transfer to another flow" / "sub-flow" → `flow.transfer_to_flow()`
- "A/B test" / "split traffic" / "percentage" → `DistributeByPercentage` + `flow.add()`
- "wait" / "pause" / "delay" → `Wait` + `flow.add()`
- "show agent screen" / "custom UI" → `flow.show_view()`

---

## Error Handling Patterns

### GetParticipantInput Errors
- `InputTimeLimitExceeded` - User didn't press anything
- `NoMatchingCondition` - User pressed button not in conditions
- `NoMatchingError` - Catch-all error

### Lambda Errors
- `NoMatchingCondition` - Lambda didn't return expected value
- `NoMatchingError` - Lambda execution failed

### Standard Pattern: Chain all error handlers
```python
menu = flow.get_input("Press 1, 2, or 3", timeout=10)
error_msg = flow.play_prompt("Invalid selection. Goodbye.")

menu.when("1", option1) \
    .when("2", option2) \
    .when("3", option3) \
    .otherwise(error_msg) \
    .on_error("InputTimeLimitExceeded", error_msg) \
    .on_error("NoMatchingCondition", error_msg) \
    .on_error("NoMatchingError", error_msg)
```

---

## Terraform Integration

Use template variables for ARNs that will be injected at deploy time:

```python
lambda_block = flow.invoke_lambda(function_arn="${LAMBDA_ARN}")
queue_block = TransferContactToQueue(queue_id="${QUEUE_ARN}")
hours_block = flow.check_hours(hours_of_operation_id="${HOURS_ID}")
```

In Terraform:
```hcl
resource "aws_connect_contact_flow" "flow" {
  content = replace(
    replace(
      file("flow.json"),
      "$${LAMBDA_ARN}",
      aws_lambda_function.my_function.arn
    ),
    "$${QUEUE_ARN}",
    aws_connect_queue.my_queue.arn
  )
}
```

---

## Block Type Reference

### Participant Actions (Customer-facing)
- `MessageParticipant` - Play prompt/message
- `GetParticipantInput` - Get DTMF input
- `DisconnectParticipant` - End call
- `ConnectParticipantWithLexBot` - Lex bot interaction
- `ShowView` - Agent workspace view
- `MessageParticipantIteratively` - Play multiple prompts

### Flow Control
- `Compare` - Conditional branching
- `CheckHoursOfOperation` - Business hours check
- `CheckMetricData` - Queue metrics
- `Wait` - Pause execution
- `DistributeByPercentage` - A/B testing
- `TransferToFlow` - Sub-flow transfer
- `EndFlowExecution` - End without disconnect

### Contact Actions (Metadata/Routing)
- `UpdateContactAttributes` - Store data
- `UpdateContactTargetQueue` - Change target queue
- `UpdateContactRecordingBehavior` - Recording settings
- `UpdateContactRoutingBehavior` - Routing settings
- `UpdateContactCallbackNumber` - Callback number
- `UpdateContactEventHooks` - Event hooks
- `TransferContactToQueue` - Queue transfer
- `CreateTask` - Create task

### Integrations
- `InvokeLambdaFunction` - Lambda invocation
- `CreateCallbackContact` - Schedule callback

---

## Output and Deployment

### Generate JSON
```python
flow.compile_to_file("output/my_flow.json")
```

### Validation
```bash
./validate_flow.sh output/my_flow.json
```

### Deploy with AWS CLI
```bash
aws connect create-contact-flow \
  --instance-id e1587ab3-b10f-405d-b621-8f8a26669655 \
  --name "My Flow" \
  --type CONTACT_FLOW \
  --content file://output/my_flow.json
```

---

## Common Mistakes to Avoid

1. **Forgetting to connect blocks**
   ```python
   # WRONG: Blocks not connected
   welcome = flow.play_prompt("Welcome")
   menu = flow.get_input("Press 1", timeout=10)
   
   # CORRECT:
   welcome.then(menu)
   ```

2. **Not handling all error cases**
   ```python
   # WRONG: Missing error handlers
   menu.when("1", option1)
   
   # CORRECT:
   menu.when("1", option1).otherwise(error).on_error("InputTimeLimitExceeded", error)
   ```

3. **Forgetting disconnect blocks**
   ```python
   # WRONG: Call never ends
   final_msg = flow.play_prompt("Goodbye")
   
   # CORRECT:
   final_msg = flow.play_prompt("Goodbye")
   disconnect = flow.disconnect()
   final_msg.then(disconnect)
   ```

4. **Using incorrect condition values**
   ```python
   # WRONG: GetParticipantInput expects strings
   menu.when(1, sales)  # Bad: integer
   
   # CORRECT:
   menu.when("1", sales)  # Good: string
   ```

5. **Not importing required types**
   ```python
   # WRONG: Missing import
   lex = flow.lex_bot(lex_v2_bot=LexV2Bot(...))  # NameError
   
   # CORRECT:
   from blocks.types import LexV2Bot
   lex = flow.lex_bot(lex_v2_bot=LexV2Bot(...))
   ```

---

## Translation Guidelines

When a user describes a flow in natural language:

1. **Identify entry point** - Usually a welcome message or immediate action
2. **Map each decision point** - Press button, hours check, data lookup
3. **Identify branches** - What happens for each option
4. **Plan error handling** - What if timeout, invalid input, system error
5. **Determine exit points** - Where does each path end (usually disconnect)
6. **Draw connections** - Use `.then()`, `.when()`, `.otherwise()`, `.on_error()`

### Example Translation

**User:** "When someone calls, check if we're open. If open, play a menu where they press 1 for sales or 2 for support. If closed, tell them to call back later. After any selection, hang up."

**Translation:**
1. Entry: hours check (immediate action)
2. Decision: open/closed (CheckHoursOfOperation)
3. If open: menu (GetParticipantInput)
4. If closed: message (MessageParticipant)
5. Menu branches: 1=sales, 2=support (conditions)
6. Error handling: timeout, invalid input
7. Exit: all paths → disconnect

**Code:**
```python
flow = ContactFlowBuilder("Business Hours Routing")

hours = flow.check_hours(hours_of_operation_id="{{HOURS_ID}}")
menu = flow.get_input("Press 1 for Sales, 2 for Support", timeout=10)
closed = flow.play_prompt("We're closed. Please call back during business hours.")
sales = flow.play_prompt("Connecting to Sales")
support = flow.play_prompt("Connecting to Support")
error = flow.play_prompt("Invalid selection. Goodbye.")
disconnect = flow.disconnect()

hours.when("True", menu).when("False", closed)
menu.when("1", sales).when("2", support).otherwise(error) \
    .on_error("InputTimeLimitExceeded", error) \
    .on_error("NoMatchingCondition", error)

sales.then(disconnect)
support.then(disconnect)
closed.then(disconnect)
error.then(disconnect)

flow.compile_to_file("hours_routing.json")
```

---

## Questions to Ask When User Request is Unclear

- "What happens after the user presses [button]?"
- "Should we handle timeout differently than invalid input?"
- "Where should this flow transfer/disconnect?"
- "Do you need to store any data for later use?"
- "Should this route to a queue or just play a message?"
- "What error handling do you need?"
- "Is this for Terraform deployment? (affects ARN format)"

---

## Summary

**Your job:** Convert human descriptions of call flows into working Python code using this library.

**Key principles:**
- Map intent to blocks (prompt, input, disconnect, lambda, etc.)
- Connect blocks with `.then()`, `.when()`, `.otherwise()`, `.on_error()`
- Always handle errors
- Always end flows with disconnect
- Use templates (`${VAR}`) for Terraform deployments
- Import required types when using advanced features

**Mental model:** User intent → Identify pattern → Select blocks → Connect blocks → Handle errors → Generate JSON
