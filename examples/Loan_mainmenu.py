import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from flow_builder import ContactFlowBuilder

flow = ContactFlowBuilder("Loan Center Main Menu", debug=True)

# Welcome message
welcome = flow.play_prompt("Thank you for calling federal student aid")

# Set initial attributes
set_attributes = flow.update_attributes(
    caller_intent="main_menu",
    loan_intent="foreclosed"
)

# First attempt at getting loan balance
main_menu = flow.get_input(
    "How much is your loan balance remaining? Press 1 for 10k, 2 for 50k, 3 for 100k, or 4 for unknown.",
    timeout=10
)

# Retry message (only played on retry path)
retry_msg = flow.play_prompt("I didn't catch that. Let me repeat the options.")

# Second attempt - same prompt
retry_menu = flow.get_input(
    "How much is your loan balance remaining? Press 1 for 10k, 2 for 50k, 3 for 100k, or 4 for unknown.",
    timeout=10
)

# Second retry message
final_retry_msg = flow.play_prompt("Let me try one more time.")

# Third and final attempt
final_menu = flow.get_input(
    "How much is your loan balance remaining? Press 1 for 10k, 2 for 50k, 3 for 100k, or 4 for unknown.",
    timeout=10
)

# Response messages with attribute setting
balance_10k_attrs = flow.update_attributes(loan_balance="10k")
balance_10k_msg = flow.play_prompt("Your loan balance is 10k")

balance_50k_attrs = flow.update_attributes(loan_balance="50k")
balance_50k_msg = flow.play_prompt("Your loan balance is 50k")

balance_100k_attrs = flow.update_attributes(loan_balance="100k")
balance_100k_msg = flow.play_prompt("Your loan balance is 100k")

balance_unknown_attrs = flow.update_attributes(loan_balance="unknown")
balance_unknown_msg = flow.play_prompt("Your loan balance is unknown")

# Final error message
final_error = flow.play_prompt("I'm sorry, I couldn't process your request. Please call back and try again. Goodbye.")

# Disconnect block
disconnect = flow.disconnect()

# Wire up the flow
welcome.then(set_attributes)
set_attributes.then(main_menu)

# First menu - on error, go to first retry
main_menu.when("1", balance_10k_attrs) \
    .when("2", balance_50k_attrs) \
    .when("3", balance_100k_attrs) \
    .when("4", balance_unknown_attrs) \
    .otherwise(retry_msg) \
    .on_error("InputTimeLimitExceeded", retry_msg) \
    .on_error("NoMatchingCondition", retry_msg) \
    .on_error("NoMatchingError", retry_msg)

# First retry message leads to second attempt
retry_msg.then(retry_menu)

# Second menu - on error, go to second retry
retry_menu.when("1", balance_10k_attrs) \
    .when("2", balance_50k_attrs) \
    .when("3", balance_100k_attrs) \
    .when("4", balance_unknown_attrs) \
    .otherwise(final_retry_msg) \
    .on_error("InputTimeLimitExceeded", final_retry_msg) \
    .on_error("NoMatchingCondition", final_retry_msg) \
    .on_error("NoMatchingError", final_retry_msg)

# Second retry message leads to final attempt
final_retry_msg.then(final_menu)

# Final menu - on error, give up and disconnect
final_menu.when("1", balance_10k_attrs) \
    .when("2", balance_50k_attrs) \
    .when("3", balance_100k_attrs) \
    .when("4", balance_unknown_attrs) \
    .otherwise(final_error) \
    .on_error("InputTimeLimitExceeded", final_error) \
    .on_error("NoMatchingCondition", final_error) \
    .on_error("NoMatchingError", final_error)

# Connect attribute setting to message playback
balance_10k_attrs.then(balance_10k_msg)
balance_50k_attrs.then(balance_50k_msg)
balance_100k_attrs.then(balance_100k_msg)
balance_unknown_attrs.then(balance_unknown_msg)

# All endpoints disconnect
balance_10k_msg.then(disconnect)
balance_50k_msg.then(disconnect)
balance_100k_msg.then(disconnect)
balance_unknown_msg.then(disconnect)
final_error.then(disconnect)

# Generate the flow JSON
flow.compile_to_file("src/output/loan_center_main_menu.json")
