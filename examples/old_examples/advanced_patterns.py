"""
Advanced Flow Example - Demonstrating different block usage patterns

Shows three ways to use the ContactFlowBuilder:
1. Fluent API for common blocks
2. Convenience methods for complex blocks
3. Direct instantiation with add() for specialized blocks
"""
import sys
sys.path.insert(0, '../src')
from flow_builder import ContactFlowBuilder
from blocks.types import LexV2Bot, ViewResource, Media
from blocks.contact_actions import CreateTask
import json
from pathlib import Path
import uuid


def create_advanced_flow():
    """Create a flow showing multiple usage patterns."""
    
    flow = ContactFlowBuilder("Advanced Flow Demo", debug=True)
    
    # PATTERN 1: FLUENT API (Simple, common blocks)
    
    welcome = flow.play_prompt("Welcome to our advanced support system.")
    
    # Get customer input with fluent API
    main_menu = flow.get_input("Press 1 for account info, 2 for technical support, or 3 for billing.", timeout=10)
    welcome.then(main_menu)
    
    # PATTERN 2: CONVENIENCE METHODS (Common complex blocks)
    
    # Option 1: Account balance via Lambda
    balance_check = flow.play_prompt("Let me check your balance...")
    main_menu.when("1", balance_check)
    
    # Use convenience method for Lambda invocation
    balance_lambda = flow.invoke_lambda(
        function_arn="{{BALANCE_LAMBDA_ARN}}",
        timeout_seconds="10"
    )
    balance_check.then(balance_lambda)
    
    balance_msg = flow.play_prompt("Your current balance is...")
    balance_lambda.then(balance_msg)
    
    # Option 2: Technical support with Lex bot
    tech_intro = flow.play_prompt("Connecting you to our AI technical assistant...")
    main_menu.when("2", tech_intro)
    
    # Use convenience method for Lex bot
    lex_bot = flow.lex_bot(
        text="How can I help you with technical support today?",
        lex_v2_bot=LexV2Bot(alias_arn="{{LEX_BOT_ARN}}"),
        lex_session_attributes={"category": "technical"}
    )
    tech_intro.then(lex_bot)
    
    # Handle Lex intent: ResetPassword
    reset_lambda = flow.invoke_lambda("{{RESET_PASSWORD_LAMBDA_ARN}}")
    lex_bot.on_intent("ResetPassword", reset_lambda)
    
    reset_msg = flow.play_prompt("I've sent a password reset link to your email.")
    reset_lambda.then(reset_msg)
    
    # Option 3: Billing - show agent view
    billing_intro = flow.play_prompt("Let me pull up your billing information...")
    main_menu.when("3", billing_intro)
    
    billing_view = flow.show_view(
        view_resource=ViewResource(
            id="{{BILLING_VIEW_ID}}",
            version="1.0"
        ),
        view_data={"type": "billing", "detailed": "true"}
    )
    billing_intro.then(billing_view)
    
    billing_msg = flow.play_prompt("I've displayed your billing details.")
    billing_view.then(billing_msg)
    
    # PATTERN 3: DIRECT INSTANTIATION (Specialized/custom blocks)
    
    # Handle invalid input - create a task for follow-up
    invalid_input = flow.play_prompt("I didn't understand your selection. Let me create a support ticket.")
    main_menu.on_error("NoMatchError", invalid_input)
    
    # Use direct instantiation for specialized block with custom config
    create_task = CreateTask(
        identifier=str(uuid.uuid4()),
        parameters={
            "Name": "Customer Support Request",
            "Description": "Follow up on unclear customer input",
            "TemplateId": "{{SUPPORT_TASK_TEMPLATE}}",
            "Priority": "2"
        }
    )
    task_block = flow.add(create_task)
    invalid_input.then(task_block)
    
    # Confirmation message after task creation
    task_confirm = flow.play_prompt("A support representative will contact you shortly.")
    task_block.then(task_confirm)
    
    # COMMON ENDING
    
    # All paths converge to thank you
    thank_you = flow.play_prompt("Thank you for contacting us. Goodbye!")
    
    # Multiple merge points
    balance_msg.then(thank_you)
    reset_msg.then(thank_you)
    billing_msg.then(thank_you)
    task_confirm.then(thank_you)
    
    # End with disconnect
    disconnect = flow.disconnect()
    thank_you.then(disconnect)
    
    return flow


def main():    
    flow = create_advanced_flow()
    
    # Compile and save
    compiled = flow.compile()
    output_path = Path(__file__).parent.parent / "src" / "output" / "advanced_flow_demo.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(compiled, f, indent=2)
    
    print(f"Flow compiled to: {output_path}")
    print(f"   Total blocks: {len(compiled['Actions'])}")
    print(f"   Positioned blocks: {len(compiled['Metadata']['ActionMetadata'])}")
    
    print("\n BLOCK TYPE BREAKDOWN:")
    block_types = {}
    for action in compiled['Actions']:
        block_type = action['Type']
        block_types[block_type] = block_types.get(block_type, 0) + 1
    
    for block_type, count in sorted(block_types.items()):
        print(f"   {block_type}: {count}")
    
  

if __name__ == "__main__":
    main()