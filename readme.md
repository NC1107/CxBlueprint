# CxBlueprint

Programmatic Amazon Connect contact flow generation using Python.

## What It Does

Generate Amazon Connect flows from Python code instead of the visual editor:

```python
from flow_builder import ContactFlowBuilder

flow = ContactFlowBuilder("Customer Support")

welcome = flow.play_prompt("Welcome! Press 1 for sales, 2 for support.")
menu = flow.get_input("Please make your selection", timeout=5)
welcome.then(menu)

sales = flow.play_prompt("Connecting to sales...")
support = flow.play_prompt("Connecting to support...")

menu.when("1", sales).when("2", support)

flow.compile_to_file("support_flow.json")
```

## Features

- Fluent Python API for building flows
- BFS-based layout algorithm (handles loops and complex flows)
- Template placeholder support for Terraform/IaC
- Decompile existing flows to Python
- All Amazon Connect block types supported
- Shell scripts to download, validate, and test flows against Connect

## Quick Start

```bash
# See full example
cd full_example
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
examples/               # Sample flows
full_example/           # Complete deployment example
docs/                   # API reference
```

## Documentation

- [API Reference](docs/API_REFERENCE.md)
- [Full Example](full_example/README.md)

## Requirements

- Python 3.11+
- AWS credentials (for deployment)
- Terraform (optional, for infrastructure)
