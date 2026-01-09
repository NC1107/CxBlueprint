"""
Simple Counter Lambda - stores count in /tmp
"""
import json
import os

counter_file = '/tmp/counter.txt'

def lambda_handler(event, context):
    """Increment counter in /tmp and return the count"""
    
    try:
        # Try to read current count
        if os.path.exists(counter_file):
            with open(counter_file, 'r') as f:
                count = int(f.read().strip())
        else:
            count = 0
        
        # Increment
        count += 1
        
        # Write back
        with open(counter_file, 'w') as f:
            f.write(str(count))
        
        print(f"Counter incremented to: {count}")
        
        # Return for Connect to use as $.External.count
        return {
            'count': str(count),
            'success': 'true'
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'count': '0',
            'success': 'false',
            'error': str(e)
        }
