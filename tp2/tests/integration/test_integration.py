"""
Integration tests for file and CSV operations (Exercises 3 & 4)
"""
import pytest
import csv
from pathlib import Path


class TestNumberFileIntegration:
    """Tests for Exercise 3: Load numbers from file and sum them"""
    
    @staticmethod
    def load_numbers(path):
        """Load numbers from a file"""
        with open(path, "r", encoding="utf-8") as f:
            return [int(line.strip()) for line in f if line.strip()]
    
    @staticmethod
    def sum_numbers(nums):
        """Calculate sum of numbers"""
        return sum(nums)
    
    def test_load_and_sum_numbers(self, tmp_path):
        """Test loading numbers from file and calculating sum"""
        numbers_file = tmp_path / "numbers.txt"
        numbers_file.write_text("10\n20\n30\n40\n50\n")
        
        numbers = self.load_numbers(numbers_file)
        total = self.sum_numbers(numbers)
        
        assert numbers == [10, 20, 30, 40, 50]
        assert total == 150
    
    def test_load_numbers_with_empty_lines(self, tmp_path):
        """Test loading numbers file with empty lines"""
        numbers_file = tmp_path / "numbers_empty.txt"
        numbers_file.write_text("10\n\n20\n  \n30\n")
        
        numbers = self.load_numbers(numbers_file)
        
        assert numbers == [10, 20, 30]
        assert sum(numbers) == 60
    
    def test_load_empty_file(self, tmp_path):
        """Test loading from empty file"""
        numbers_file = tmp_path / "empty.txt"
        numbers_file.write_text("")
        
        numbers = self.load_numbers(numbers_file)
        
        assert numbers == []
        assert sum(numbers) == 0
    
    def test_load_negative_numbers(self, tmp_path):
        """Test loading file with negative numbers"""
        numbers_file = tmp_path / "negative.txt"
        numbers_file.write_text("-10\n-20\n30\n")
        
        numbers = self.load_numbers(numbers_file)
        
        assert numbers == [-10, -20, 30]
        assert sum(numbers) == 0
    
    def test_load_large_numbers(self, tmp_path):
        """Test loading file with large numbers"""
        numbers_file = tmp_path / "large.txt"
        numbers_file.write_text("1000\n2000\n3000\n")
        
        numbers = self.load_numbers(numbers_file)
        
        assert numbers == [1000, 2000, 3000]
        assert sum(numbers) == 6000


class TestCSVUserIntegration:
    """Tests for Exercise 4: Load users from CSV and filter adults"""
    
    @staticmethod
    def load_users(path):
        """Load users from CSV file"""
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [{"name": r["name"], "age": int(r["age"])} for r in reader]
    
    @staticmethod
    def filter_adults(users):
        """Filter users who are 18 or older"""
        return [u for u in users if u["age"] >= 18]
    
    def test_load_and_filter_adults(self, tmp_path):
        """Test loading users from CSV and filtering adults (age >= 18)"""
        csv_file = tmp_path / "users.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age"])
            writer.writeheader()
            writer.writerows([
                {"name": "Alice", "age": "25"},
                {"name": "Bob", "age": "17"},
                {"name": "Charlie", "age": "30"},
                {"name": "David", "age": "16"},
                {"name": "Eve", "age": "18"},
            ])
        
        users = self.load_users(csv_file)
        adults = self.filter_adults(users)
        
        assert len(users) == 5
        assert len(adults) == 3
        assert adults[0]["name"] == "Alice"
        assert adults[1]["name"] == "Charlie"
        assert adults[2]["name"] == "Eve"
    
    def test_load_all_adults(self, tmp_path):
        """Test when all users are adults"""
        csv_file = tmp_path / "all_adults.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age"])
            writer.writeheader()
            writer.writerows([
                {"name": "Alice", "age": "25"},
                {"name": "Bob", "age": "30"},
                {"name": "Charlie", "age": "45"},
            ])
        
        users = self.load_users(csv_file)
        adults = self.filter_adults(users)
        
        assert len(adults) == 3
    
    def test_load_no_adults(self, tmp_path):
        """Test when no users are adults"""
        csv_file = tmp_path / "no_adults.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age"])
            writer.writeheader()
            writer.writerows([
                {"name": "Alice", "age": "15"},
                {"name": "Bob", "age": "16"},
                {"name": "Charlie", "age": "17"},
            ])
        
        users = self.load_users(csv_file)
        adults = self.filter_adults(users)
        
        assert len(adults) == 0
    
    def test_load_empty_csv(self, tmp_path):
        """Test loading from CSV with only header"""
        csv_file = tmp_path / "empty_users.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age"])
            writer.writeheader()
        
        users = self.load_users(csv_file)
        
        assert len(users) == 0
    
    def test_boundary_age_18(self, tmp_path):
        """Test boundary condition: age exactly 18 should be included"""
        csv_file = tmp_path / "boundary.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age"])
            writer.writeheader()
            writer.writerows([
                {"name": "Exactly18", "age": "18"},
                {"name": "Almost18", "age": "17"},
                {"name": "JustOver18", "age": "19"},
            ])
        
        users = self.load_users(csv_file)
        adults = self.filter_adults(users)
        
        assert len(adults) == 2
        assert adults[0]["name"] == "Exactly18"
        assert adults[1]["name"] == "JustOver18"
