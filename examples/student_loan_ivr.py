#!/usr/bin/env python3
"""
Student Loan IVR - Complex menu with retry logic and repeat functionality
Demonstrates:
- 2 chances to press correct option (retry pattern)
- Press 9 to repeat message
- Multi-level menu navigation
- Multiple error handling paths
"""
import sys
sys.path.insert(0, '../src')

from flow_builder import ContactFlowBuilder

# Create flow with debug
flow = ContactFlowBuilder("Student Loan IVR", debug=True)

# Entry
welcome = flow.play_prompt("Welcome to Student Loan Services. Please listen carefully as our menu options have changed.")

# Main menu with repeat option
main_menu = flow.play_prompt("Press 1 for Loan Balance and Payments. Press 2 for Deferment or Forbearance. Press 3 for Consolidation. Press 4 to speak with a representative. Press 9 to hear this menu again.")
welcome.then(main_menu)

# Main menu input (first attempt)
main_input_1 = flow.get_input("Please make your selection now", timeout=10)
main_menu.then(main_input_1)

# Main menu input (second attempt - if first fails)
main_retry = flow.play_prompt("I didn't receive your selection. Let me repeat the options. Press 1 for Balance and Payments, 2 for Deferment, 3 for Consolidation, 4 for a representative, or 9 to repeat.")
main_input_2 = flow.get_input("Please make your selection now", timeout=10)
main_retry.then(main_input_2)

# Path 1: Loan balance and payments
balance_menu = flow.play_prompt("Balance and Payments. Press 1 to hear your current balance. Press 2 to make a payment. Press 3 for payment history. Press 9 to return to the main menu.")
balance_input = flow.get_input("Please make your selection", timeout=10)
balance_menu.then(balance_input)

# Balance submenu options
current_balance = flow.play_prompt("Your current loan balance is $45,230. Your next payment of $350 is due on February 15th.")
make_payment = flow.play_prompt("To make a payment, please have your bank account information ready. Transferring you to our secure payment system.")
payment_history = flow.play_prompt("Your last payment of $350 was received on January 15th. You have made 24 consecutive on-time payments.")

balance_done = flow.play_prompt("Is there anything else I can help you with today?")
current_balance.then(balance_done)
make_payment.then(balance_done)
payment_history.then(balance_done)

# Balance input routing
balance_input.when("1", current_balance).when("2", make_payment).when("3", payment_history).when("9", main_menu)
balance_input.otherwise(main_retry)
balance_input.on_error("InputTimeLimitExceeded", main_retry)
balance_input.on_error("NoMatchingCondition", main_retry)
balance_input.on_error("NoMatchingError", main_retry)

# === PATH 2: DEFERMENT OR FORBEARANCE ===
deferment_menu = flow.play_prompt("Deferment and Forbearance options. Press 1 to request a deferment. Press 2 to request forbearance. Press 3 to check your eligibility. Press 9 to return to the main menu.")
deferment_input = flow.get_input("Please make your selection", timeout=10)
deferment_menu.then(deferment_input)

# Deferment submenu options
request_deferment = flow.play_prompt("To request a deferment, you will need to provide documentation of your financial hardship. Transferring you to a specialist.")
request_forbearance = flow.play_prompt("Forbearance allows you to temporarily suspend or reduce your payments. Let me connect you with a forbearance specialist.")
check_eligibility = flow.play_prompt("Based on your account, you are eligible for up to 12 months of economic hardship deferment. Would you like to speak with someone about this?")

deferment_done = flow.play_prompt("Thank you. Is there anything else I can help you with?")
request_deferment.then(deferment_done)
request_forbearance.then(deferment_done)
check_eligibility.then(deferment_done)

# Deferment input routing
deferment_input.when("1", request_deferment).when("2", request_forbearance).when("3", check_eligibility).when("9", main_menu)
deferment_input.otherwise(main_retry)
deferment_input.on_error("InputTimeLimitExceeded", main_retry)
deferment_input.on_error("NoMatchingCondition", main_retry)
deferment_input.on_error("NoMatchingError", main_retry)

# === PATH 3: CONSOLIDATION ===
consolidation_menu = flow.play_prompt("Loan Consolidation. Press 1 to learn about consolidation benefits. Press 2 to check if you qualify. Press 3 to start a consolidation application. Press 9 to return to the main menu.")
consolidation_input = flow.get_input("Please make your selection", timeout=10)
consolidation_menu.then(consolidation_input)

# Consolidation options
consolidation_benefits = flow.play_prompt("Consolidating your loans can simplify your payments and may lower your monthly payment. However, it may also increase the total amount of interest you pay.")
consolidation_qualify = flow.play_prompt("You have 3 eligible federal loans totaling $45,230. You qualify for Direct Consolidation.")
consolidation_apply = flow.play_prompt("Great! I'll transfer you to a consolidation specialist who can help you complete your application.")

