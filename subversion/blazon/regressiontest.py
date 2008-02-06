#!/usr/bin/python

import unittest
import blazon
import arrangement
import sys
import os
import Image

# Bugs that we've seen before.

SpecificBugTraps = unittest.TestSuite()

class FesseStuff(unittest.TestCase):
    def setUp(self):
        self.fesse = blazon.Fesse()
    def testPatternSiblings(self):
        self.assert_(self.fesse.patternSiblings(1) is not None)
    def testPatternContents(self):
        self.assert_(self.fesse.patternContents(1) is not None)
#SpecificBugTraps.addTest(FesseStuff)


# Test for SVG drawing code
# TODO: arrangement in specific loci (in base, in dexter chief, &c.)
# Arrangement in n rows.
# Proper rejection (ie. exception raising) of bogus/conflicting arrangement
# requests.

ArrangementTests = unittest.TestSuite()

class Arrange2by4TestCase(unittest.TestCase):
    def test2by4(self):
        shield = blazon.Field("sable")
        chargegroup = blazon.ChargeGroup(8, blazon.Annulet("or"))
        chargegroup.arrangement = arrangement.ByNumbers()
        chargegroup.arrangement.setRows([2, 2, 2, 2])
        shield.charges.append(chargegroup)
        for charge in shield.charges:
            charge.arrange()
#ArrangementTests.addTest(Arrange2by4TestCase)

class BogusByNumbersTestCase(unittest.TestCase):
    """You are not supposed to have a mismatch between the number of charges
    in a group, and the total number of all charges in all rows."""
    def testBogusByNumbers(self):
        shield = blazon.Field("vert")
        chargegroup = blazon.ChargeGroup(6, blazon.Roundel("argent"))
        chargegroup.arrangement = arrangement.ByNumbers()
        chargegroup.arrangement.setRows([1, 2, 3, 4])
        shield.charges.append(chargegroup)
        for charge in shield.charges:
            self.assertRaises(blazon.ArrangementError, charge.arrange)
#ArrangementTests.addTest(BogusByNumbersTestCase)

class InChiefTestCase(unittest.TestCase):
    def testInChief(self):
        shield = blazon.Field("gules")
        lozenge = blazon.Lozenge("or")
        lozenge.arrangement = arrangement.InChief()
        for charge in shield.charges:
            charge.arrange()
#ArrangementTests.addTest(InChiefTestCase)

class InOrleTestCase(unittest.TestCase):
    def testInOrle(self):
        shield = blazon.Field("gules")
        bezants = blazon.ChargeGroup(9, blazon.Roundel("or"))
        bezants.arrangement = arrangement.InOrle()
        shield.charges.append(bezants)
        for charge in shield.charges:
            charge.arrange()
#ArrangementTests.addTest(InOrleTestCase)

## SVG drawing tests

SVGDrawingTests = unittest.TestSuite()

def HasOnlyTheColors(shield, colors):
    """Check that the shield has all of these colors, and none other colors."""
    import sets
    shieldcolors = sets.Set([c.color for c in shield.tincture.colors])
    wantedcolors = sets.Set(colors)
    return len(shieldcolors - wantedcolors) is 0 and \
           len(wantedcolors - shieldcolors) is 0

class BlazonryTestCase(unittest.TestCase):
    """Will eventually include code that takes as arguments a blazon,
    and the desired state on the shield object that corresponds to it."""
    def testBlazon(self):
        pass
#SVGDrawingTests.addTest(BlazonryTestCase)

class ChargesAppendTestCase(unittest.TestCase):
    def testAppend(self):
        """Test for correct behaviour when appending a charge to a field."""
        shield = blazon.Field("vert")
        shield.charges.append(blazon.Saltire("or", "plain"))
        self.assertEqual(len(shield.charges), 1)
        self.assertTrue(shield.charges[0].tincture.color is 'yellow')
#SVGDrawingTests.addTest(ChargesAppendTestCase)

class Charges10TestCase(unittest.TestCase):
    def test10Charges(self):
        """Test for ability to add a group of ten charges without errors."""
        shield = blazon.Field("sable")
        shield.charges.append(blazon.ChargeGroup(10, blazon.Lozenge("argent")))
        for charge in shield.charges:
            charge.arrange()
