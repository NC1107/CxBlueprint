"""
Generate the counter flow - Simple example using ContactFlowBuilder as a library
"""
import sys
sys.path.insert(0, '../src')

from flow_builder import ContactFlowBuilder
import json
from pathlib import Path


def generate_counter_flow():
    """Generate a flow that invokes a counter Lambda and speaks the result."""
    
    # Create the flow builder
    flow = ContactFlowBuilder("Counter Flow")
    
    # Step 1: Welcome message (entry point)
    welcome = flow.play_prompt("Thank you for calling!")
    
    # Step 2: Invoke Lambda (template placeholder - resolved by Terraform)
    invoke_counter = flow.invoke_lambda(
        function_arn="${COUNTER_LAMBDA_ARN}",
        timeout_seconds="8"
    )
    welcome.then(invoke_counter)
    
    # Step 3: Say the count back (using Lambda's return value)
    say_count = flow.play_prompt("You are caller number $.External.count")
    invoke_counter.then(say_count)
    
    # Step 4: Disconnect (end of flow)
    disconnect = flow.disconnect()
    say_count.then(disconnect)
    invoke_counter.on_error("NoMatchingError", disconnect)  # Handle Lambda errors
    
    return flow


def main():
    """Generate the flow JSON file for Terraform deployment."""
    
    print("Generating Counter Flow")
    print("="*60)
    
    flow = generate_counter_flow()    
    compiled = flow.compile()   
    output_path = Path(__file__).parent / "counter_flow.json"
    
    with open(output_path, 'w') as f:
        json.dump(compiled, f, indent=2)
    
    print(f"Flow generated: {output_path}")
    print(f"Total blocks: {len(compiled['Actions'])}")
    print("Next: cd terraform && terraform apply")


if __name__ == "__main__":
    main()
