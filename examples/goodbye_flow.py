"""
Goodbye Flow - Simple flow that says goodbye and disconnects
"""
import sys
sys.path.insert(0, '../src')
from flow_builder import ContactFlowBuilder


def create_goodbye_flow():
    """Create a simple goodbye flow."""
    
    flow = ContactFlowBuilder("Goodbye Flow", debug=True)
    
    # Say goodbye
    goodbye = flow.play_prompt("Goodbye! Thank you for using our system. Have a great day!")
    
    # Disconnect
    disconnect = flow.disconnect()
    
    # Chain them together
    goodbye.then(disconnect)
    
    return flow


def main():
    flow = create_goodbye_flow()
    
    from pathlib import Path
    import json
    
    compiled = flow.compile()
    output_path = Path(__file__).parent.parent / "src" / "output" / "goodbye_flow.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(compiled, f, indent=2)
    
    print(f"Generated {flow.name} with {len(compiled['Actions'])} blocks")


if __name__ == "__main__":
    main()