#SVGDrawingTests.addTest(Charges10TestCase)

class ChargesTwoGroupsTestCase(unittest.TestCase):
    def test10Charges(self):
        """Test for ability to add *two* group of ten charges without errors."""
        shield = blazon.Field("sable")
        # Currently, this looks wrong, because the annulets end up
        # *on top of* the lozenges.
        shield.charges.append(blazon.ChargeGroup(10, blazon.Lozenge("argent")))
        shield.charges.append(blazon.ChargeGroup(10, blazon.Annulet("or")))
        for charge in shield.charges:
            charge.arrange()
#SVGDrawingTests.addTest(ChargesTwoGroupsTestCase)


class PerPaleTestCase(unittest.TestCase):
    def testPerPale(self):
        shield = blazon.Field()
        shield.tincture = blazon.PerPale(color1="vert", color2="sable")
        # Maybe it's silly to test for number of pieces, since it's used
        # only internally
        self.assert_(shield.tincture.pieces is 2)
        self.assert_(HasOnlyTheColors(shield, ["green", "black"]))
        self.assert_(repr(shield) is not None)
#SVGDrawingTests.addTest(PerPaleTestCase)

class PerFessTestCase(unittest.TestCase):
    def testPerFess(self):
        shield = blazon.Field()
        shield.tincture = blazon.PerPale(color1="argent", color2="gules")
        # Ditto
        self.assert_(shield.tincture.pieces is 2)
        self.assert_(HasOnlyTheColors(shield, ["white", "red"]))
        self.assert_(repr(shield) is not None)
#SVGDrawingTests.addTest(PerFessTestCase)
        
class QuarteredTestCase(unittest.TestCase):
    def testQuartered(self):
        shield = blazon.Field()
        shield.tincture = blazon.PerCross(color1="vert", color2="sable")
        self.assert_(HasOnlyTheColors(shield, ["green", "black"]))
        self.assert_(repr(shield) is not None)
#SVGDrawingTests.addTest(QuarteredTestCase)

class PerSaltireTestCase(unittest.TestCase):
    def testPerSaltire(self):
        shield = blazon.Field()
        shield.tincture = blazon.PerSaltire(color1="azure", color2="argent")
        self.assert_(HasOnlyTheColors(shield, ["blue", "white"]))
        self.assert_(repr(shield) is not None)
#SVGDrawingTests.addTest(PerSaltireTestCase)

class TiercedInPairleTestCase(unittest.TestCase):
    def testTiercedInPairle(self):
        shield = blazon.Field()
        shield.tincture = blazon.PerPall(color1="vert", color2="azure", color3="gules")
        self.assert_(HasOnlyTheColors(shield, ["green", "blue", "red"]))
        self.assert_(repr(shield) is not None)
#SVGDrawingTests.addTest(TiercedInPairleTestCase)

class GyronnyTestCase(unittest.TestCase):
    def testGyronny(self):
        shield = blazon.Field()
        shield.tincture = blazon.Gyronny(color1="purpure", color2="argent")
        self.assert_(HasOnlyTheColors(shield, ["purple", "white"]))
        self.assert_(shield.tincture.pieces is 8)
        self.assert_(repr(shield) is not None)
#SVGDrawingTests.addTest(GyronnyTestCase)

# Various LINEYs...

class PalyTestCase(unittest.TestCase):
    def testPaly(self):
        shield = blazon.Field()
        shield.tincture = blazon.Paly(color1="sable", color2="or")
        self.assert_(HasOnlyTheColors(shield, ["black", "yellow"]))
        self.assert_(shield.tincture.pieces is 8)
        self.assert_(repr(shield) is not None)
#SVGDrawingTests.addTest(PalyTestCase)

class PilyTestCase(unittest.TestCase):
    def testPily(self):
        shield = blazon.Field()
        shield.tincture = blazon.Pily(color1="or", color2="purpure")
        self.assert_(HasOnlyTheColors(shield, ["yellow", "purple"]))
        self.assert_(shield.tincture.pieces is 8)
        self.assert_(repr(shield) is not None)
