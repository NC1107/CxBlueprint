"""
Hello Flow - Simple flow that says hello and transfers to goodbye flow
"""
import sys
sys.path.insert(0, '../src')
from flow_builder import ContactFlowBuilder


def create_hello_flow():
    """Create a simple hello flow that transfers to goodbye flow."""
    
    flow = ContactFlowBuilder("Hello Flow", debug=True)
    
    # Say hello
    hello = flow.play_prompt("Hello! Welcome to our system.")
    
    # Transfer to goodbye flow (using placeholder ID for now)
    # In production, this would be the actual contact flow ID/ARN
    transfer = flow.transfer_to_flow("arn:aws:connect:us-east-1:123456789012:instance/12345678-1234-1234-1234-123456789012/contact-flow/goodbye-flow-id")
    
    # Chain them together
    hello.then(transfer)
    
    return flow


def main():
    flow = create_hello_flow()
    
    from pathlib import Path
    import json
    
    compiled = flow.compile()
    output_path = Path(__file__).parent.parent / "src" / "output" / "hello_flow.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(compiled, f, indent=2)
    
    print(f"Generated {flow.name} with {len(compiled['Actions'])} blocks")


if __name__ == "__main__":
    main()