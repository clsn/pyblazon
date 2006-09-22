#!/usr/bin/python

import unittest
import blazon
import sys

# Test for SVG drawing code

SVGDrawingTests = unittest.TestSuite()

class BlazonryTestCase(unittest.TestCase):
    """Will eventually include code that takes as arguments a blazon,
    and the desired state on the shield object that corresponds to it."""
    def testBlazon(self):
        pass
SVGDrawingTests.addTest(BlazonryTestCase)

class ChargesAppendTestCase(unittest.TestCase):
    """Test for correct behaviour when appending a charge to a field."""
    def testAppend(self):
        shield = blazon.Field("vert")
        shield.charges.append(blazon.Saltire("or", "plain"))
        self.assertEqual(len(shield.charges), 1)
        self.assertTrue(shield.charges[0].tincture.color is 'yellow')
SVGDrawingTests.addTest(ChargesAppendTestCase)

# Tests for blazonry-related code

BlazonryTests = unittest.TestSuite()

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
        import re
        test = blazon.Blazon("This, is, also, a test.")
        # Whatever the text normalizer done, it should not allow
        # punctuation to attach to a word.
        self.assert_(re.match("[a-z][\,\.]", test.GetBlazon()) is None)

BlazonryTests.addTest(CorrectBlazonPreprocessing)

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
            try:
                self.assert_(ParsesOK(line), "This does not parse: " + line)
            except AttributeError:
                print "Could not parse good blazon:"
                print line # Output offending blazon
                raise      # Re-raise
BlazonryTests.addTest(CanParseBlazonry)

class CanNotParseBlazonry(unittest.TestCase):
    def testBlazons(self):
        import sys
        BlazonTestSuite = unittest.TestSuite()
        testblazons = open("tests/blazons-bad.txt", "r")
        for line in testblazons:
            line = line.strip()
            self.assert_(not ParsesOK(line))
BlazonryTests.addTest(CanNotParseBlazonry)

# Tests for through-and-through acceptance of blazons

PipelineTests = unittest.TestSuite()

class PurpureALozengeArgent(unittest.TestCase):
    def testBlazon(self):
        line = "Purpure, a lozenge argent."
        curblazon = blazon.Blazon(line)            
        shield = curblazon.GetShield()
        # What is missing here is a way of retrieving the *actions* generated
        # by the blazon, before those actions are actually executed.
PipelineTests.addTest(PurpureALozengeArgent)

# - tests for standards-compliant SVG output
from xml.parsers.xmlproc import xmlproc
from xml.parsers.xmlproc import xmlval
from xml.parsers.xmlproc import xmldtd

class ValidateSVGofBlazons(unittest.TestCase):
    def setUp(self):
        dtd_filename = "tests/svg10.dtd"
        self.dtd = xmldtd.load_dtd(dtd_filename)
    def testSVG(self):
        testblazons = open("tests/blazons-good.txt", "r")
        for line in testblazons:
            line = line.strip()
            curblazon = blazon.Blazon(line)
            shield = curblazon.GetShield()
            if shield is not None:
                # If the shield *is* empty, it should be caught by other tests.
                try:
                    SVGisValid = self.ValidateXML(repr(shield))
                except SystemExit:
                    SVGisValid = False
                self.assert_(SVGisValid, "Invalid SVG for blazon: " + line)
    def ValidateXML(self, XML):
        # self.parser = xmlval.XMLValidator()
        self.parser = xmlproc.XMLProcessor()
        self.parser.set_application(xmlval.ValidatingApp(self.dtd, self.parser))
        self.parser.dtd = self.dtd
        self.parser.ent = self.dtd
        # self.parser.parseStart()
        self.parser.feed(XML)
 #       self.parser.flush()
 #       self.parser.parseEnd()
        self.parser.close()
        # Big fat assumption: if there were no exceptions, everything went well.
        # I *think* that's the way XMLValidator works, anyway ...
        return True
                    

# TODO:
# One way to test for correct output could be to have a collection of
# known-good shields, and compare them to the produced SVG output.
# To account for changes in the SVG structure that is invisible when drawn,
# the gold-standard shield and the candidate shield could be converted to
# bitmaps, and subtracted. If the difference is above a set threshold, it
# should trigger a manual investigation.

if __name__ == '__main__':
    unittest.main()
