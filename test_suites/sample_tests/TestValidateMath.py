import unittest
from random import randint

from StormTestCase import StormTestCase


class ValidateMathTestCase(StormTestCase):

    def setUp(self):
        self.number_a = 1
        self.number_b = 2


    def test_validate_math_test_case(self):
        self.description = """This is a test function to validate sample of math values and testing if the product
        of those values equal an even number."""
        self.preconditions = """2 sample values are provided"""
        self.postconditions = """Values are added and should be even"""
        self.story_link = "https://www.jeremyhuntsman.com"

        self.start_test_step(name="Add the 2 numbers")

        product_number = self.number_a + self.number_b

        self.end_test_step(product_number)

        self.start_test_step(name="validate the product is an integer")

        self.assertIsInstance(product_number, int)

        self.end_test_step(product_number)

        self.start_test_step(name="validate the product is an even number")

        even_or_odd_number = (product_number / 2)

        self.assertIsInstance(even_or_odd_number, int)

        self.end_test_step(even_or_odd_number)


