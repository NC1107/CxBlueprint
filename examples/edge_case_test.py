"""
Edge case test flow: loops, retries, merge points
"""
import sys
sys.path.insert(0, '../src')
from flow_builder import ContactFlowBuilder


def create_edge_case_flow():
    """Create a simple flow with edge cases:
    - Loop back (press 9 to repeat)
    - Retry logic (1 attempt)
    - Merge points (multiple paths to same block)
    - Shared error handlers
    """
    
    flow = ContactFlowBuilder("Edge Case Test", debug=True)
    
    # 1. Start with welcome (set as first block)
    welcome = flow.play_prompt("Welcome! Let's test edge cases.")
    
    # 2. Shared blocks (merge points)
    thank_you = flow.play_prompt("Thank you for calling. Goodbye.")
    disconnect = flow.disconnect()
    thank_you.then(disconnect)
    
    # 3. Main menu with loop back
    main_menu = flow.get_input(
        "Press 1 for account info, 2 for support, or 9 to repeat this menu",
        timeout=10
    )
    welcome.then(main_menu)
    
    # Press 9 loops back to main menu
    main_menu.when("9", main_menu)
    
    # Retry handler - one attempt then fallback
    retry_prompt = flow.play_prompt("I didn't receive your selection. Let me try again.")
    retry_prompt.then(main_menu)
    
    # Main menu errors - first attempt goes to retry, second to shared thank_you
    main_menu.on_error("NoMatchError", retry_prompt)
    main_menu.on_error("Timeout", thank_you)  # Merge point: error goes to shared block
    
    # Option 1: Account info path
    account_info = flow.play_prompt("Your account balance is $1,234.56")
    main_menu.when("1", account_info)
    account_info.then(thank_you)  # Merge point: success path joins shared thank_you
    
    # Option 2: Support path (also merges to thank_you)
    support = flow.play_prompt("Transferring you to our support team")
    main_menu.when("2", support)
    support.then(thank_you)  # Merge point: another path to shared thank_you
    
    return flow


def main():
    print("\n" + "="*70)
    print("EDGE CASE TEST FLOW")
    print("="*70)
    print("\nEdge cases being tested:")
    print("  • Loop back (press 9 → main menu)")
    print("  • Retry logic (1 attempt)")
    print("  • Merge points (multiple paths → thank_you)")
    print("  • Shared disconnect block")
    print()
    
    flow = create_edge_case_flow()
    
    # Manual compilation and save
    import json
    from pathlib import Path
    
    compiled = flow.compile()
    # Use absolute path to ensure it goes to the right place
    output_path = Path(__file__).parent.parent / "src" / "output" / "edge_case_test.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(compiled, f, indent=2)
    
    print(f"\nFlow manually compiled to: {output_path}")
    print(f"   Total Actions: {len(compiled['Actions'])}")
    print(f"   Positioned blocks: {len(compiled['Metadata']['ActionMetadata'])}")
    
    print(f"\nFlow compiled to: {output_path}")
    print("\n" + "="*70)
    print("FLOW STRUCTURE")
    print("="*70)
    print("""
Main Menu (press 1, 2, or 9)
    ├─ 1 → Account Info → Thank You → Disconnect
    ├─ 2 → Support → Thank You → Disconnect (MERGE)
    ├─ 9 → Main Menu (LOOP BACK)
    ├─ NoMatchError → Retry → Main Menu (RETRY LOOP)
    └─ Timeout → Thank You → Disconnect (MERGE + ERROR PATH)

Key observations:
  • Main menu can loop back to itself (press 9)
  • Retry creates a small loop back to main menu
  • Thank You is a merge point (3 paths converge here)
  • Disconnect is the final merge point
  • One error path skips retry and goes straight to thank_you
""")
    print("="*70)


if __name__ == "__main__":
    main()
