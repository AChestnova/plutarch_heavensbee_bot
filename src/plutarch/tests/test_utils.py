import unittest
from plutarch.helpers import SpreadsheetHelper

class TestCalculateExpiry(unittest.TestCase):
    """Test class """
    def test_check_tests(self):
        """Test when the expiration date is within the threshold."""
        f = SpreadsheetHelper.check_tests
        message = f("hello")
        self.assertEqual(message, "hello")
        
if __name__ == "__main__":
    unittest.main()