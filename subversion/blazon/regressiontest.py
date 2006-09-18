#!/usr/bin/python

import unittest
import blazon

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

# Tests for blazonry-related code

def ParsesOK(line):
    """Since blazonry parsing is a moving target, this function should try to test if the blazon it gets will parse in whichever way is currently fashionable."""
    # This is not a very good way of doing it, because YAPPS complains when it fails, creating a lot of clutter on the screen.
    curblazon = blazon.Blazon(line)            
    shield = curblazon.GetShield()
    # YAPPS gives us None when it fails.
    return shield is not None

class CorrectBlazonPreprocessing(unittest.TestCase):
    def testCaps(self):
        test = blazon.Blazon("This is a test")
        self.assertEqual(test.blazon, "this is a test")
    def testPunctuation(self):
        test = blazon.Blazon("This, is, also, a test.")
        self.assertEqual(test.blazon, "this , is , also , a test .")

# The Right Way(tm) would be to create a single test case for each line,
# but I don't know how to do that.
# Apparently, unittest.main() only asks *classes*, not *instances* of
# unittest.TestCase to run themselves.

class CanParseBlazonry(unittest.TestCase):
    def testBlazons(self):
        BlazonTestSuite = unittest.TestSuite()
        testblazons = open("tests/blazons-good.txt", "r")
        for line in testblazons:
            line = line.strip()
            self.assert_(ParsesOK(line))

class CanNotParseBlazonry(unittest.TestCase):
    def testBlazons(self):
        import sys
        import StringIO
        BlazonTestSuite = unittest.TestSuite()
        testblazons = open("tests/blazons-bad.txt", "r")
        for line in testblazons:
            line = line.strip()
            self.assert_(not ParsesOK(line))

# TODO:
# - tests for standards-compliant SVG output
# - tests for through-and-through acceptance of blazons

# One way to test for correct output could be to have a collection of
# known-good shields, and compare them to the produced SVG output.
# To account for changes in the SVG structure that is invisible when drawn,
# the gold-standard shield and the candidate shield could be converted to
# bitmaps, and subtracted. If the difference is above a set threshold, it
# should trigger a manual investigation.

if __name__ == '__main__':
    unittest.main()
