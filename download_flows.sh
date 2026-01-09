#!/bin/bash

# Download contact flows from Amazon Connect to input/ directory
# Usage: ./download_flows.sh

INSTANCE_ID="e1587ab3-b10f-405d-b621-8f8a26669655"
PROFILE="cxforge"
OUTPUT_DIR="./input"

mkdir -p "$OUTPUT_DIR"

echo "Fetching flows from Connect..."

flows=$(aws connect list-contact-flows \
  --instance-id "$INSTANCE_ID" \
  --profile "$PROFILE" \
  --output json)

flow_ids=$(echo "$flows" | jq -r '.ContactFlowSummaryList[] | .Id')
total=$(echo "$flow_ids" | wc -l | tr -d ' ')

echo "Found $total flows"
echo ""

count=0
for flow_id in $flow_ids; do
  count=$((count + 1))
  
  flow_data=$(aws connect describe-contact-flow \
    --instance-id "$INSTANCE_ID" \
    --contact-flow-id "$flow_id" \
    --profile "$PROFILE" \
    --output json)
  
  flow_name=$(echo "$flow_data" | jq -r '.ContactFlow.Name')
  flow_type=$(echo "$flow_data" | jq -r '.ContactFlow.Type')
  content=$(echo "$flow_data" | jq -r '.ContactFlow.Content')
  
  if [ "$flow_type" != "CONTACT_FLOW" ]; then
    echo "[$count/$total] Skipping $flow_name (type: $flow_type)"
    continue
  fi
  
  if [ "$content" == "null" ] || [ -z "$content" ]; then
    echo "[$count/$total] Skipping $flow_name (no content)"
    continue
  fi
  
  safe_name=$(echo "$flow_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | sed 's/[^a-z0-9_-]/_/g')
  output_file="$OUTPUT_DIR/${safe_name}.json"
  
  echo "$content" | jq '.' > "$output_file"
  echo "[$count/$total] Downloaded $flow_name"
done

echo ""
echo "Done. Flows saved to $OUTPUT_DIR"