consolidation_done = flow.play_prompt("Thank you for considering consolidation. Anything else I can help with?")
consolidation_benefits.then(consolidation_done)
consolidation_qualify.then(consolidation_done)
consolidation_apply.then(consolidation_done)

# Consolidation input routing
consolidation_input.when("1", consolidation_benefits).when("2", consolidation_qualify).when("3", consolidation_apply).when("9", main_menu)
consolidation_input.otherwise(main_retry)
consolidation_input.on_error("InputTimeLimitExceeded", main_retry)
consolidation_input.on_error("NoMatchingCondition", main_retry)
consolidation_input.on_error("NoMatchingError", main_retry)

# === PATH 4: REPRESENTATIVE ===
representative = flow.play_prompt("Please hold while I transfer you to the next available representative. Current wait time is approximately 3 minutes.")
representative_disconnect = flow.disconnect()
representative.then(representative_disconnect)

# Main menu input routing (first attempt)
main_input_1.when("1", balance_menu).when("2", deferment_menu).when("3", consolidation_menu).when("4", representative).when("9", main_menu)
main_input_1.otherwise(main_retry)
main_input_1.on_error("InputTimeLimitExceeded", main_retry)
main_input_1.on_error("NoMatchingCondition", main_retry)
main_input_1.on_error("NoMatchingError", main_retry)

# === MAIN MENU INPUT ROUTING (Second Attempt - Last Chance) ===
# On second failure, go to representative
main_input_2.when("1", balance_menu).when("2", deferment_menu).when("3", consolidation_menu).when("4", representative).when("9", main_menu)
main_input_2.otherwise(representative)  # Give up, send to rep
main_input_2.on_error("InputTimeLimitExceeded", representative)
main_input_2.on_error("NoMatchingCondition", representative)
main_input_2.on_error("NoMatchingError", representative)

# === END FLOW ===
# After any "done" message, ask if they want to do something else
end_input = flow.get_input("Press 1 to return to the main menu, or press 2 to end this call", timeout=10)
balance_done.then(end_input)
deferment_done.then(end_input)
consolidation_done.then(end_input)

goodbye = flow.play_prompt("Thank you for calling Student Loan Services. Have a great day!")
final_disconnect = flow.disconnect()
goodbye.then(final_disconnect)

end_input.when("1", main_menu).when("2", goodbye)
end_input.otherwise(goodbye)
end_input.on_error("InputTimeLimitExceeded", goodbye)
end_input.on_error("NoMatchingCondition", goodbye)
end_input.on_error("NoMatchingError", goodbye)

# Compile
print("\n" + "="*70)
print("COMPILING STUDENT LOAN IVR")
print("="*70)
print("\nFeatures:")
print("  • 2-attempt retry logic (main menu)")
print("  • Press 9 to repeat menu (loops back)")
print("  • 4 main menu options")
print("  • 3 sub-menus with 3-4 options each")
print("  • Graceful fallback to representative")
print("  • Return to main menu or end call options")
print("\n")

flow.compile_to_file("../src/output/student_loan_ivr.json")

print("\n" + "="*70)
print("FLOW ANALYSIS")
print("="*70)

import json
with open("../src/output/student_loan_ivr.json") as f:
    data = json.load(f)

metadata = data['Metadata']['ActionMetadata']
positions = [(id, meta['position']) for id, meta in metadata.items()]

# Check overlaps
overlaps = []
for i, (id1, pos1) in enumerate(positions):
    for j, (id2, pos2) in enumerate(positions[i+1:], i+1):
        x_dist = abs(pos1['x'] - pos2['x'])
        y_dist = abs(pos1['y'] - pos2['y'])
        if x_dist < 200 and y_dist < 200:
            overlaps.append((id1[:8], pos1, id2[:8], pos2, x_dist, y_dist))

if overlaps:
    print(f'\nFound {len(overlaps)} potential overlaps')
else:
    print('\nNo overlaps detected!')

# Stats
x_coords = [pos["x"] for _, pos in positions]
y_coords = [pos["y"] for _, pos in positions]
print(f'\nCanvas: {max(x_coords) - min(x_coords):.0f}px × {max(y_coords) - min(y_coords):.0f}px')
print(f'Total blocks: {len(data["Actions"])}')

# Count block types
from collections import Counter
block_types = Counter(action['Type'] for action in data['Actions'])
print('\nBlock types:')
for block_type, count in sorted(block_types.items()):
    print(f'  {block_type}: {count}')

print("="*70)
