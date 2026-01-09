#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from flow_builder import ContactFlowBuilder

def create_loan_center_main_menu():
    """
    Creates a loan call center main menu flow with:
    - Welcome message for federal student aid
    - Sets initial caller attributes
    - Loan balance input menu with 4 options
    - Confirmation of selected balance amount
    - Retry logic for failed inputs
    """
    
    flow = ContactFlowBuilder("Loan Center Main Menu", debug=True)
    
    # Welcome message and set initial attributes
    welcome = flow.play_prompt("Thank you for calling federal student aid")
    
    # Set initial caller attributes
    set_initial_attributes = flow.update_attributes(
        caller_intent="main_menu",
        loan_intent="foreclosed"
    )
    
    # Main menu for loan balance
    loan_balance_menu = flow.get_input(
        "How much is your loan balance remaining? Press 1 for 10k, 2 for 50k, 3 for 100k, 4 for unknown",
        timeout=10
    )
    
    # Retry menu for first failed attempt
    retry_menu_1 = flow.get_input(
        "I didn't receive your input. Please try again. Press 1 for 10k, 2 for 50k, 3 for 100k, 4 for unknown",
        timeout=10
    )
    
    # Retry menu for second failed attempt  
    retry_menu_2 = flow.get_input(
        "Last chance. Please press 1 for 10k, 2 for 50k, 3 for 100k, 4 for unknown",
        timeout=10
    )
    
    # Response messages and attribute setting for each option
    # Option 1: 10k
    confirm_10k = flow.play_prompt("Your loan balance is 10k")
    set_10k_balance = flow.update_attributes(loan_balance="10k")
    
    # Option 2: 50k  
    confirm_50k = flow.play_prompt("Your loan balance is 50k")
    set_50k_balance = flow.update_attributes(loan_balance="50k")
    
    # Option 3: 100k
    confirm_100k = flow.play_prompt("Your loan balance is 100k") 
    set_100k_balance = flow.update_attributes(loan_balance="100k")
    
    # Option 4: unknown
    confirm_unknown = flow.play_prompt("Your loan balance is unknown")
    set_unknown_balance = flow.update_attributes(loan_balance="unknown")
    
    # Final messages
    thank_you = flow.play_prompt("Thank you for providing your loan balance information")
    final_disconnect = flow.disconnect()
    
    # Error handling message for failed inputs
    input_failed = flow.play_prompt("We were unable to process your input. Please call back and try again. Goodbye")
    error_disconnect = flow.disconnect()
    
    # Connect the flow
    welcome.then(set_initial_attributes)
    set_initial_attributes.then(loan_balance_menu)
    
    # Main menu branching with error handling
    loan_balance_menu.when("1", confirm_10k) \
        .when("2", confirm_50k) \
        .when("3", confirm_100k) \
        .when("4", confirm_unknown) \
        .otherwise(retry_menu_1) \
        .on_error("InputTimeLimitExceeded", retry_menu_1) \
        .on_error("NoMatchingCondition", retry_menu_1)
    
    # First retry menu branching
    retry_menu_1.when("1", confirm_10k) \
        .when("2", confirm_50k) \
        .when("3", confirm_100k) \
        .when("4", confirm_unknown) \
        .otherwise(retry_menu_2) \
        .on_error("InputTimeLimitExceeded", retry_menu_2) \
        .on_error("NoMatchingCondition", retry_menu_2)
    
    # Second retry menu branching (last chance)
    retry_menu_2.when("1", confirm_10k) \
        .when("2", confirm_50k) \
        .when("3", confirm_100k) \
        .when("4", confirm_unknown) \
        .otherwise(input_failed) \
        .on_error("InputTimeLimitExceeded", input_failed) \
        .on_error("NoMatchingCondition", input_failed)
    
    # Connect confirmation messages to attribute setting
    confirm_10k.then(set_10k_balance)
    confirm_50k.then(set_50k_balance) 
    confirm_100k.then(set_100k_balance)
    confirm_unknown.then(set_unknown_balance)
    
    # Connect attribute setting to thank you and final disconnect
    set_10k_balance.then(thank_you)
    set_50k_balance.then(thank_you)
    set_100k_balance.then(thank_you)
    set_unknown_balance.then(thank_you)
    
    thank_you.then(final_disconnect)
    
    # Connect error path
    input_failed.then(error_disconnect)
    
    return flow

if __name__ == "__main__":
    # Create and compile the flow
    flow = create_loan_center_main_menu()
    
    # Generate the JSON output
    output_file = "src/output/loan_center_main_menu.json"
    flow.compile_to_file(output_file)
    
    print(f"Loan Center Main Menu flow compiled to: {output_file}")
    print("\nFlow structure:")
    print("1. Welcome message: 'Thank you for calling federal student aid'")
    print("2. Set attributes: caller_intent='main_menu', loan_intent='foreclosed'")
    print("3. Present loan balance menu (1-4 options)")
    print("4. Confirm selection and set loan_balance attribute")
    print("5. Retry logic: 2 additional chances on input failure")
    print("6. Thank you message and disconnect")