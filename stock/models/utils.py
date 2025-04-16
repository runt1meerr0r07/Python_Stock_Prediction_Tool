def safe_compare(a, b, operator="gt"):
    """Safe comparison that handles None values without errors
    operator can be: "gt" (>), "lt" (<), "gte" (>=), "lte" (<=), "eq" (==)
    Returns False if either value is None
    """
    if a is None or b is None:
        return False
    
    if operator == "gt":
        return a > b
    elif operator == "lt":
        return a < b
    elif operator == "gte":
        return a >= b
    elif operator == "lte":
        return a <= b
    elif operator == "eq":
        return a == b
    return False


def format_large_number(num):
    """Format large numbers to human-readable format with K, M, B suffixes"""
    if num >= 1e9:
        return f"{num/1e9:.2f}B"
    elif num >= 1e6:
        return f"{num/1e6:.2f}M"
    elif num >= 1e3:
        return f"{num/1e3:.2f}K"
    return str(num)