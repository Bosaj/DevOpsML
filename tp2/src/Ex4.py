"""
Exercise 4: CSV operations for integration testing
"""
import csv

def load_users(path):
    """Load users from CSV file"""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [{"name": r["name"], "age": int(r["age"])} for r in reader]

def filter_adults(users):
    """Filter users who are 18 or older"""
    return [u for u in users if u["age"] >= 18]
