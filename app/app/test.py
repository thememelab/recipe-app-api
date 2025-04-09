""" Sample tests"""

from django.test import SimpleTestCase
from app import calc


class Calctest(SimpleTestCase):
    """ test the calc module."""

    def test_add_numbers(self):
        """Test adding numbers together. """
        res = calc.add(5,6)

        self.assertEqual(res,11)

    def test_subtract_numbers(self):
        """Subtracting numbers from one another"""
        res =  calc.subtract(10,15)
        self.assertEqual(res,5)
