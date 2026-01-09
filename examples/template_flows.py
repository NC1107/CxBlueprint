"""
Hello & Goodbye Flows - Template-based flow dependencies

Shows how to define related flows with template placeholders that get
resolved during Terraform/CDK deployment.
"""
import sys
sys.path.insert(0, '../src')
from flow_builder import ContactFlowBuilder
import json
from pathlib import Path


def create_hello_goodbye_flows():
    """Create both hello and goodbye flows with template references."""
    
    print("🔗 TEMPLATE-BASED FLOW DEPENDENCIES")
    print("="*60)
    
    # 1. Define Goodbye Flow (target of transfer)
    print("1. Creating Goodbye Flow...")
    goodbye_flow = ContactFlowBuilder("Goodbye Flow")
    goodbye_msg = goodbye_flow.play_prompt("Goodbye! Thank you for calling. Have a great day!")
    disconnect = goodbye_flow.disconnect()
    goodbye_msg.then(disconnect)
    
    # 2. Define Hello Flow (references goodbye flow via template)
    print("2. Creating Hello Flow with template reference...")
    hello_flow = ContactFlowBuilder("Hello Flow")
    hello_msg = hello_flow.play_prompt("Hello! Welcome to our system.")
    
    # Use template placeholder - will be resolved during deployment
    transfer = hello_flow.transfer_to_flow("{{GOODBYE_FLOW_ARN}}")
    hello_msg.then(transfer)
    
    return hello_flow, goodbye_flow


def save_flows_with_templates():
    """Save flows showing template approach."""
    hello_flow, goodbye_flow = create_hello_goodbye_flows()
    
    # Compile both flows
    hello_compiled = hello_flow.compile()
    goodbye_compiled = goodbye_flow.compile()
    
    # Save with template names
    output_dir = Path(__file__).parent.parent / "src" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    hello_path = output_dir / "template_hello_flow.json"
    goodbye_path = output_dir / "template_goodbye_flow.json"
    
    with open(hello_path, 'w') as f:
        json.dump(hello_compiled, f, indent=2)
    
    with open(goodbye_path, 'w') as f:
        json.dump(goodbye_compiled, f, indent=2)
    
    print(f"\n3. Generated Template Files:")
    print(f"   Hello: {hello_path}")
    print(f"   Goodbye: {goodbye_path}")
    
    # Show the template reference
    transfer_block = next(a for a in hello_compiled['Actions'] if a['Type'] == 'TransferToFlow')
    template_ref = transfer_block['Parameters']['ContactFlowId']
    print(f"   Template reference: {template_ref}")
    
    return hello_compiled, goodbye_compiled


def show_terraform_integration():
    """Show how Terraform would handle these flows."""
    
    print("\n4. Terraform Integration Example:")
    print("-" * 40)
    
    terraform_example = '''
# terraform/contact_flows.tf

# Deploy goodbye flow first (no dependencies)
resource "aws_connect_contact_flow" "goodbye" {
  instance_id = var.connect_instance_id
  name        = "Goodbye Flow"
  description = "Exit flow that says goodbye and disconnects"
  type        = "CONTACT_FLOW"
  
  # Use our generated JSON as template
  content = file("../src/output/template_goodbye_flow.json")
}

# Deploy hello flow with resolved dependency
resource "aws_connect_contact_flow" "hello" {
  instance_id = var.connect_instance_id
  name        = "Hello Flow"  
  description = "Entry flow that transfers to goodbye flow"
  type        = "CONTACT_FLOW"
  
  # Template substitution - replace {{GOODBYE_FLOW_ARN}} with real ARN
  content = templatefile("../src/output/template_hello_flow.json", {
    GOODBYE_FLOW_ARN = aws_connect_contact_flow.goodbye.arn
  })
  
  # Explicit dependency ensures goodbye deploys first
  depends_on = [aws_connect_contact_flow.goodbye]
}

# Output the flow ARNs for other resources
output "hello_flow_arn" {
  value = aws_connect_contact_flow.hello.arn
}

output "goodbye_flow_arn" {
  value = aws_connect_contact_flow.goodbye.arn
}
'''
    
    print(terraform_example)
    
    print("\n5. Deployment Flow:")
    print("   a) Python generates flows with templates")
    print("   b) Terraform deploys goodbye flow first") 
    print("   c) Terraform gets goodbye flow ARN")
    print("   d) Terraform replaces {{GOODBYE_FLOW_ARN}} in hello flow")
    print("   e) Terraform deploys hello flow with resolved reference")
    print("   f) Both flows now have valid, resolvable references")


def main():
    hello_data, goodbye_data = save_flows_with_templates()
    show_terraform_integration()
    
    print("\n" + "="*60)
    print("BENEFITS OF THIS APPROACH")
    print("="*60)
    print("Single source of truth (one Python file)")
    print("Clear dependency relationship")
    print("Template-based, environment agnostic")
    print("Terraform handles deployment order")
    print("No hardcoded ARNs in source code")
    print("Works across dev/staging/prod environments")
    print("Infrastructure as Code friendly")
    
    print(f"\n📊 Flow Summary:")
    print(f"   Hello Flow: {len(hello_data['Actions'])} blocks")
    print(f"   Goodbye Flow: {len(goodbye_data['Actions'])} blocks")
    print(f"   Template references: 1 ({{GOODBYE_FLOW_ARN}})")


if __name__ == "__main__":
    main()