#SVGDrawingTests.addTest(PilyTestCase)


class ChevronnyTestCase(unittest.TestCase):
    def testPily(self):
        shield = blazon.Field()
        # Not according to the Rule of Tincture, but who cares?
        shield.tincture = blazon.Chevronny(color1="azure", color2="vert")
        self.assert_(HasOnlyTheColors(shield, ["blue", "green"]))
        # Chevronny has 8 pieces like everything else, but is not
        # used in a very sensible way.
        self.assert_(shield.tincture.pieces is 8)
        self.assert_(repr(shield) is not None)
#SVGDrawingTests.addTest(ChevronnyTestCase)


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

#BlazonryTests.addTest(CorrectBlazonPreprocessing)

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
#BlazonryTests.addTest(CanParseBlazonry)

## Put the following test back if and when we suspect the parser of
## accepting bogus input. (This does not currently seem to be an
## important risk, and it creates a bit of spurious output.)
# class CanNotParseBlazonry(unittest.TestCase):
#     def testBlazons(self):
#         """Check that all bad test case blazons are not accepted by the parser."""
#         import sys
#         BlazonTestSuite = unittest.TestSuite()
#         testblazons = open("tests/blazons-bad.txt", "r")
#         for line in testblazons:
#             line = line.strip()
#             self.assert_(not ParsesOK(line))
# BlazonryTests.addTest(CanNotParseBlazonry)

# Tests for through-and-through acceptance of blazons

PipelineTests = unittest.TestSuite()

class PurpureALozengeArgent(unittest.TestCase):
    def testBlazon(self):
        line = "Purpure, a lozenge argent."
        curblazon = blazon.Blazon(line)            
        shield = curblazon.GetShield()
        # What is missing here is a way of retrieving the *actions* generated
        # by the blazon, before those actions are actually executed.
#PipelineTests.addTest(PurpureALozengeArgent)

# - tests for standards-compliant SVG output
from xml.parsers.xmlproc import xmlproc
from xml.parsers.xmlproc import xmlval
from xml.parsers.xmlproc import xmldtd

class DummyErrorHandler(xmlval.ErrorHandler):
    def warning(self, msg):
        # Do not print warnings.
        pass

def WarningLess_load_dtd(sysid):
    # Cut & paste job from libs, with the following important change:
    from xml.parsers.xmlproc import dtdparser
    from xml.parsers.xmlproc import utils
    dp=dtdparser.DTDParser()
    # Shup up about the warnings.
    dp.set_error_handler(DummyErrorHandler(dp))
    dtd=xmldtd.CompleteDTD(dp)
    dp.set_dtd_consumer(dtd)
    dp.parse_resource(sysid)
    return dtd

class ValidateSVGofBlazons(unittest.TestCase):
    def setUp(self):
        dtd_filename = "tests/svg10.dtd"
        # self.dtd = xmldtd.load_dtd(dtd_filename)
        self.dtd = WarningLess_load_dtd(dtd_filename)
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
        self.parser.dtd = self.dtd
        self.parser.ent = self.dtd
        self.parser.feed(XML)
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
    tested = NonTransparentPart(tested)
    gs = NonTransparentPart(gs)
    gxsize, gysize = gs.size
    txsize, tysize = tested.size
    # Compare only the common subset of the images.
    if gxsize < txsize:
        xsize = gxsize
    else:
        xsize = txsize
    if gysize < tysize:
        ysize = gysize
    else:
        ysize = tysize
    area = xsize * ysize
    wrongpixels = 0
    for x in range(xsize):
        for y in range(ysize):
            if not PixelsAlmostSame(tested.getpixel((x,y)), gs.getpixel((x,y))):
                wrongpixels = wrongpixels + 1
    return float(wrongpixels) / float(area)

def NonTransparentPart(image):
    """Problem: if the shield moves around in the image file, we are misled to
    believe that it has changed. To remedy this, only count lines that
    contain non-transparent pixels."""
    return image.crop(image.getbbox())

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

def RunAllTests():
    unittest.main()

if __name__ == '__main__':
    RunAllTests()
