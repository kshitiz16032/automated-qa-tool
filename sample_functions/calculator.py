def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]
