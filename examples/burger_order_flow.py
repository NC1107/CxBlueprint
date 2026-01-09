"""
Example: Complex burger ordering flow with multiple menus
"""
import sys
sys.path.insert(0, '../src')
from flow_builder import ContactFlowBuilder


def create_burger_order_flow():
    """Create a comprehensive burger ordering flow."""
    
    flow = ContactFlowBuilder("Burger Order Flow", debug=True)
    
    # Welcome
    welcome = flow.play_prompt("Welcome to Burger Palace! Thank you for calling.")
    
    # Main menu
    main_menu = flow.get_input("Press 1 to place an order, 2 to track your order, or 3 to speak with an agent", timeout=10)
    
    # Order path
    order_welcome = flow.play_prompt("Great! Let's get your order started.")
    
    # Burger type menu
    burger_menu = flow.get_input("Press 1 for Classic Burger, 2 for Deluxe Burger, or 3 for Veggie Burger", timeout=10)
    
    # Classic burger path
    classic_size = flow.get_input("You selected Classic Burger. Press 1 for Small, 2 for Medium, or 3 for Large", timeout=10)
    classic_confirm = flow.play_prompt("Perfect! Your Classic Burger has been added to your order.")
    
    # Deluxe burger path
    deluxe_size = flow.get_input("You selected Deluxe Burger. Press 1 for Small, 2 for Medium, or 3 for Large", timeout=10)
    deluxe_confirm = flow.play_prompt("Excellent choice! Your Deluxe Burger has been added to your order.")
    
    # Veggie burger path
    veggie_size = flow.get_input("You selected Veggie Burger. Press 1 for Small, 2 for Medium, or 3 for Large", timeout=10)
    veggie_confirm = flow.play_prompt("Great! Your Veggie Burger has been added to your order.")
    
    # Track order path
    track_order = flow.play_prompt("Please hold while we look up your order status.")
    track_result = flow.play_prompt("Your order is being prepared and will be ready in 15 minutes.")
    
    # Agent path
    transfer_msg = flow.play_prompt("Please hold while we connect you to an agent.")
    
    # Thank you messages
    order_thanks = flow.play_prompt("Thank you for your order! You will receive a confirmation text shortly.")
    track_thanks = flow.play_prompt("Thank you for calling Burger Palace!")
    agent_thanks = flow.play_prompt("Thank you for calling. Goodbye.")
    
    # Disconnects
    disconnect_order = flow.disconnect()
    disconnect_track = flow.disconnect()
    disconnect_agent = flow.disconnect()
    disconnect_error = flow.disconnect()
    
    # Wire the flow
    welcome.then(main_menu).on_error("NoMatchingError", disconnect_error)
    
    # Main menu branching
    main_menu.when("1", order_welcome) \
        .when("2", track_order) \
        .when("3", transfer_msg) \
        .otherwise(disconnect_error) \
        .on_error("InputTimeLimitExceeded", disconnect_error) \
        .on_error("NoMatchingCondition", disconnect_error) \
        .on_error("NoMatchingError", disconnect_error)
    
    # Order flow
    order_welcome.then(burger_menu).on_error("NoMatchingError", disconnect_error)
    
    # Burger menu branching
    burger_menu.when("1", classic_size) \
        .when("2", deluxe_size) \
        .when("3", veggie_size) \
        .otherwise(disconnect_error) \
        .on_error("InputTimeLimitExceeded", disconnect_error) \
        .on_error("NoMatchingCondition", disconnect_error) \
        .on_error("NoMatchingError", disconnect_error)
    
    # Classic burger sizes
    classic_size.when("1", classic_confirm) \
        .when("2", classic_confirm) \
        .when("3", classic_confirm) \
        .otherwise(disconnect_error) \
        .on_error("InputTimeLimitExceeded", disconnect_error) \
        .on_error("NoMatchingCondition", disconnect_error) \
        .on_error("NoMatchingError", disconnect_error)
    
    # Deluxe burger sizes
    deluxe_size.when("1", deluxe_confirm) \
        .when("2", deluxe_confirm) \
        .when("3", deluxe_confirm) \
        .otherwise(disconnect_error) \
        .on_error("InputTimeLimitExceeded", disconnect_error) \
        .on_error("NoMatchingCondition", disconnect_error) \
        .on_error("NoMatchingError", disconnect_error)
    
    # Veggie burger sizes
    veggie_size.when("1", veggie_confirm) \
        .when("2", veggie_confirm) \
        .when("3", veggie_confirm) \
        .otherwise(disconnect_error) \
        .on_error("InputTimeLimitExceeded", disconnect_error) \
        .on_error("NoMatchingCondition", disconnect_error) \
        .on_error("NoMatchingError", disconnect_error)
    
    # Order confirmations to thank you
    classic_confirm.then(order_thanks).on_error("NoMatchingError", disconnect_error)
    deluxe_confirm.then(order_thanks).on_error("NoMatchingError", disconnect_error)
    veggie_confirm.then(order_thanks).on_error("NoMatchingError", disconnect_error)
    
    order_thanks.then(disconnect_order).on_error("NoMatchingError", disconnect_order)
    
    # Track order path
    track_order.then(track_result).on_error("NoMatchingError", disconnect_error)
    track_result.then(track_thanks).on_error("NoMatchingError", disconnect_error)
    track_thanks.then(disconnect_track).on_error("NoMatchingError", disconnect_track)
    
    # Agent transfer path
    transfer_msg.then(agent_thanks).on_error("NoMatchingError", disconnect_error)
    agent_thanks.then(disconnect_agent).on_error("NoMatchingError", disconnect_agent)
    
    # Compile
    flow.compile_to_file("../src/output/code_generated_burger.json")
    
    return flow


if __name__ == "__main__":
    flow = create_burger_order_flow()
    print(f"Generated {flow.name} with {len(flow.blocks)} blocks")
