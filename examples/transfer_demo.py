"""
Transfer Flow Example - Shows hello and goodbye flows working together
"""
import sys
sys.path.insert(0, '../src')
from flow_builder import ContactFlowBuilder
import json
from pathlib import Path


def create_transfer_demo():
    """Demo showing how flows transfer to each other."""
    
    print("🔄 TRANSFER FLOW DEMO")
    print("="*60)
    
    # Step 1: Create Goodbye Flow first (so we have its ID)
    print("1. Creating Goodbye Flow...")
    goodbye_flow = ContactFlowBuilder("Goodbye Flow")
    goodbye_msg = goodbye_flow.play_prompt("Goodbye! Thank you for calling. Have a great day!")
    disconnect = goodbye_flow.disconnect()
    goodbye_msg.then(disconnect)
    
    # Save goodbye flow
    goodbye_compiled = goodbye_flow.compile()
    goodbye_path = Path(__file__).parent.parent / "src" / "output" / "demo_goodbye_flow.json"
    goodbye_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(goodbye_path, 'w') as f:
        json.dump(goodbye_compiled, f, indent=2)
    
    # Get the flow ID (in production this would be the deployed flow ARN)
    goodbye_flow_id = "arn:aws:connect:us-east-1:123456789012:instance/demo-instance/contact-flow/" + goodbye_compiled['StartAction']
    
    print(f"   ✅ Goodbye Flow ID: {goodbye_flow_id[-30:]}")
    
    # Step 2: Create Hello Flow that transfers to Goodbye Flow
    print("2. Creating Hello Flow with transfer...")
    hello_flow = ContactFlowBuilder("Hello Flow")
    hello_msg = hello_flow.play_prompt("Hello! Welcome to our demo system.")
    transfer = hello_flow.transfer_to_flow(goodbye_flow_id)
    hello_msg.then(transfer)
    
    # Save hello flow
    hello_compiled = hello_flow.compile()
    hello_path = Path(__file__).parent.parent / "src" / "output" / "demo_hello_flow.json"
    
    with open(hello_path, 'w') as f:
        json.dump(hello_compiled, f, indent=2)
    
    print(f"   ✅ Hello Flow transfers to: {goodbye_flow_id[-30:]}")
    
    print("\n3. Flow Execution Path:")
    print("   📞 Customer calls → Hello Flow")
    print("   💬 'Hello! Welcome to our demo system.'")
    print("   🔄 Transfer to → Goodbye Flow")  
    print("   💬 'Goodbye! Thank you for calling. Have a great day!'")
    print("   📴 Disconnect")
    
    print("\n4. Deployment Notes:")
    print("   • Deploy goodbye flow first to get real ARN")
    print("   • Update hello flow with actual goodbye flow ARN") 
    print("   • Both flows can be independently managed")
    print("   • Transfer allows modular flow design")
    
    print(f"\n5. Generated Files:")
    print(f"   Hello Flow: {hello_path}")
    print(f"   Goodbye Flow: {goodbye_path}")
    
    return hello_compiled, goodbye_compiled


def main():
    hello_data, goodbye_data = create_transfer_demo()
    print(f"Generated hello flow with {len(hello_data['Actions'])} blocks")
    print(f"Generated goodbye flow with {len(goodbye_data['Actions'])} blocks")


if __name__ == "__main__":
    main()