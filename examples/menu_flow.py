"""
Example: Creating a menu flow with input options
"""
import sys
sys.path.insert(0, '../src')
from flow_builder import ContactFlowBuilder


def create_menu_flow():
    """Create a flow with a menu that asks caller to press 1 or 2."""
    
    # Create a new flow
    flow = ContactFlowBuilder("Menu Selection Flow")
    
    # Add blocks
    welcome = flow.play_prompt("Thank you for calling")
    menu = flow.get_input("Please press 1 or 2", timeout=8)
    option_oranges = flow.play_prompt("Oranges")
    option_apples = flow.play_prompt("Apples")
    disconnect = flow.disconnect()
    
    welcome.then(menu).on_error("NoMatchingError", disconnect)
    
    menu.when("1", option_oranges) \
        .when("2", option_apples) \
        .otherwise(disconnect) \
        .on_error("InputTimeLimitExceeded", disconnect) \
        .on_error("NoMatchingCondition", disconnect) \
        .on_error("NoMatchingError", disconnect)
    
    option_oranges.then(disconnect).on_error("NoMatchingError", disconnect)
    option_apples.then(disconnect).on_error("NoMatchingError", disconnect)
    
    # Compile to file
    flow.compile_to_file("../src/output/code_generated_menu.json")
    
    return flow


if __name__ == "__main__":
    flow = create_menu_flow()
    print(f"Generated {flow.name} with {len(flow.blocks)} blocks")
