import re
import json


def extract_orange_numbers(text):
    """
    Extract numbers with orange background from a JSON string.
    This function is created to solve Problem Set 1 of the evaluation.
    
    Args:
        text (str): The JSON text to process
    
    Returns:
        list: A list of integers extracted from the text
    """
    # The regex pattern to match JSON object IDs
    pattern = r'"id":(\d+)'
    
    # Find all matches
    matches = re.findall(pattern, text)
    
    # Convert matches to integers
    numbers = [int(match) for match in matches]
    
    return numbers


def parse_json_data(text):
    """
    Parse JSON data from text.
    
    Args:
        text (str): JSON string
    
    Returns:
        dict: Parsed JSON data or None if parsing fails
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
