#!/bin/bash

# Validate a contact flow by creating and deleting it in Amazon Connect
# Usage: ./validate_flow.sh <flow_file.json>

INSTANCE_ID="e1587ab3-b10f-405d-b621-8f8a26669655"
PROFILE="cxforge"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <flow_file.json>"
    exit 1
fi

FLOW_FILE="$1"

if [ ! -f "$FLOW_FILE" ]; then
    echo "Error: File not found"
    exit 1
fi

echo "Validating $(basename "$FLOW_FILE")..."

# Create test flow
TIMESTAMP=$(date +%s)
TEST_FLOW_NAME="test_validation_${TIMESTAMP}"
FLOW_CONTENT=$(cat "$FLOW_FILE" | jq -c '.')

result=$(aws connect create-contact-flow \
  --instance-id "$INSTANCE_ID" \
  --name "$TEST_FLOW_NAME" \
  --type "CONTACT_FLOW" \
  --content "$FLOW_CONTENT" \
  --profile "$PROFILE" \
  --output json 2>&1)

if [ $? -eq 0 ]; then
    echo "✓ Valid"
    
    # Clean up
    flow_id=$(echo "$result" | jq -r '.ContactFlowId')
    aws connect delete-contact-flow \
      --instance-id "$INSTANCE_ID" \
      --contact-flow-id "$flow_id" \
      --profile "$PROFILE" \
      --output json 2>&1 > /dev/null
    
    exit 0
else
    echo "✗ Invalid"
    echo "$result" | grep -i "error" | head -3
    exit 1
fi
