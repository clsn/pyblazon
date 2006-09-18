#!/usr/bin/python

import unittest
import blazon
import parse

# Test for SVG drawing code

class BlazonryTestCase(unittest.TestCase):
    """Will eventually include code that takes as arguments a blazon,
    and the desired state on the shield object that corresponds to it."""
    def testBlazon(self):
        pass

class ChargesAppendTestCase(unittest.TestCase):
    """Test for correct behaviour when appending a charge to a field."""
    def testAppend(self):
        shield = blazon.Field("vert")
        shield.charges.append(blazon.Saltire("or", "plain"))
        self.assertEqual(len(shield.charges), 1)
        self.assertTrue(shield.charges[0].tincture.color is 'yellow')

# TODO: tests for standards-compliant SVG output

# Tests for blazonry-related code

class CorrectBlazonPreprocessing(unittest.TestCase):
    def testCaps(self):
        test = blazon.Blazon("This is a test")
        self.assertEqual(test.blazon, "this is a test")
    def testPunctuation(self):
        test = blazon.Blazon("This, is, also, a test.")
        self.assertEqual(test.blazon, "this , is , also , a test .")

if __name__ == '__main__':
    unittest.main()
