#!/usr/bin/python

import unittest
import blazon
import sys
import os
import Image

# Test for SVG drawing code

SVGDrawingTests = unittest.TestSuite()

class BlazonryTestCase(unittest.TestCase):
    """Will eventually include code that takes as arguments a blazon,
    and the desired state on the shield object that corresponds to it."""
    def testBlazon(self):
        pass
SVGDrawingTests.addTest(BlazonryTestCase)

class ChargesAppendTestCase(unittest.TestCase):
    def testAppend(self):
        """Test for correct behaviour when appending a charge to a field."""
        shield = blazon.Field("vert")
        shield.charges.append(blazon.Saltire("or", "plain"))
        self.assertEqual(len(shield.charges), 1)
        self.assertTrue(shield.charges[0].tincture.color is 'yellow')
SVGDrawingTests.addTest(ChargesAppendTestCase)

class PerPaleTestCase(unittest.TestCase):
    def testPerPale(self):
        shield = blazon.Field()
        shield.tincture = blazon.PerPale(color1="vert", color2="sable")
        # Maybe it's silly to test for this, since it's used only internally
        self.assert_(shield.tincture.pieces is 2)
        for color in shield.tincture.colors:
            self.assert_(color.color is "green" or color.color is "black")
        self.assert_(repr(shield) is not None)
SVGDrawingTests.addTest(PerPaleTestCase)

class PerFessTestCase(unittest.TestCase):
    def testPerFess(self):
        shield = blazon.Field()
        shield.tincture = blazon.PerPale(color1="argent", color2="gules")
        # Ditto
        self.assert_(shield.tincture.pieces is 2)
        for color in shield.tincture.colors:
            self.assert_(color.color is "white" or color.color is "red")
        self.assert_(repr(shield) is not None)
SVGDrawingTests.addTest(PerFessTestCase)
        
class QuarteredTestCase(unittest.TestCase):
    def testQuartered(self):
        shield = blazon.Field()
        shield.tincture = blazon.PerCross(color1="vert", color2="sable")
        for color in shield.tincture.colors:
            self.assert_(color.color is "green" or color.color is "black")
        self.assert_(repr(shield) is not None)
SVGDrawingTests.addTest(QuarteredTestCase)

# TODO:
# When charges are in a group, they must not overlap each other.
# In some specific circumstances, the charges must not cross lines of
# division either.
#
# Lines of division should not cross themselves. This is currently a problem
# with, for instance, embattled/engrailed piles. But the problem should
# probably be fixed before it is tested...

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
        """Check that blazons are properly de-capitalised after being input."""
        test = blazon.Blazon("This is a test")
        self.assertEqual(test.blazon, "this is a test")
    def testPunctuation(self):
        """Check that punctuation isn't stuck to tokens in a way that
        could confuse the parser."""
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
        """Check that all good test blazons parse successfully."""
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
        """Check that all bad test case blazons are not accepted by the parser."""
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
        """Draw all good blazons from the test set, and check if they generate valid SVG."""
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
                    

# One way to test for correct output is to have a collection of
# known-good shields, and compare them to the produced SVG output.
# To account for changes in the SVG structure that is invisible when drawn,
# the gold-standard shield and the candidate shield could be converted to
# bitmaps, and subtracted. If the difference is above a set threshold, it
# should trigger a manual investigation.
#
# FIXME: needs to write this in a more object-oriented way (remove global
# variables &c.)

IMGDIR       = "tests/gsshields/"
TESTSVGFN    = "tests/gsshields/in.svg"
TESTEDIMGFN  = "tests/gsshields/out.png"
TESTBLAZONFN = "tests/gsshields/gsblazons.txt"
MAX_DISCREPANCY = 0.05

def PixelsAlmostSame(a, b):
    for acolor, bcolor in zip(a, b):
        if abs(acolor - bcolor) > 6:
            return False
    return True

def CompImage(tested, gs):
    xsize, ysize = tested.size
    area = xsize * ysize
    wrongpixels = 0
    for x in range(xsize):
        for y in range(ysize):
            if not PixelsAlmostSame(tested.getpixel((x,y)), gs.getpixel((x,y))):
                wrongpixels = wrongpixels + 1
    return float(wrongpixels) / float(area)

def BlazonsAndGoldStandards(filename):
    f = open(filename, "r")
    out = []
    for line in f:
        line = line.strip()
        out.append(BlazonAndGoldStandard(line))
    return out

def BlazonAndGoldStandard(line):
    gs, coadef = line.split(" ", 1)
    return [coadef, gs]

def GenTestImage(coadef, svgfn, imgfn):
    curblazon = blazon.Blazon(coadef)
    shield = curblazon.GetShield()
    f = open(svgfn, "w")
    f.writelines(repr(shield))
    f.close()
    os.system("rsvg -w 100 " + svgfn + " " + imgfn)

class CompImages(unittest.TestCase):
    def testCompImages(self):
        """Compare generated shields to stored gold standards of the same shields."""
        for curblazon, gsfn in BlazonsAndGoldStandards(TESTBLAZONFN):
            GenTestImage(curblazon, TESTSVGFN, TESTEDIMGFN)
            testedshield = Image.open(TESTEDIMGFN)
            goldstandard = Image.open(IMGDIR + gsfn)
            discrepancy = CompImage(testedshield, goldstandard)
            self.assert_(discrepancy < MAX_DISCREPANCY, \
                         "Detected difference of " + \
                         repr(int(discrepancy * 100)) + "%. " + \
                         "This looks different than before:\n" + \
                         curblazon + "\nCompare the shields, and replace " + \
                         "with the new version if OK.\n" + \
                         "Old (expected) version: " + IMGDIR + gsfn + "\n" + \
                         "New version: " + TESTEDIMGFN)


if __name__ == '__main__':
    unittest.main()
