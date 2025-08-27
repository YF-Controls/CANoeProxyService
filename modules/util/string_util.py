import re

def clear_spaeces(text: str) -> str:
    """Replaces multiple spaces with a single space."""
    return re.sub(r'\s+', ' ', text.strip())


def str_to_float(value: str, default: float = 0.0) -> float:
    '''Convert a string to a float, returning a default value if conversion fails.
    Args:
        value (str): The string to convert.
        default (float): The default value to return if conversion fails.
    Returns:
        float: The converted float value or the default value if conversion fails.
    '''
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
