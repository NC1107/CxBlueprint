#!/usr/bin/env python3
"""
Comprehensive test of hierarchical layout algorithm
Demonstrates:
- Layer assignment (topological ordering)
- Lane assignment (branch fan-out)
- Error path swim lanes
- Merge point handling
- Collision detection
"""
import sys
sys.path.insert(0, '../src')

from flow_builder import ContactFlowBuilder

# Create flow with debug enabled
flow = ContactFlowBuilder("Comprehensive Layout Test", debug=True)

# Entry point
welcome = flow.play_prompt("Welcome! This flow demonstrates hierarchical layout.")

# Layer 1: Main router
main_router = flow.get_input("Press 1 for Sales, 2 for Support, 3 for Info, or 0 for Operator", timeout=10)
welcome.then(main_router)

# === SALES PATH (Branch 1) ===
# Layer 2
sales_greeting = flow.play_prompt("Sales department. Let me help you today.")

# Layer 3: Sales sub-menu with multiple options
sales_menu = flow.get_input("Press 1 for New Business, 2 for Existing Account, or 3 for Billing", timeout=10)
sales_greeting.then(sales_menu)

# Layer 4: Sales endpoints
sales_new = flow.play_prompt("Connecting you to New Business Sales...")
sales_existing = flow.play_prompt("Connecting you to Account Management...")
sales_billing = flow.play_prompt("Connecting you to Sales Billing...")
sales_disconnect = flow.disconnect()

sales_menu.when("1", sales_new).when("2", sales_existing).when("3", sales_billing).otherwise(sales_disconnect)
sales_menu.on_error("InputTimeLimitExceeded", sales_disconnect)
sales_menu.on_error("NoMatchingCondition", sales_disconnect)
sales_menu.on_error("NoMatchingError", sales_disconnect)

sales_new.then(sales_disconnect)
sales_existing.then(sales_disconnect)
sales_billing.then(sales_disconnect)

# === SUPPORT PATH (Branch 2) ===
# Layer 2
support_greeting = flow.play_prompt("Technical Support. We're here to assist you.")

# Layer 3: Support menu
support_menu = flow.get_input("Press 1 for Technical Issue, 2 for Account Help, or 3 for Cancellation", timeout=10)
support_greeting.then(support_menu)

# Layer 4: Support endpoints
support_technical = flow.play_prompt("Connecting you to Technical Support...")
support_account = flow.play_prompt("Connecting you to Account Support...")
support_cancel = flow.play_prompt("We're sorry to see you go. Connecting to retention team...")
support_disconnect = flow.disconnect()

support_menu.when("1", support_technical).when("2", support_account).when("3", support_cancel).otherwise(support_disconnect)
support_menu.on_error("InputTimeLimitExceeded", support_disconnect)
support_menu.on_error("NoMatchingCondition", support_disconnect)
support_menu.on_error("NoMatchingError", support_disconnect)

support_technical.then(support_disconnect)
support_account.then(support_disconnect)
support_cancel.then(support_disconnect)

# === INFO PATH (Branch 3) - Simple path ===
# Layer 2
info_message = flow.play_prompt("For general information, please visit our website at example.com")
info_disconnect = flow.disconnect()
info_message.then(info_disconnect)

# === OPERATOR PATH (Branch 4) - Direct to operator ===
# Layer 2
operator_message = flow.play_prompt("Connecting you to an operator. Please hold.")
operator_disconnect = flow.disconnect()
operator_message.then(operator_disconnect)

# Wire up main router with all branches
main_router.when("1", sales_greeting).when("2", support_greeting).when("3", info_message).when("0", operator_message)

# Error handling for main router - goes to operator
main_router.otherwise(operator_message)
main_router.on_error("InputTimeLimitExceeded", operator_message)
main_router.on_error("NoMatchingCondition", operator_message)
main_router.on_error("NoMatchingError", operator_message)

# Compile
print("\n" + "="*70)
print("COMPILING COMPREHENSIVE LAYOUT TEST")
print("="*70)
print("\nThis flow demonstrates:")
print("  • 4 main branches from entry router")
print("  • 2 branches with sub-menus (Sales, Support)")
print("  • 2 branches with simple paths (Info, Operator)")
print("  • Multiple merge points (disconnect blocks)")
print("  • Error handling swim lanes")
print("  • Hierarchical layer assignment")
print("  • Lane-based horizontal positioning")
print("\n")

flow.compile_to_file("../src/output/comprehensive_layout.json")

print("\n" + "="*70)
print("ANALYZING RESULT")
print("="*70)

import json
with open("../src/output/comprehensive_layout.json") as f:
    data = json.load(f)

metadata = data['Metadata']['ActionMetadata']
positions = [(id, meta['position']) for id, meta in metadata.items()]

# Check for overlaps
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
    print('\nNo overlaps detected! Perfect spacing.')

# Calculate canvas bounds
x_coords = [pos["x"] for _, pos in positions]
y_coords = [pos["y"] for _, pos in positions]
print(f'\nCanvas dimensions:')
print(f'  Width:  {max(x_coords) - min(x_coords)}px  (X: {min(x_coords)} to {max(x_coords)})')
print(f'  Height: {max(y_coords) - min(y_coords)}px  (Y: {min(y_coords)} to {max(y_coords)})')

print(f'\nTotal blocks: {len(data["Actions"])}')
print("="*70)
