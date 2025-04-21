import re
import json


def extract_orange_numbers(text):
    """
    Extract numbers with orange color background from the below text in italics.
    
    Args:
        text (str): JSON text with numbers to extract
    
    Returns:
        list: List of integers extracted from the text
    """
    # Regular expression to find all numbers after "id":
    pattern = r'"id":(\d+)'
    
    # Find all matches
    matches = re.findall(pattern, text)
    
    # Convert matches to integers
    numbers = [int(match) for match in matches]
    
    return numbers


if __name__ == "__main__":
    # The text from Problem Set 1
    json_text = """{"orders":[{"id":1},{"id":2},{"id":3},{"id":4},{"id":5},{"id":6},{"id":7},{"id":8},{"id":9},{"id":10},{"id":11},{"id":648},{"id":649},{"id":650},{"id":651},{"id":652},{"id":653}],"errors":[{"code":3,"message":"[PHP Warning #2] count(): Parameter must be an array or an object that implements Countable (153)"}]}"""
    
    # Extract and print the results
    result = extract_orange_numbers(json_text)
    print("Extracted numbers:", result)
    
    # Alternative method using JSON parsing
    try:
        data = json.loads(json_text)
        order_ids = [order["id"] for order in data["orders"]]
        print("Using JSON parsing:", order_ids)
    except json.JSONDecodeError:
        print("Invalid JSON")
