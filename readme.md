# CxBlueprint

Programmatic Amazon Connect contact flow generation using Python.

## What It Does

Generate Amazon Connect flows from Python code instead of the visual editor.

### Simple Example

```python
from flow_builder import ContactFlowBuilder

flow = ContactFlowBuilder("Burger Order")

welcome = flow.play_prompt("Welcome to Burger Palace!")
menu = flow.get_input("Press 1 for Classic Burger or 2 for Veggie Burger", timeout=10)
welcome.then(menu)

classic = flow.play_prompt("You selected Classic Burger. Your order is confirmed!")
veggie = flow.play_prompt("You selected Veggie Burger. Your order is confirmed!")
error_msg = flow.play_prompt("Invalid selection. Goodbye.")

disconnect = flow.disconnect()

# Chain menu options with error handling
menu.when("1", classic) \
    .when("2", veggie) \
    .otherwise(error_msg) \
    .on_error("InputTimeLimitExceeded", error_msg) \
    .on_error("NoMatchingCondition", error_msg) \
    .on_error("NoMatchingError", error_msg)

# Or without chaining:
# menu.when("1", classic)
# menu.when("2", veggie)
# menu.otherwise(error_msg)
# menu.on_error("InputTimeLimitExceeded", error_msg)
# menu.on_error("NoMatchingCondition", error_msg)
# menu.on_error("NoMatchingError", error_msg)

classic.then(disconnect)
veggie.then(disconnect)
error_msg.then(disconnect)

flow.compile_to_file("burger_order.json")
```

### Terraform Template Example

Use placeholders for dynamic resource ARNs:

```python
from flow_builder import ContactFlowBuilder

flow = ContactFlowBuilder("Counter Flow")

welcome = flow.play_prompt("Thank you for calling!")
invoke_counter = flow.invoke_lambda(
    function_arn="${COUNTER_LAMBDA_ARN}",  # Resolved by Terraform
    timeout_seconds="8"
)
welcome.then(invoke_counter)

say_count = flow.play_prompt("You are caller number $.External.count")
invoke_counter.then(say_count)

disconnect = flow.disconnect()
say_count.then(disconnect)
invoke_counter.on_error("NoMatchingError", disconnect)

flow.compile_to_file("counter_flow.json")
```

## Generated Flow Examples

Here's what the generated flows look like in the Amazon Connect console:

![Example Generated Flow](docs/example_generated_flow.png)

![Example Generated Flow 2](docs/example_generate_flow2.png)

## Features

- Fluent Python API for building flows
- Naive block positioning for AWS Connect visual canvas
- Automatic UUID generation for blocks
- Error/Conditional handling support
- Integration with AWS Lambda and lexv2 bots
- Template placeholder support for Terraform/IaC
- Decompile existing flows to Python
- Majority of Amazon Connect block types supported
- Shell scripts to download, validate, and test flows against Connect

## Quick Start

```bash
# See Terraform example
cd terraform_example
python flow_generator.py

# Deploy with Terraform
cd terraform
terraform init
terraform apply
```

## Project Structure

```
src/
  flow_builder.py       # Main builder API
  decompiler.py         # JSON to Python
  blocks/               # All Connect block types
    contact_actions/    # Actions like CreateTask
      readme.md         # Contains progress on supported blocks
     flow_control_actions/ # Flow control blocks
      readme.md         # Contains progress on supported blocks
     interactions/      # Interaction blocks
      readme.md         # Contains progress on supported blocks
     participant_actions/  # Participant blocks
      readme.md         # Contains progress on supported blocks
examples/               # Sample flows
terraform_example/      # Complete deployment example
docs/                   # API reference
```

## Documentation

- [API Reference](docs/API_REFERENCE.md)
- [Terraform Example](terraform_example/README.md)

## Requirements

- Python 3.11+
- AWS credentials (for deployment)
- Terraform (optional, for infrastructure)
