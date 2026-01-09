#!/bin/bash

# Validate all flows in the output directory
# Usage: ./validate_all_flows.sh

OUTPUT_DIR="./output"
VALIDATOR="./validate_flow.sh"

if [ ! -f "$VALIDATOR" ]; then
    echo "Error: Validator script not found"
    exit 1
fi

chmod +x "$VALIDATOR"

total=$(find "$OUTPUT_DIR" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
echo "Validating $total flows..."
echo ""

valid_count=0
invalid_count=0

for flow_file in "$OUTPUT_DIR"/*.json; do
    if [ -f "$flow_file" ]; then
        "$VALIDATOR" "$flow_file"
        
        if [ $? -eq 0 ]; then
            valid_count=$((valid_count + 1))
        else
            invalid_count=$((invalid_count + 1))
        fi
        
        sleep 1
    fi
done

echo ""
echo "Results: $valid_count valid, $invalid_count invalid"

if [ $invalid_count -eq 0 ]; then
    exit 0
else
    exit 1
fi
