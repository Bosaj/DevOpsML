import pytest
from src.Ex1 import addition, soustraction, multiplication, division

# Tests pour addition
def test_addition_positifs():
    assert addition(2, 3) == 5

def test_addition_negatifs():
    assert addition(-2, -3) == -5

def test_addition_mixte():
    assert addition(5, -3) == 2

def test_addition_zero():
    assert addition(0, 5) == 5

# Tests pour soustraction
def test_soustraction_positifs():
    assert soustraction(5, 3) == 2

def test_soustraction_negatifs():
    assert soustraction(-5, -3) == -2

def test_soustraction_mixte():
    assert soustraction(5, -3) == 8

def test_soustraction_zero():
    assert soustraction(5, 0) == 5

# Tests pour multiplication
def test_multiplication_positifs():
    assert multiplication(2, 3) == 6

def test_multiplication_negatifs():
    assert multiplication(-2, -3) == 6

def test_multiplication_mixte():
    assert multiplication(-2, 3) == -6

def test_multiplication_zero():
    assert multiplication(5, 0) == 0

# Tests pour division
def test_division_positifs():
    assert division(6, 3) == 2

def test_division_negatifs():
    assert division(-6, -3) == 2

def test_division_mixte():
    assert division(-6, 3) == -2

def test_division_decimale():
    assert division(5, 2) == 2.5

def test_division_par_zero():
    with pytest.raises(ValueError, match="Division par zéro impossible"):
        division(5, 0)