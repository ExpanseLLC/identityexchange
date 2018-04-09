import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hello_world import main


class TestMethods(unittest.TestCase):

    def test_greet(self):
        self.assertEqual(main.Greeter().greet(), 'Hello World!')
