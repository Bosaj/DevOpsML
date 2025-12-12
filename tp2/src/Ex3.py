"""
Exercise 3: File operations for integration testing
"""

def load_numbers(path):
    """Load numbers from a file"""
    with open(path, "r", encoding="utf-8") as f:
        return [int(line.strip()) for line in f if line.strip()]

def sum_numbers(nums):
    """Calculate sum of numbers"""
    return sum(nums)
