#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import SVGdraw
import math
import sys
import copy
import re
import ast

from pathstuff import partLine
from treatment import *
from arrangement import ByNumbers

class ArrangementError(Exception):
   """An exception that is raised when we are asked to arrange some charges
   in a way that we don't know how to do."""
   def __init__(self, message):
      self.message = message
   def __str__(self):
      return self.message

# For the sake of argument, let's assume the base background SVG is 100x125
# in user-units, starting from 0,0 at top left.  Most ordinaries will also
# be the same size and same location--only they'll have clipping paths,
# which may also be stroked.  Then we can just fill the whole ordinary (or
# a rectangle filling it).

class Ordinary:
   """The top class for anything that is inside a shield. Instances of direct
   subclasses of this will usually correspond to Ordinaries as it is meant in
   heraldics."""
   id=0
   FESSPTX=50
   FESSPTY=50
   HEIGHT=110
   WIDTH=100

   CHIEFPTY=-FESSPTY+15
   DEXCHIEFX=-FESSPTX+15
   SINCHIEFX=FESSPTX-15

   DEXCHIEF=(DEXCHIEFX,CHIEFPTY)
   SINCHIEF=(SINCHIEFX,CHIEFPTY)
   CHIEFPT=(0,CHIEFPTY)

   FESSEPT=(0,0)

   BASEPT=(0,FESSPTY-6)

   DEXSIDE=(DEXCHIEFX+15,0)
   SINSIDE=(SINCHIEFX-15,0)

   ImageFilters=False                   # Have we done the filters for images?

   def __init__(self,*args,**kwargs):
      self.svg=SVGdraw.group()
      # (x=-Ordinary.FESSPTX,
      #                      y=-Ordinary.FESSPTY,
      #                      width=Ordinary.WIDTH,
      #                      height=Ordinary.HEIGHT,
      #                      viewBox=(-Ordinary.FESSPTX,
      #                               -Ordinary.FESSPTY,
      #                               Ordinary.WIDTH,
      #                               Ordinary.HEIGHT))
      self.setup(*args,**kwargs)

   def setup(self,tincture="none",linetype="plain",*args,**kwargs):
      "setup(tincture, linetype) -- set up the basic info for the ordinary"
      self.done=False
      self.args=args
      self.field=None
      self.kwargs=kwargs
      if type(tincture)==str:
         self.tincture=Treatment(tincture)
      else:
         self.tincture=tincture
      self.lineType=linetype
      self.charges=[]
      self.fimbriation_width=4          # default
      if not hasattr(self,'svg'):
         self.svg=SVGdraw.group()
      # OK, can't set the id of the mask here; mustn't do that
      # in setup because if this charge gets copied then there'll be
      # multiple elements with the same ID, and that's a no-no.  But
      # we can set it later on, in process or in finalizeSVG.
      self.mask=SVGdraw.SVGelement('mask')
      self.svg.addElement(self.mask)
      # Must separate clipPathElt from the mask containing it, since
      # masks can't have transforms, etc.  So it is now a group inside the mask.
      self.clipPathElt=SVGdraw.group(attributes={'fill':'white'})
      self.mask.addElement(self.clipPathElt)
      self.maingroup=SVGdraw.group()
      self.baseRect=SVGdraw.rect(x=-Ordinary.FESSPTX*1.5,
                                 y=-Ordinary.FESSPTY*1.5,
                                 width=Ordinary.WIDTH*2,
                                 height=Ordinary.HEIGHT*2)
      # Not the best solution...
      self.baseRect.charge=self
      self.inverted = False

   def fimbriate(self,color):
      # Only plain colors ATM
      # sys.stderr.write("fimbriating with %s\n"%color)
      self.fimbriation=Treatment.lookup[color]

   def void(self,color):
      "void(color) -- voiding is fimbriating plus filling with 'none'"
      self.fimbriate(color)
      self.tincture=Treatment("none")

   def setOverall(self):
      self.overall=True

   def isOverall(self):
      if hasattr(self,'overall'):
         return self.overall
      else:
         return False

   def be_added(self, parent):
      self.parent=parent
      self.field=parent.field
      # This'll be useful down the road.
      if "transform" not in self.maingroup.attributes:
         self.maingroup.attributes["transform"]=""

   # Is this too brittle a way to do it?
   def do_fimbriation(self):
      "actually do the fimbriation.  Called during process()"
      t=self.clipPathElt.attributes.get("transform")
      if not t:
         t=""
      try:
         t+=self.endtransforms
      except AttributeError:
         pass
      self.maingroup.addElement(SVGdraw.SVGelement('use',
                                                   attributes={"xlink:href":"#%s"%self.clipPath.attributes["id"],
                                                               "stroke":self.fimbriation,
                                                               "stroke-width":self.fimbriation_width,
                                                               "fill":"none",
                                                               "transform": t}))

   def process(self): pass

   def addCharge(self,charge):
      "ord.addCharge(charge) -- place a charge on the ordinary/charge"
      charge.be_added(self)
      self.charges.append(charge)

   def extendCharges(self,charges):
      "ord.extendCharges(chargearray) -- place a bunch of charges on the ordinary"
      for elt in charges:
         self.addCharge(elt)

   def invert(self):
      self.inverted=True
      if not hasattr(self,"clipTransforms"):
         self.clipTransforms=""
      self.clipTransforms += " rotate(180)"

   def orient(self,direction,*args,**kwargs):
      pass

   def modify(self,name,*args,**kwargs):
      # Special cases:
      if name =="inverted":
         self.invert()
      elif name in ("reversed","fesswise","contourny",
                    "bendwise","bendwise sinister","palewise"):
         self.orient(name,**kwargs)
      else:
         # General mucking about!
         # Right, this is for general "modification" of a charge/ordinary.
         # The motivation for this was handling "endorsed" and "cotised"
         # by just giving their names.  BUT it has to be done AFTER the
         # "process" and all, otherwise it doesn't know about the linetype.
         # So we make an attribute full of functions that finalizeSVG will
         # call when it's good and ready.
         if not hasattr(self,"mods"):
            self.mods=[]
         # Will I need (*args,**kwargs) ?
         def it(self):
            try:
               getattr(self,name)(*args, **kwargs)
            except AttributeError:
               # print "Method %s not found."%name
               pass
         self.mods.append(it)


   def finalizeSVG(self):
      "Do all the actual work, recur down into charges, etc, to build the SVG for this ordinary."
      # we really should only ever do this once.
      # if self.done:
      #   return self.svg
      self.process()
      # Do any mods waiting around
      if hasattr(self,"mods"):
         for f in self.mods:
            f(self)
      # Keep the "defs" property around for general use, but fill it
      # automatically if possible.
      if not hasattr(self,"mydefs"):
         # Storage for some kind of pattern/treatment SVG data, I'm not sure
         # what it is...
         # Seems to be some global storage, for countercharging perhaps.
         # Also, seems to only be moved from "defs" when they have
         # finished drawing.
         self.mydefs=[]
      #if hasattr(self.tincture,"id"):
      #   self.defs.append(self.tincture.elt)
      defs=SVGdraw.defs()
      self.svg.addElement(defs)
      self.defsElt=defs
      # NOW we can set the id for the mask
      # I guess we could also use the hash of self.  Whatever.
      self.mask.attributes["id"]="Clip%04d"%Ordinary.id
      Ordinary.id += 1
      self.maingroup.attributes["mask"]="url(#%s)"%self.mask.attributes["id"]
      if hasattr(self,"clipPath"):
         # For fimbriation (at least one way to do it), need an id on the actual
         # path, not just the group:
         self.clipPath.attributes["id"]="ClipPath%04d"%Ordinary.id
         Ordinary.id+=1
         if hasattr(self,"clipTransforms"):
            if "transform" not in self.clipPath.attributes:
               self.clipPath.attributes["transform"]=""
            self.clipPath.attributes["transform"] += self.clipTransforms
      self.baseRect=self.tincture.fill(self.baseRect)
      self.maingroup.addElement(self.baseRect)
      if hasattr(self,"fimbriation"):
           self.do_fimbriation()
      if hasattr(self,"charges"):
         for charge in self.charges:
            try:
                charge.maingroup.attributes["transform"]=self.clipPathElt.attributes["transform"]+charge.maingroup.attributes["transform"]
            except KeyError:
                pass
            self.maingroup.addElement(charge.finalizeSVG())
      if hasattr(self,"newmaingroup"):
         self.maingroup=self.newmaingroup
      self.svg.addElement(self.maingroup)
      # Add in all the defs...
      for i in self.mydefs:
         defs.addElement(i)
      # self.done=True
      # add any last-minute transforms
      if hasattr(self,"endtransforms"):
         if "transform" not in self.clipPathElt.attributes:
            self.clipPathElt.attributes["transform"]=""
         self.clipPathElt.attributes["transform"]+=self.endtransforms
      return self.svg

   def patternContents(self,num):
      """In the absence of other information, where should num charges be
      positioned on top of (ie. "charged with") this ordinary or charge?
      return a list of [scale, pos1, pos2...] for num charges."""
      for elt in self.charges:
         try:
            rv=elt.patternSiblings(num)
            if rv:
               return rv
         except AttributeError:
            pass
      try:
         rv=self.tincture.patternContents(num)
         if rv:
            return rv
      except AttributeError:
         pass
      return None

   @staticmethod
   def invertPattern(pat):
      """Turn the pattern upside-down.
      Useful for "inverted" versions of charges/divisions."""
      for i in range(1,len(pat)):
         x=list(pat[i])
         x[1]*=-1
         try:
            x[3]*=-1
         except IndexError:
            pass
         pat[i]=tuple(x)

   def getBaseURL(self):
      if hasattr(self,"base"):
         return self.base
      try:
         return self.parent.getBaseURL()
      except Exception:
         return None

   def moveto(self,loc):
      pass
   def shiftto(self,loc):
      pass
   def resize(self,x,y=None):
      pass
   def scale(self,x,y=None):
      pass

class TrueOrdinary:
   """
   Marker class, to distinguish between charges and ordinaries, since regular
   class inheritance isn't reliable.  Some ordinaries (e.g. bendlets) are also
   Charges, presumably to enable them to be shifted around easier.

   The criterion: If you have a charge, and then another charge on the shield,
   the two charges should move over and make room for one another more or less
   as equals, in the way that charges pattern.  But a TrueOrdinary does not
   move for a charge, and charges pattern around them.
   """
   pass

class Field(Ordinary,TrueOrdinary):
   "Class for the field as a whole.  It's an ordinary, of sorts."
   std_desc="""This is an SVG of a blazon, a heraldic description of a shield.  It was generated with pyBlazon, by Mark Shoulson and Arnt Richard Johansen"""
   def __init__(self,tincture="argent",base=None,outline=True):
      # Horrendously geeky trick to slip the blazon into the title element
      # even though it is set long after.  The brackets that result are
      # actually good, IMO.  I could get rid of them, but I am not going
      # to.  Set self.blazon to a *list* containing the blazon, which is
      # then passed as the contents of the title element.  We can then
      # change the content of the list without changing the list address
      # itself.
      self.blazon=[None]
      self.svg=SVGdraw.svg(x=0,y=0,width="10cm",height="11cm",
                           viewBox=(-Ordinary.FESSPTX-3,
                                    -Ordinary.FESSPTY-3,
                                    Ordinary.WIDTH+6,
                                    Ordinary.HEIGHT+6))
      #        self.svg.attributes["transform"]="scale(1,-1)"
      self.svg.addElement(SVGdraw.title(self.blazon))
      self.svg.addElement(SVGdraw.description(self.__class__.std_desc))
      self.svg.attributes["xmlns:xlink"]="http://www.w3.org/1999/xlink"
      self.pdata=SVGdraw.pathdata()
      self.pdata.move(-Ordinary.FESSPTX,-Ordinary.FESSPTY)
      self.pdata.vline(Ordinary.HEIGHT/3-Ordinary.FESSPTY)
      self.pdata.bezier(-Ordinary.FESSPTX,
                        Ordinary.HEIGHT*7/8-Ordinary.FESSPTY,
                        0,Ordinary.HEIGHT-Ordinary.FESSPTY,
                        0,Ordinary.HEIGHT-Ordinary.FESSPTY)
      self.pdata.bezier(0,Ordinary.HEIGHT-Ordinary.FESSPTY,
                        Ordinary.FESSPTX,
                        Ordinary.HEIGHT*7/8-Ordinary.FESSPTY,
                        #Ordinary.FESSPTX,-Ordinary.FESSPTY)
                        Ordinary.FESSPTX,Ordinary.HEIGHT/3-Ordinary.FESSPTY)
      self.pdata.vline(-Ordinary.FESSPTY)
      self.pdata.closepath()
      self.charges=[]
      self.setup(tincture)
      # The Field can't be duplicated, so it's safe to set its mask id now.
      # Besides, if we don't then it blows up when it tries to copy it
      # if there's a chief
      self.mask.attributes["id"]="Mask%04d"%Ordinary.id
      Ordinary.id+=1
      self.maingroup.attributes["mask"]="url(#%s)"%self.mask.attributes["id"]
      Ordinary.defs=[]                  # This is a hack.
      self.outline=outline
      # self.maingroup.addElement(SVGdraw.circle(cx=0,cy=0,r=20,fill="red"))
      self.field=self

   def finalizeSVG(self):
      self.clipPath=SVGdraw.path(self.pdata)
      self.clipPathElt.addElement(self.clipPath)
      try:
         if self.tincture.color=="none":
            self.outline=False
      except AttributeError:
         pass
      if self.outline:
         self.svg.addElement(SVGdraw.path(self.pdata,stroke="black",
                                          stroke_width=1,fill="none"))
      super().finalizeSVG()

   # A chief is different.  Adding one depresses the rest of the field.
   def addChief(self, chief):
      """Add a chief, which may depress the rest of the field"""
      self.chief=chief                  # Have to handle this later.

   def addBordure(self,bordure):
      "add a Bordure, given as an argument."
      self.bordure=bordure
      bordure.parent=self

   def setBlazon(self,blazon):
      # Replace the *contents* of the blazon list.
      self.blazon[0]=blazon.replace("&","&amp;"). \
                      replace("<","&lt;").replace(">","&gt;")

   def setBase(self,base):
      self.base=base

   def setOutline(self,outline):
      self.outline=outline

   def __repr__(self):
      """Output the SVG of the whole thing."""
      if "transform" not in self.maingroup.attributes:
         self.maingroup.attributes["transform"]=""
      if hasattr(self,"bordure"):       # Add the bordure before the chief!
         self.maingroup.attributes["transform"]+=" scale(.85)"
         self.borduregroup=SVGdraw.group()
      if hasattr(self,"chief"):
         self.maingroup.attributes["transform"]+=" scale(1,.8) translate(0,15)"
         g=SVGdraw.group()
         g.addElement(self.maingroup)
         g.attributes["mask"]=self.maingroup.attributes["mask"]
         self.newmaingroup=g
      self.finalizeSVG()
      if hasattr(self,"chief"):
         if hasattr(self,"borduregroup"):
            self.borduregroup.attributes["transform"]=" scale(1,.8) translate(0,15)"
            g=SVGdraw.group()
            g.attributes["mask"]=self.maingroup.attributes["mask"]
            g.addElement(self.borduregroup)
            self.bordurecontainer=g
         g=SVGdraw.group()
         g.attributes["mask"]=self.maingroup.attributes["mask"]
         g.addElement(self.chief.finalizeSVG())
         self.svg.addElement(g)
      if hasattr(self,"bordure"):
         self.borduregroup.attributes["mask"]=self.maingroup.attributes["mask"]
         self.borduregroup.addElement(self.bordure.finalizeSVG())
         if hasattr(self,"bordurecontainer"):
            self.svg.addElement(self.bordurecontainer)
            # It really ought to have one or the other...
         elif hasattr(self,"borduregroup"):
            self.svg.addElement(self.borduregroup)
      drawing=SVGdraw.drawing()
      drawing.setSVG(self.svg)
      for thing in Ordinary.defs:
         self.defsElt.addElement(thing)
      return drawing.toXml()

class Charge(Ordinary):
   "Charges are more self-contained than ordinaries, not generally extending off the edges of the field."
   def moveto(self,*args):
      "charge.moveto((x,y)) -- translate the charge to coords (x,y).  Note it's a tuple!"
      # Remember, args[0] is a tuple!
      if "transform" not in self.maingroup.attributes:
         self.maingroup.attributes["transform"]=""
      self.maingroup.attributes["transform"]+=" translate(%.4f,%.4f)" % args[0]

   # Lousy name, but we need a *different* kind of moving, to slide
   # the outline but not the innards/tincture.
   def shiftto(self,*args):
      "charge.shiftto((x,y)) -- like moveto, but slides the outline and not the tincture.  This matters for things like countercharging."
      if "transform" not in self.clipPathElt.attributes:
         self.clipPathElt.attributes["transform"]=""
      self.clipPathElt.attributes["transform"]+=" translate(%.4f,%.4f)"%args[0]

   def scale(self,x,y=None):
      "charge.scale(x,[y]) -- scale the charge."
      if not y:                        # I can't scale by 0 anyway.
         y=x
      if "transform" not in self.maingroup.attributes:
         self.maingroup.attributes["transform"]=""
      self.maingroup.attributes["transform"] += " scale(%.2f,%.2f)"%(x,y)

   # Same as shiftto: changes the size of the outline only.
   def resize(self,x,y=None):
      "Same as scale, but only the outline, as with shiftto."
      if not y:
         y=x
      if "transform" not in self.clipPathElt.attributes:
         self.clipPathElt.attributes["transform"]=""
      self.clipPathElt.attributes["transform"] += " scale(%.2f,%.2f)"%(x,y)

   def orient(self, direction="none", absolute=False, andThen=None):
      """
      charge.orient(direction, [absolute,] [andThen]):

      tilt/turn/flip the charge.  direction is a string: "bendwise",
      "palewise", "fesswise", "reversed", "contourny", etc.  absolute is
      False by default; if True it means it was really specified and don't
      turn this again.  e.g. "argent on a bend sable a billet palewise",
      when you do the bend processing that turns charges bendwise, don't
      turn this one, because it was turned palewise *absolute*.  andThen is
      something of a hack: it's a string that's run with orient after the
      orientation is done.  Lets us accomplish two orientations at once,
      for things like "palewise contourny"
      """
      # Hrm.  These rotations and things have to come at the END of all the
      # transforms, otherwise things wind up moving in the wrong direction
      # when they are scaled down and shifted about to make room for
      # others.
      #
      # If absolute is True, then this is an *absolute* orientation.
      # No other orientations (rotations, in particular) may occur.
      if not hasattr(self,'absoluteRotation'):
         self.absoluteRotation=False
      if not hasattr(self,"endtransforms"):
         self.endtransforms=""
      if direction=="bendwise" and not self.absoluteRotation:
         self.endtransforms+=" rotate(-45)"
      elif direction=="bendwise sinister" and not self.absoluteRotation:
         self.endtransforms+=" rotate(45)"
      elif direction=="contourny" or \
           direction=="reversed":
         self.endtransforms+=" scale(-1.0,1.0)"
      elif direction=="inverted":
         self.invert()
      elif direction=="fesswise" and not self.absoluteRotation:
         # I think by rights individual charges should have to handle these
         # themselves, since for some things palewise is normal, and for
         # others fesswise is.  By default, I'm going to define palewise
         # is normal, and fesswise is a -90 degree turn.  I guess.
         #
         # Going to need to do better than that.  Some charges are fesswise
         # in nature and some are palewise in nature.  Specifying
         # "bendwise" means turning a palewise charge -45deg but turning a
         # fesswise charge +45deg.  Most/all? of the normal geometric
         # charges are palewise in nature, but things like beasts couchant
         # or passant are fesswise.
         self.endtransforms+=" rotate(-90)"
      else:                             # Hope we're being given a number here.
         try:
            num=int(direction)
            self.endtransforms+=" rotate(%d)"%num
         except ValueError:
            pass
      if absolute and direction != "contourny" and direction!="reversed" and \
             direction != "inverted":
         self.absoluteRotation=True
      # Hack to handle "palewise contourny" etc.
      if andThen:
         self.orient(andThen, absolute=absolute)

   def reduced(self):
      self.scale(0.75)

   def enlarged(self):
      self.scale(1.3333333)

   def rotate(self, degrees):
      if "transform" not in self.clipPathElt.attributes:
         self.clipPathElt.attributes["transform"]=""
      self.clipPathElt.attributes["transform"] += " rotate(%d)"%degrees

   def dexterchief(self):
      self.moveto(Ordinary.DEXCHIEF)

   def sinisterchief(self):
      self.moveto(Ordinary.SINCHIEF)

   def chief(self):
      self.moveto(Ordinary.CHIEFPT)

   def addCharge(self,charge):
      Ordinary.addCharge(self,charge)
      # The following appears to make no difference, visually:
      charge.maingroup.attributes["transform"]+=" scale(.8)"
      # Should it be removed?


class Cross(Ordinary,TrueOrdinary):
    """A cross in the heraldic sense (it goes all the way to the edges of the
    shield) NOT a cross couped."""
    def process(self):
        p=partLine()
        p.lineType=self.lineType
        p.move(10,-Ordinary.HEIGHT)
        p.makeline(10,-10,align=1)
        p.makeline(Ordinary.WIDTH,-10)
        p.line(Ordinary.WIDTH,10)
        p.makeline(10,10,align=1)
        p.makeline(10,Ordinary.HEIGHT)
        p.line(-10,Ordinary.HEIGHT)
        p.makeline(-10,10,align=1)
        p.makeline(-Ordinary.WIDTH,10)
        p.line(-Ordinary.WIDTH,-10)
        p.makeline(-10,-10,align=1)
        p.makeline(-10,-Ordinary.HEIGHT)
        p.closepath()
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)

    @staticmethod
    def patternContents(num):
       patterns=[[.3],[.3,(0,0)],             # 0,1
                 [.25,(-30,0),(30,0)],
                 [.25,(-30,0),(30,0),(0,0)], # ???
                 [.25,(-30,0),(30,0),(0,30),(0,-30)],
                 [.25,(-30,0),(30,0),(0,30),(0,-30),(0,0)]]
       try:
          return patterns[num]
       except IndexError:
          return None

    @staticmethod
    def patternSiblings(num):
       patterns=[[.4],[.4,(-26,-26)],   # ???
                 [.4,(-26,-26),(26,-26)], # ???
                 [.4,(-26,-26),(26,-26),(-26,26)], # ???
                 [.3,(-26,-26),(26,-26),(-26,26),(26,26)] # 4 charges
                 ]
       try:
          return patterns[num]
       except IndexError:
          return None


class Fesse(Ordinary,TrueOrdinary):
   "Fesse ordinary: big fat stripe across the middle."
   def process(self):
      p=partLine(-Ordinary.WIDTH, -20)
      # Fesse is unusual: when "embattled", only the *top* line is
      # crenelated, unless it is blazoned "embattled counter-embattled"
      # Hm.  For now, we'll allow/require "counter-embattled" by itself
      # for that.
      p.lineType=self.lineType
      if self.lineType == "embattled":
         p.move(-Ordinary.WIDTH,-20)
         p.makelinerel(Ordinary.WIDTH*3,0)
         p.relline(0,40)
         p.relline(-Ordinary.WIDTH*3,0)
         p.relline(0,-40)
         p.closepath()
      else:
         p.rect(-Ordinary.WIDTH,-20,Ordinary.WIDTH*3,40)
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

   @staticmethod
   def patternContents(num):
      patterns=[[.5],[.5,(0,0)],
                [.5,(-20,0),(20,0)],
                [.35,(-28,0),(28,0),(0,0)],
                [.29,(-33,0),(-11,0),(11,0),(33,0)],
                [.2 ,(-38,0),(-19,0),(0,0),(19,0),(38,0)],
                [.2 ,(-40,0),(-24,0),(-8,0),(8,0),(24,0),(40,0)],
                [.18,(-42,0),(-28,0),(-14,0),(0,0),(14,0),(28,0),(42,0)],
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

   @staticmethod
   def patternSiblings(num):
      patterns=[[.3],[.3,(0,-33)],
                [.3,(0,-33),(0,33)],
                [.3,(-33,-33),(33,-33),(0,33)],
                [.3,(-33,-33),(33,-33),(33,33),(-33,33)],
                [.3,(-33,-33),(0,-33),(33,-33),(-20,33),(20,33)],
                [.3,(-33,-33),(0,-33),(33,-33),(-20,33),(0,44),(20,33)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

class Gore(Ordinary,TrueOrdinary):
   "Fairly ugly-looking (dexter) Gore ordinary."
   # One really bad-looking gore.  I suppose we'll have to improve this.
   def process(self):
      # Any way to do this with lines of partition?
      p=SVGdraw.pathdata()
      p.move(-Ordinary.FESSPTX-2,-Ordinary.FESSPTY)
      p.bezier(-Ordinary.FESSPTX/2, -10,
               -Ordinary.FESSPTX/2, -10,
               0,0)
      p.bezier(-Ordinary.FESSPTX/2, 10,
               -Ordinary.FESSPTX/2, 10,
               -Ordinary.FESSPTX-10, Ordinary.HEIGHT)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

class Bar(Fesse,Charge):
   "diminutive of fesse."
   def process(self):
      p=partLine(-Ordinary.WIDTH, -8)
      p.lineType=self.lineType
      p.rect(-Ordinary.WIDTH, -8, Ordinary.WIDTH*3,16)
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)


   @staticmethod
   def patternWithOthers(num):
      patterns=[[1], [1,(0,0)],
                [1, (0,10), (0,-10)],
                [1, (0,25), (0,0), (0,-25)],
                [(1,.6), (0,30), (0,10), (0,-10), (0,-30)],
                [(1,.5), (0,30), (0,15), (0,0), (0,-15), (0,-30)],
                [(1,.45), (0,40), (0,24), (0,8), (0,-8), (0,-24), (0,-40)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

   def moveto(self,loc):
      Charge.moveto(self,loc)
   def shiftto(self,loc):
      Charge.shiftto(self,loc)
   def scale(self,x,y=None):
      Charge.scale(x,y)
   def resize(self,x,y=None):
      Charge.resize(self,x,y)

class BarGemelle(Bar):
   "Pair of bars"
   def process(self):
      p=partLine()
      p.lineType=self.lineType
      p.rect(-Ordinary.WIDTH,-6,Ordinary.WIDTH*3,5)
      p.rect(-Ordinary.WIDTH,1,Ordinary.WIDTH*3,5)
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

class Saltire(Cross):
   "saltire ordinary: big ol' X"
   def process(self):
      Cross.process(self)
      self.clipPath.attributes["transform"]="rotate(45)"

   @staticmethod
   def patternContents(num):
      patterns=[[.25],[.25,(0,0)],
                [.25,(-26,-26),(26,-26)],
                [.25,(-26,-26),(0,0),(26,-26)],
                [.25,(-26,-26),(-26,26),(26,-26),(26,26)],
                [.25,(-26,-26),(-26,26),(26,-26),(26,26),(0,0)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

   # This works okay for even nums, but not odd ones.
   # FIXME: Should be rewritten.
   @staticmethod
   def patternSiblings(num):
      return Cross.patternContents(num)

class Pall(Ordinary,TrueOrdinary):
   "Pall ordinary: Y-shape"
   def process(self):
      wd=7*math.cos(math.pi/4)
      p=partLine(-Ordinary.WIDTH-wd, -Ordinary.WIDTH+wd)
      p.lineType=self.lineType
      p.makeline(-wd*2,0,align=1)
      p.makeline(-wd*2,Ordinary.HEIGHT)
      p.relhline(4*wd)
      p.makeline(2*wd,0,align=1)
      p.makeline(Ordinary.WIDTH+wd, -Ordinary.WIDTH+wd)
      p.relline(-2*wd,-2*wd)
      p.makeline(0,-wd*2,align=1)
      p.makeline(-Ordinary.WIDTH+wd, -Ordinary.WIDTH-wd)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

   def patternSiblings(self,num):
      patterns=[[.35],[.35,(0,-30)],
                [.35,(-30,0),(30,0)],
                [.35,(-30,0),(30,0),(0,-30)]
                ]
      try:
         res=patterns[num]
      except IndexError:
         return None
      if hasattr(self,"inverted") and self.inverted:
         self.invertPattern(res)
      return res

   def patternContents(self,num):
      patterns=[[.3],[.27,(0,0)],
                [.2,(-18,-18,(),-45),(18,-18,(),45)],
                [.2,(-18,-18,(),-45),(18,-18,(),45),(0,22,(),0)],
                [.2,(-18,-18,(),-45),(18,-18,(),45),(0,22,(),0),(0,0)]
                ]
      try:
         res=patterns[num]
         if hasattr(self,"inverted") and self.inverted:
            self.invertPattern(res)
         return res
      except IndexError:
         return None

class Endorsing(Ordinary,TrueOrdinary):
   "Really just a modification of a Pale, but it behaves like another ordinary (or pair of them"

   # Essentially the same thing on bends, which are just tilted Pales.

   # According to WP, an "endorse" is actually an ordinary in its own
   # right, half the width of a pallet.
   def process(self):
      p=partLine()
      try:
         l,r = self.kwargs['leftparam'], self.kwargs['rightparam']
      except KeyError:
         l,r = -14, 12
      # Only carry over the lineType where it would work, viz. dancetty and
      # wavy (and nothing else?) otherwise leave plain... but then need
      # wider clearance...
      if self.lineType in ['wavy', 'dancetty']:
         p.lineType=self.lineType
      elif self.lineType is not None and self.lineType != 'plain':
         p.lineType='plain'
         l -= 3
         r += 3
      p.rect(l, -2*Ordinary.HEIGHT, 2, Ordinary.HEIGHT*3)
      p.rect(r, -2*Ordinary.HEIGHT, 2, Ordinary.HEIGHT*3)
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)
      # sys.stderr.write(str(self.kwargs)+"\n")
      try:
         self.clipPath.attributes['transform']=self.kwargs['transform']
      except KeyError:
         pass

class Pale(Ordinary,TrueOrdinary):
   "Pale ordinary: vertical stripe"
   def process(self):
      p=partLine()
      p.lineType=self.lineType
      p.rect(-10,-2*Ordinary.HEIGHT,20,Ordinary.HEIGHT*3)
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

   def endorsed(self, *args, **kwargs):
      end=Endorsing(*args, linetype=self.lineType, **kwargs)
      self.parent.addCharge(end)

   @staticmethod
   def patternSiblings(num):
      patterns=[[.4],[.4,(-26,0)],
                [.4,(-26,0),(26,0)],
                [.3,(-26,-26),(-26,26),(26,0)], # ???
                [.3,(-26,-26),(-26,26),(26,-26),(26,26)],
                [.3,(-26,-26),(-26,26),(26,-26),(26,26),(-26,0)],
                [.3,(-26,-26),(-26,26),(26,-26),(26,26),(-26,0),(26,0)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

   @staticmethod
   def patternContents(num):
      patterns=[[.25],[.25,(0,0)],
                [.25,(0,-30),(0,30)],
                [.25,(0,-30),(0,30),(0,0)],
                [.25,(0,-36),(0,12),(0,-12),(0,36)],
                [.25,(0,-40),(0,-20),(0,0),(0,20),(0,40)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

class CanadianPale(Pale):
   def process(self):
      p=partLine()
      p.lineType=self.lineType
      p.rect(-Ordinary.WIDTH/4.0, -Ordinary.HEIGHT, Ordinary.WIDTH/2.0, Ordinary.HEIGHT*3)
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

   @staticmethod
   def patternSiblings(num):
      patterns=[[.25],[.25,(-35,-10)],
                [.25,(-35,-10),(35,-10)],
                [.25,(-35,-36),(-35,16),(35,-10)], # ???
                [.25,(-35,-36),(-35,16),(35,-36),(35,16)],
                [.25,(-35,-36),(-35,16),(35,-36),(35,16),(-35,-10)],
                [.25,(-35,-36),(-35,16),(35,-36),(35,16),(-35,-10),(35,-10)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

   @staticmethod
   def patternContents(num):
      patterns=[[.5],[.5,(0,0)],
                [.5,(0,-30),(0,30)],
                [.5,(0,-30),(0,30),(0,0)],
                [.5,(0,-36),(0,12),(0,-12),(0,36)],
                [.5,(0,-40),(0,-20),(0,0),(0,20),(0,40)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

   def endorsed(self, *args, **kwargs):
      end=Endorsing(*args, linetype=self.lineType, leftparam=-Ordinary.WIDTH/4.0-4, rightparam=Ordinary.WIDTH/4.0+2, **kwargs)
      self.parent.addCharge(end)

class Pallet(Pale,Charge):
   "Pallet ordinary: a diminutive of Pale"
   # Or would this be better done as Paly of an odd number?
   palletwidth=10
   def process(self):
      p=partLine(linetype=self.lineType)
      p.rect(-self.palletwidth/2,
             -2*Ordinary.HEIGHT,self.palletwidth,Ordinary.HEIGHT*3)
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

   def patternWithOthers(self,num):
      rv=[1]
      # Space them evenly. Alter widths so negative space is equal too?
      # That would be paly of odd number!
      spacing=(Ordinary.WIDTH-num*self.palletwidth)/(num+1)
      where=-Ordinary.FESSPTX+spacing+self.palletwidth/2
      for i in range(num):
         rv.append((where, 0))
         where += spacing+self.palletwidth
      return rv

   def endorsed(self,*args,**kwargs):
      try:
         trns=self.maingroup.attributes['transform']
      except KeyError:
         trns=None
      end=Endorsing(*args, linetype=self.lineType, leftparam=-9, rightparam=7, transform=trns, **kwargs)
      self.parent.addCharge(end)

   def moveto(self,loc):
      Charge.moveto(self,loc)
   def shiftto(self,loc):
      Charge.moveto(self,loc)
   def resize(self,x,y=None):
      Charge.resize(self,x,y)
   def scale(self,x,y=None):
      Charge.scale(self,x,y)


class Bend(Ordinary,TrueOrdinary):
   "Bend ordinary.  Diagonal stripe"
   def __init__(self,*args,**kwargs):
      self.setup(*args,**kwargs)
      self.transform="rotate(-45)"

   def process(self):
      # Hmm.  Not necessarily a good idea, but I think I will NOT use the
      # trick here that's used in Saltire, to isolate the rotation in a
      # group so it isn't inherited.  Things on a bend usually ARE
      # rotated.  May need to reconsider this.
      r=partLine()
      r.lineType=self.lineType
      r.rect(-10,-2*Ordinary.HEIGHT,20,Ordinary.HEIGHT*3)
      p=SVGdraw.path(r)
      p.attributes["transform"]=self.transform
      self.clipPath=p
      self.clipPathElt.addElement(p)
      # Hrm.  But now the outer clipping path (?) is clipping the end of
      # the bend??

   def cotised(self,*args,**kwargs):
      cot=Endorsing(*args,linetype=self.lineType,transform=self.transform,**kwargs)
      self.parent.addCharge(cot)

   @staticmethod
   def patternSiblings(num):
      patterns=[[.4],[.4,(26,-26)],
                [.4,(26,-26),(-23,23)],
                [.35,(-23,23),(8,-32),(32,-8)],
                [.35,(8,-32),(32,-8),(-7,29),(-29,7)],
                [.3,(8,-32),(32,-32),(32,-8),(-7,29),(-29,7)],
                [.3,(8,-32),(32,-32),(32,-8),(0,40),(-23,23),(-33,0)],
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

   @staticmethod
   def patternContents(num):
      patterns=[[.25],[.25,(0,0,(),-45)],
                [.25,(-30,-30,(),-45),(26,26,(),-45)],
                [.25,(-30,-30,(),-45),(26,26,(),-45),(0,0,(),-45)],
                [.25,(-30,-30,(),-45),(-12,-12,(),-45),
                 (8,8,(),-45),(26,26,(),-45)],
                [.2 ,(-35,-35,(),-45),(-20,-20,(),-45),(-5,-5,(),-45),
                 (10,10,(),-45),(25,25,(),-45)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None


class Bendlet(Bend,Charge):
   "Diminutive of Bend"
   def process(self):
      r=partLine()
      r.lineType=self.lineType
      r.rect(-5,-2*Ordinary.HEIGHT,10,Ordinary.HEIGHT*3)
      p=SVGdraw.path(r)
      p.attributes["transform"]=self.transform
      self.clipPath=p
      self.clipPathElt.addElement(p)

   @staticmethod
   def patternWithOthers(num):
      patterns=[[1],[1,(0,0)],
                [1,(7,-7),(-7,7)],
                [1,(-15,15),(0,0),(15,-15)],
                [1,(-21,21),(-7,7),(7,-7),(21,-21)],
                [1,(-24,24),(-12,12),(0,0),(12,-12),(24,-24)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

   def cotised(self, *args, **kwargs):
      trns=self.transform
      try:
         trns=self.maingroup.attributes['transform']+' '+trns
      except KeyError:
         pass
      end=Endorsing(*args, linetype=self.lineType, leftparam=-8, rightparam=6, transform=trns, **kwargs)
      self.parent.addCharge(end)

   def moveto(self,loc):
      Charge.moveto(self,loc)
   def shiftto(self,loc):
      Charge.shiftto(self,loc)
   def scale(self,x,y=None):
      Charge.scale(x,y)
   def resize(self,x,y=None):
      Charge.resize(self,x,y)

   def enhanced(self):
      self.moveto((0,-27))

   def debased(self):
      self.moveto((0,27))

class BendSinister(Bend):
   "Reversed bend: slants from upper right to lower left"
   def __init__(self,*args,**kwargs):
      self.setup(*args,**kwargs)
      self.transform="rotate(45)"

   @staticmethod
   def patternContents(num):
      b=Bend.patternContents(num)
      if not b:
         return None
      rv=[]
      rv.append(b[0])
      for i in range(1,len(b)):
         l=list(b[i])
         l[0]=-l[0]
         try:
            l[3]=-l[3]
         except IndexError:
            pass
         rv.append(tuple(l))
      return rv

   @staticmethod
   def patternSiblings(num):
      b=Bend.patternSiblings(num)
      rv=[]
      rv.append(b[0])
      for i in range(1,len(b)):
         rv.append((-b[i][0],b[i][1]))
      return rv

class BendletSinister(Bendlet,BendSinister):
   "Diminutive of Bend Sinister.  Actually this should probably be called a Scarpe"
   def __init__(self,*args,**kwargs):
      BendSinister.__init__(self,*args,**kwargs)

   def process(self):
      Bendlet.process(self)

   @staticmethod
   def patternWithOthers(num):
      res=Bendlet.patternWithOthers(num)
      for i in range(1,len(res)):       # Skip the scale...
         res[i]=(-res[i][0],res[i][1])
      return res

   @staticmethod
   def patternSiblings(num):
      return BendSinister.patternSiblings(num)

   def moveto(self,loc):
      Charge.moveto(self,loc)
   def shiftto(self,loc):
      Charge.shiftto(self,loc)
   def scale(self,x,y=None):
      Charge.scale(x,y)
   def resize(self,x,y=None):
      Charge.resize(self,x,y)

class Baton(BendletSinister):
   "Couped bendlet sinister."
   def __init__(self,*args,**kwargs):
      BendletSinister.__init__(self,*args,**kwargs)

   def process(self):
      self.clipPath=SVGdraw.rect(-5,-Ordinary.FESSPTY+10,
                                 10,Ordinary.HEIGHT-30)
      if hasattr(self,"transform"):
         self.clipPath.attributes["transform"]=self.transform
      self.clipPathElt.addElement(self.clipPath)

class Chief(Ordinary,TrueOrdinary):
   "Chiefs are a little different; they can push the rest of the field downward, and are not enclosed in bordures."
   # Chiefs will also have to be handled specially, as they ordinarily
   # do not overlay things on the field, but push them downward.  Including
   # bordures, right?
   def process(self):
      p=partLine()
      p.lineType=self.lineType
      # sys.stderr.write("Chief's linetype: (%s)\n"%self.lineType)
      # There are days when you want a quarterly chief.  So we'll
      # build the chief around the origin, like a charge, and then
      # move it.
      # Shift fancy-lined chiefs more, so as not to reveal the edge of the
      # shrunken field beneath.
      if p.lineType and p.lineType != "plain":
         p.rect(-Ordinary.WIDTH, -Ordinary.HEIGHT,
                Ordinary.WIDTH*3, Ordinary.HEIGHT+13.5)
         self.maingroup.attributes["transform"]="translate(0,%f)"%(-Ordinary.FESSPTY+13.5)
      else:
         p.rect(-Ordinary.WIDTH, -Ordinary.HEIGHT,
                Ordinary.WIDTH*3, Ordinary.HEIGHT+11)
         self.maingroup.attributes["transform"]="translate(0,%f)"%(-Ordinary.FESSPTY+11)
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

   @staticmethod
   def patternContents(num):
      # Also note that Chief is translated, so everything is around the origin.
      patterns=[[.25],[.25,(0,0)],
                [.25,(-20,0),(20,0)],
                [.25,(-30,0),(0,0),(30,0)],
                [.25,(-33,0),(-11,0),(11,0),(33,0)],
                [.2,(-34,0),(-17,0),(0,0),(17,0),(34,0)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

   # Chief doesn't need a patternSiblings.
   @staticmethod
   def patternSiblings(num):
      return None

class Bordure(Ordinary,TrueOrdinary):
   "Bordure ordinary.  Also an unusual one; might have to squish the field smaller.  Lines of partition tricky with bordure..."
   # Doing lines of partition is going to be hard with this one.
   def process(self):
      if self.lineType and self.lineType != "plain":
          pdata=partLine()
          pdata.lineType=self.lineType
          pdata.move(-Ordinary.FESSPTX,-Ordinary.FESSPTY)
          pdata.makeline(-Ordinary.FESSPTX,Ordinary.HEIGHT/3-Ordinary.FESSPTY,
                         align=1)
          pdata.makeline(Ordinary.WIDTH/6-Ordinary.FESSPTX,
                         3*Ordinary.HEIGHT/4-Ordinary.FESSPTY)
          pdata.makeline(0,Ordinary.HEIGHT-Ordinary.FESSPTY)
          pdata.makeline(-Ordinary.WIDTH/6+Ordinary.FESSPTX,
                         3*Ordinary.HEIGHT/4-Ordinary.FESSPTY,
                         align=1)
          pdata.makeline(Ordinary.FESSPTX,Ordinary.HEIGHT/3-Ordinary.FESSPTY)
          pdata.makeline(Ordinary.FESSPTX,-Ordinary.FESSPTY)
          pdata.makeline(-Ordinary.FESSPTX,-Ordinary.FESSPTY)
          pdata.closepath()
      else:
          # I don't like copying the field border the hard way like this.
          # Is there a more elegant way?
          pdata=SVGdraw.pathdata()
          pdata.move(-Ordinary.FESSPTX,-Ordinary.FESSPTY)
          pdata.vline(Ordinary.HEIGHT/3-Ordinary.FESSPTY)
          pdata.bezier(-Ordinary.FESSPTX,
                       Ordinary.HEIGHT*7/8-Ordinary.FESSPTY,
                       0,Ordinary.HEIGHT-Ordinary.FESSPTY,
                       0,Ordinary.HEIGHT-Ordinary.FESSPTY)
          pdata.bezier(0,Ordinary.HEIGHT-Ordinary.FESSPTY,
                       Ordinary.FESSPTX,
                       Ordinary.HEIGHT*7/8-Ordinary.FESSPTY,
                       Ordinary.FESSPTX,Ordinary.HEIGHT/3-Ordinary.FESSPTY)
          pdata.vline(-Ordinary.FESSPTY)
          pdata.closepath()
      self.clipPath=SVGdraw.path(pdata)
      self.clipPath.attributes["transform"]=" scale(.75)"
      self.clipPath.attributes["fill"]="black" # Doing masks now!!
      self.clipPathElt.addElement(SVGdraw.rect(-Ordinary.WIDTH,-Ordinary.HEIGHT,
                                               Ordinary.WIDTH*4,
                                               Ordinary.HEIGHT*4))
      self.clipPathElt.addElement(self.clipPath)
      # Ugh.  pattern{Contents,Siblings} is going to be tough on this one.

      # patternSiblings may not even be relevant.

   @staticmethod                        # Be handy to have this static
   def patternContents(num):            # for "an orle of marlets"
      patterns=[[.15],[.15,(0,-44)],
                [.15,(-43,0),(43,0)],
                [.15,(-43,-43),(43,-43),(0,52)],
                [.15,(0,-44),(-43,0),(43,0),(0,52)],
                [.15,(-43,-43),(43,-43),(-41,10),(41,10),(0,52)],
                [.15,(-43,-43),(43,-43),(-41,10),(41,10),(0,52),(0,-44)],
                [.15,(-43,-43),(43,-43),(-44,-5),(44,-5),(0,52),(-31,30),(31,30)],
                [.15,(-43,-43),(43,-43),(-44,-5),(44,-5),(0,52),(-31,30),(31,30),(0,-44)],
                [.15,(-43,-43),(43,-43),(-44,-5),(44,-5),(0,52),(-31,30),(31,30),(-15,-44),(15,-44)],
                [.15,(-43,-43),(43,-43),(-44,-15),(44,-15),(-41,10),(41,10),(-15,-44),(15,-44),(-25,37),(25,37)],
   [.15,(-43,-43),(43,-43),(-44,-15),(44,-15),(-41,10),(41,10),(-15,-44),(15,-44),(-25,37),(25,37),(0,52)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None


class Chevron(Ordinary,TrueOrdinary):
   "Chevron ordinary: up-pointing arrowhead sorta."
   def __init__(self,*args,**kwargs):
      Ordinary.__init__(self,*args,**kwargs)
      self.chevronwidth=25

   def drawme(self,width):
      # Chevrons are like fesses: when just "embattled" the bottom lines
      # remain plain.
      p=partLine()
      p.lineType=self.lineType
      p.move(-Ordinary.FESSPTX,20)
      p.makeline(0,-20,align=1,shift=-1)
      p.makeline(Ordinary.FESSPTX,20)
      p.relvline(width)
      if self.lineType=="embattled":
         p.line(0,width-20)
         p.line(-Ordinary.FESSPTX,20+width)
      else:
         p.makeline(0,width-20,align=1)
         p.makeline(-Ordinary.FESSPTX,20+width,shift=-1)
      p.closepath
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

   def process(self):
      self.drawme(self.chevronwidth)

   def patternContents(self,num):
      patterns=[[.25],[.25,(0,-5)],
                [.25,(-20,9),(20,9)],
                [.25,(-25,12),(25,12),(0,-5)],
                [.25,(-33,18.5),(33,18.5),(-14,4),(14,4)],
                [.25,(-33,18.5),(33,18.5),(-17,5.5),(17,5.5),(0,-5)]
                ]
      try:
         res=patterns[num]
         if hasattr(self,"inverted") and self.inverted:
            self.invertPattern(res)
      except IndexError:
         return None
      return res

   def patternWithOthers(self,num):
      patterns=[[1],[1,(0,0)],
                [.4,(0,-10),(0,10)],
                [.4,(0,-20),(0,0),(0,20)],
                [.4,(0,-30),(0,-10),(0,10),(0,30)],
                [.35,(0,-30),(0,-15),(0,0),(0,15),(0,30)]
                ]
      try:
         # Don't need to consider inversion here.
         res=patterns[num]
         if isinstance(self,Chevronel): # Chevronels don't need to rescale.
            res[0]=1
         return res
      except IndexError:
         return None

   def patternSiblings(self,num):
      patterns=[[.35],[.4,(0,32)],
                [.3,(-33,-20),(33,-20)],
                [.3,(-33,-20),(33,-20),(0,30)]
                ]
      try:
         res=patterns[num]
         if hasattr(self,"inverted") and self.inverted:
            self.invertPattern(res)
      except IndexError:
         return None
      return res

   def enhanced(self,*args):
      self.moveto((0, -22))

   def debased(self,*args):
      self.moveto((0, 22))

   def moveto(self,*args):
      if "transform" not in self.maingroup.attributes:
         self.maingroup.attributes["transform"]=""
      self.maingroup.attributes["transform"]+=" translate(%.4f,%.4f)" % args[0]

   def shiftto(self,*args):
      if "transform" not in self.clipPathElt.attributes:
         self.clipPathElt.attributes["transform"]=""
      self.clipPathElt.attributes["transform"]+=" translate(%.4f,%.4f)"%args[0]

   def scale(self,x,y=None):
      # Ignore the x coordinate, actually.
      if not y:
         y=x
      if not hasattr(self,"chevronwidth"):
         self.chevronwidth=25
      self.chevronwidth *= y

   def resize(self,x,y=None):
      # Does this need to be different from scale?
      self.scale(x,y)

   # Yaknow, Chevrons (and chevronels) can be cotised.  Just sayin.
   # And for that matter Palls and crosses and everyone else...

class Chevronel(Chevron):
   "Diminutive of Chevron"
   def __init__(self,*args,**kwargs):
      Chevron.__init__(self,*args,**kwargs)
      self.chevronwidth=10

class Pile(Charge,TrueOrdinary):
   "Pile: A big triangle pointing downward."
   def process(self):
      p=partLine()
      p.lineType=self.lineType
      p.move(-Ordinary.FESSPTX/2,-Ordinary.FESSPTY)
      # The top line is always plain.
      # Need to draw more outside the box in case it is inverted
      p.line(0,-Ordinary.HEIGHT*2)
      p.line(Ordinary.FESSPTX/2,-Ordinary.FESSPTY)
      p.makeline(Ordinary.BASEPT[0],Ordinary.BASEPT[1],align=1)
      p.makeline(-Ordinary.FESSPTX/2,-Ordinary.FESSPTY,align=0)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

   @staticmethod
   def patternWithOthers(num):
      if num<=1:
         return [1,(0,0)]
      res=[]
      res.append(2.0/num)
      for i in range(0,num):
         res.append((90.0/num*((num-1.0)/2-i),0))
      return res

   def patternSiblings(self,num):
      patterns=[[.4],[.4,(-27,10)],
                [.4,(-27,10),(27,10)],
                [.3,(-30,-15),(-30,15),(30,-15)], # ???
                [.3,(-30,-15),(-30,15),(30,-15),(30,15)]
                ]
      try:
         res=patterns[num]
      except IndexError:
         return None
      if hasattr(self,"inverted") and self.inverted:
         self.invertPattern(res)
      return res

   def patternContents(self,num):
      # Argh.  I think I want to be able to scale different elements
      # differently!
      patterns=[[.4],[.4,(0,-15)],
                [.4,(0,-25),(0,15,(.2,))],
                [.3,(0,-33,(.4,)),(0,-5),(0,15,(.2,))]
                ]
      try:
         res=patterns[num]
      except IndexError:
         return None
      if hasattr(self,"inverted") and self.inverted:
         self.invertPattern(res)
      return res

   def resize(self,x,y=None):
      # I don't really care about y anyway.
      if "transform" not in self.clipPathElt.attributes:
         self.clipPathElt.attributes["transform"]=""
      self.clipPathElt.attributes["transform"]+=" scale(%.4f,1)"%x

class Base(Ordinary,TrueOrdinary):
   "Base: fill in the bottom of the field."
   def process(self):
      p=partLine()
      p.lineType=self.lineType
      p.move(-Ordinary.WIDTH,25)
      p.makelinerel(Ordinary.WIDTH*3,0)
      p.vline(Ordinary.HEIGHT)
      p.hline(-Ordinary.WIDTH*3)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

   @staticmethod
   def patternContents(num):
      patterns=[[.35],[.35,(0,42)],
                [.25,(-15,38),(15,38)],
                [.2,(-15,36),(15,36),(0,45)],
                [.18,(-15,33),(15,33),(-7,46),(7,46)],
                [.18,(-15,33),(15,33),(-7,46),(7,46),(0,33)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

class Label(Ordinary,TrueOrdinary):
   "Label: a horizontal stripe with several (default 3) short vertical stripes hanging from it.  Used to differentiate an eldest son's arms, classically."
   def __init__(self,points=3,*args,**kwargs):
      self.points=points
      self.setup(*args,**kwargs)

   def process(self):
      p=SVGdraw.pathdata()              # Labels don't get lines of partition.
      p.move(Ordinary.FESSPTX,-25)
      p.relhline(-Ordinary.WIDTH)
      p.relvline(4)
      p.relhline(2)
      for i in range(0,self.points):
         p.relhline((Ordinary.WIDTH)/(self.points+1)-4)
         p.relvline(10)
         p.relhline(4)
         p.relvline(-10)
      p.hline(Ordinary.FESSPTX)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

class ChargeGroup(Ordinary):    # Kind of an invisible ordinary
   "A group of charges, for arranging purposes.  Acts a little like an invisible ordinary in that it imposes a pattern on the charges."
   def __init__(self,num=None,charge=None):
      self.charges=[]
      self.field=None
      self.tincture=None
      self.svg=SVGdraw.group()
      self.maingroup=SVGdraw.group()
      self.svg.addElement(self.maingroup)
      if num and charge:
         self.numcharges(num,charge)
      # run self.setup()?

   def setOverall(self):
      self.overall=True

   def isOverall(self):
      if hasattr(self,'overall'):
         return self.overall
      else:
         return False

   def fromarray(self,array):
      "Build a ChargeGroup from an array of charges (or chargegroups)"
      # OK, this may be wrong, but at the moment anyway, single charges
      # appear here as ChargeGroups.  And we need to have the charges
      # as the elements of this group.  Lessee...
      self.charges=[]
      for incoming in array:
         if isinstance(incoming, ChargeGroup):
            self.charges.extend(incoming.charges)
         else:
            self.charges.append(incoming)

   def numcharges(self,num,charge):
      "grp.numcharges(num,charge) -- fill the group with num copies of charge"
      for i in range(0,num):
         self.charges.append(copy.deepcopy(charge))

   def finalizeSVG(self):
      # Simplified finalizeSVG for ChargeGroup.
      self.process()
      for charge in self.charges:
         charge.parent=self.parent
         self.maingroup.addElement(charge.finalizeSVG())
      return self.svg

   def process(self):
      self.arrange()

   def fimbriate(self,*args,**kwargs):
      for elt in self.charges:
         elt.fimbriate(*args,**kwargs)

   # Defaults:
   defaultplacements=[[1],[1,(0,0)],    # 0 charges, 1 charge ...
                      [.5, (-22,0),(22,0)],            # 2
                      [.5, (-25,-25),(25,-25),(0,20)], # 3
                      # and so on
                      [.4, (-22,-22),(22,-22),(-22,22),(22,22)],
                      # 5 -> in saltire:
                      [.35, (-21,-21),(21,-21),(0,0),(-21,21),(21,21)],
                      # 6 -> in pile:
                      [.3, (-26,-26),(0,-26),(26,-26),(-13,0),(13,0),(0,26)],
                      # 7 -> three three and one
                      [.3, (-26,-26),(0,-26),(26,-26),
                       (-26,0),(0,0),(26,0),
                       (0,26)],
                      # 8 -> four and four
                      [.2, (-30,-10),(-10,-10),(10,-10),(30,-10),
                       (-30,10),(-10,10),(10,10),(30,10)],
                      # 9 -> three three and three
                      [.3, (-26,-26),(0,-26),(26,-26),
                       (-26,0),(0,0),(26,0),
                       (-26,26),(0,26),(26,26)],
                      # 10 -> in pile
                      [.3, (-36,-30),(-12,-30),(12,-30),(36,-30),
                       (-24,-10),(0,-10),(24,-10),
                       (-12,10),(12,10),
                       (0,30)]
                      ]

   defaultarrangements=[0, ByNumbers([1]), ByNumbers([2]),
                        ByNumbers([2,1]), ByNumbers([2,2]),
                        ByNumbers([2,1,2]), ByNumbers([3,2,1]),
                        ByNumbers([3,3,1]), # 7
                        ByNumbers([4, 4]),  # 8
                        ByNumbers([3, 3, 3]), # 9
                        ByNumbers([4,3,2,1]), # 10
                        ByNumbers([3,2,3,2,1]),   # 11
                        ByNumbers([4,3,4,1]),   # 12
                        ByNumbers([1,4,3,4,1]),   # 13
                        ByNumbers([2,3,4,3,2]),   # 14
                        ByNumbers([5,4,3,2,1]), # 15, in pile
                        ByNumbers([4,5,4,3]),   # 16
                        ByNumbers([3,4,3,4,3]),   # 17
                        ByNumbers([5,4,4,5]),   # 18
                        ByNumbers([5,5,4,3,2]), # 19
                        ByNumbers([6,5,4,3,2]), # 20
   ]

   def arrange(self):
      # This can only work for a relatively small number, say up to 3
      # TODO: check for "in pale/fesse/bend/cross/saltire"
      num=len(self.charges)
      # An even better way to do this: Put a method on the *tincture*
      # objects (or ordinary objects) that returns the appropriate
      # list of lists of positions.  Then things like "two bars" or
      # "three bends" can be subclasses and work the same way and
      # supply information for "between" them; "between" at this
      # point might as well be a synonym for "and".

      # OK, I figure we should check (first) with the charge: if it
      # has a preferred organization, use that (check with the first
      # charge; worry about if they're different another time).
      # (second) check with the parent (bends like things in bend,
      # crosses in cross, etc).  (third) the parent, if it has no
      # preference itself, should check with its other charges
      # (ordinaries), and failing that, should check with its
      # tincture and report that.

      # The organization should be by background first, then number, I think.
      # First, how to shift things.  I *think* we only need shiftto if
      # we're being countercharged.
      # I think we'll only be using resize and not scale here.
      if isinstance(self.charges[0].tincture,Countercharged):
         def move(obj,location):
            obj.shiftto(location)
      else:
         def move(obj,location):
            obj.moveto(location)
      # Wish there were a better way to work this out than trial and error
      placements=None
      # Explicit arrangement takes precedence
      try:
         placements=self.arrangement.pattern(len(self.charges))
      except AttributeError:
         pass
      if not self.isOverall():
         if not placements:
            try:
               placements=self.charges[0].patternWithOthers(len(self.charges))
            except AttributeError:
               pass
         if not placements:
            try:
               placements=self.parent.patternContents(len(self.charges))
            except AttributeError:
               pass
      if not placements:
         try:
            # placements=ChargeGroup.defaultplacements[num]
            placements=self.defaultarrangements[num].pattern(num)
         except IndexError:
            pass
      if not placements:
         raise ArrangementError("Too many objects")
      # Let's see.  If there's ANOTHER chargegroup here, we need to, um...
      # I guess... scale down?
      # This is crude.
      # THIS DOES NOT WORK RIGHT.
      # It breaks behavior that worked before in cases like
      # {Or a bend sable between two roundels gules}
      # The roundels get double-shrunk.
      # if len(self.parent.charges) > 1:
      #   extrascale=0.4
      # else:
      #   extrascale=1.0
      extrascale=1.0
      scale=placements[0]
      if type(scale) is not type(()):
         scale=(scale,scale)
      scale=tuple(map((lambda x: x*extrascale), scale))
      for i in range(1,num+1):
         move(self.charges[i-1], (placements[i][0],placements[i][1]))
         if len(placements[i])>2 and len(placements[i][2]):
            self.charges[i-1].resize(*placements[i][2])
         else:
            self.charges[i-1].resize(*scale)
         if len(placements[i])>3:
            # Allow rotating too...
            self.charges[i-1].orient(placements[i][3])

   def patternSiblings(self,num):
      # Just use the first charge.
      return self.charges[0].patternSiblings(num)

   def orient(self,direction,*args,**kwargs):
      for c in self.charges:
         c.orient(direction,*args,**kwargs)

class Orle(ChargeGroup,TrueOrdinary):
   "diminutive of bordure, detached from the edge of the shield"
   # We will define an Orle as a bordure detached from the edge of the shield
   # (and narrower).  A Tressure is either a synonym for Orle, or else one that
   # is narrower, and may be doubled.  We'll work on it...

   # Copying the field border again...
   # OK... right, an orle has to be something *on top of* a bordure,
   # which happens to be the same color as the field.

   def __init__(self):
      self.charges=[]
      self.svg=SVGdraw.group()
      # First, add a bordure in the color of the field.  Somehow.
      self.bord=Bordure()               # How to set its color??
      self.maingroup=SVGdraw.group()
      self.svg.addElement(self.maingroup)
      self.charges.append(self.bord)

   def makebord(self,outer,inner):
      # Escutcheon path.  Tired of copying it the long way.
      pdat="M -50 -50 V-14 C-50,46 0,60 0,60 C0,60 50,46 50,-14 V-50 z"
      orl=Ordinary()
      if inner<.75:
         inner=.75
      orl.clipPath=SVGdraw.SVGelement('path',attributes={'d':pdat,
                                                         'transform':'scale(%.2f)'%outer})
      orl.tincture=self.tincture
      self.bord.tincture=self.parent.tincture
      self.charges.append(orl)
      orl.clipPathElt.addElement(orl.clipPath)
      orl.clipPathElt.addElement(
         SVGdraw.SVGelement('path',attributes={'d':pdat,
                                               'transform':'scale(%.2f)'%inner,
                                               'fill':'black'}))
   def process(self):
      self.makebord(.85,.75)

   def arrange(self):
      pass

class DoubleTressure(Orle):
   "Another diminutive bordure, this one thinner and doubled"
   # Do we need to bother with a single tressure?  Can we just take it as a
   # synonym for Orle?
   def process(self):
      Orle.makebord(self,.9,.75)
      # Everything up to here like in Orle, except maybe a little thicker.
      # Just add a fat unmasking stroke.
      pdat="M -50 -50 V-14 C-50,46 0,60 0,60 C0,60 50,46 50,-14 V-50 z"
      self.charges[-1].clipPathElt.addElement(
         SVGdraw.SVGelement('path',attributes={'d':pdat,
                                               'transform':'scale(0.83)',
                                               'fill':'none',
                                               'stroke':'black',
                                               'stroke-width':'3'}))

class Tressure(Orle):
   "Even thinner diminutive bordure"
   def process(self):
      Orle.makebord(self,.85,.8)


class Roundel(Charge):
   "Round circular charge"
   def process(self):
      self.clipPath=SVGdraw.circle(cx=0,cy=0,r=36) # make it 36
      self.clipPathElt.addElement(self.clipPath)

# Maybe this'll be handy for making "grouped" charges, behind the scenes.
class BigRect(Charge):
   "Huge charge, as big as the shield.  For use making 'grouped' charges."
   def process(self):
      self.clipPath=SVGdraw.rect(x=-Ordinary.FESSPTX,
                                 y=-Ordinary.FESSPTY,
                                 width=Ordinary.WIDTH,
                                 height=Ordinary.HEIGHT)
      self.clipPathElt.addElement(self.clipPath)

class Lozenge(Charge):
   "Diamond-shaped charge."
   def process(self):
      p=SVGdraw.pathdata()
      p.move(0,-42)
      p.line(28,0)
      p.line(0,42)
      p.line(-28,0)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

# Should I even keep defining these simple ones as classes, or just
# use ExtCharge for them?

class Fusil(Charge):
   "Longer and narrower diamond than a lozenge."
   def process(self):
      p=SVGdraw.pathdata()
      p.move(0,-42)
      p.line(22,0)
      p.line(0,42)
      p.line(-22,0)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

class Mascle(Charge):
   "Like a voided lozenge."
   def process(self):
      self.fimbriation_width=2
      self.clipPath=SVGdraw.group()
      self.clipPath.attributes["id"]="ClipPath%04d"%Ordinary.id
      Ordinary.id += 1
      p1=SVGdraw.pathdata()
      p1.move(0,-42)
      p1.line(28,0)
      p1.line(0,42)
      p1.line(-28,0)
      p1.closepath()
      path=SVGdraw.path(p1)
      path.attributes["id"]="Masc%04d"%Ordinary.id
      Ordinary.id+=1
      self.clipPath.addElement(path)
      use=SVGdraw.use("#%s"%path.attributes["id"],fill="black")
      use.attributes["transform"]=" scale(.6)"
      self.clipPath.addElement(use)
      self.clipPathElt.addElement(self.clipPath)

class Canton(Ordinary,TrueOrdinary):
   "A square in dexter chief.  Not a normal charge; it doesn't move around."
   # This one can't be an ExtCharge, because it has a special placement.
   def process(self):
      # Make the rectangle around the fess point, let the usual Ordinary
      # patternContents do its thing, then just diddle its
      # positioning.
      # Do not touch the scaling, lest furs and stuff get unduly resized.
      wid=Ordinary.WIDTH
      hit=Ordinary.WIDTH
      self.clipPath=SVGdraw.rect(-wid/2.0, -hit/2.0, wid, hit)
      self.clipPathElt.addElement(self.clipPath)
      # Is the fimbriation right, though?  And does anyone fimbriate cantons?
      # We can always move the upper left corner a little offscreen.
      if "transform" not in self.maingroup.attributes:
         self.maingroup.attributes["transform"]=""
      scale=0.4
      self.maingroup.attributes["transform"]+=" translate(%f,%f) "%(-Ordinary.FESSPTX+wid*scale/2.0, -Ordinary.FESSPTY+hit*scale/2.0)
      if "transform" not in self.clipPathElt.attributes:
         self.clipPathElt.attributes["transform"]=""
      self.clipPathElt.attributes["transform"]+=" scale(%f)"%scale

class Gyron(Ordinary,TrueOrdinary):
   "Like a canton; a right triangle in dexter chief."
   # Should we consider the possibility of more than one?  Or of a canton?
   def process(self):
      p=SVGdraw.pathdata()
      p.move(-Ordinary.FESSPTX, -Ordinary.FESSPTY)
      p.relline(Ordinary.WIDTH/3, Ordinary.HEIGHT/3)
      p.relhline(-Ordinary.WIDTH/3)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

class Fret(Ordinary,TrueOrdinary):
   "A saltire plus a (big) mascle."
   # This also should appear only once; it's an ordinary really.
   def process(self):
      # Not *really* a mascle and crossed bendlets.  A tilted square
      # looks better.
      # Try to draw the thin lines?  Bleah, probably possible but a pain
      # to compute.
      # Doesn't fimbriate at all well drawn this way. :(
      g=SVGdraw.group()
      g.attributes["id"]="ClipPath%04d"%Ordinary.id
      Ordinary.id+=1
      rect=SVGdraw.rect(-25,-25,50,50)
      rect.attributes["id"]="Fret%04d"%Ordinary.id
      Ordinary.id+=1
      g.addElement(rect)
      use=SVGdraw.use("#%s"%rect.attributes["id"],fill="black")
      use.attributes["transform"]=" scale(.7)"
      g.addElement(use)
      b1=SVGdraw.rect(-5,-Ordinary.HEIGHT,10,Ordinary.HEIGHT*3)
      g.addElement(b1)
      b2=SVGdraw.rect(-Ordinary.WIDTH,-5,Ordinary.WIDTH*3,10)
      g.addElement(b2)
      g.attributes["transform"]=" rotate(45)"
      self.clipPath=g
      self.clipPathElt.addElement(self.clipPath)

   def patternSiblings(self,num):
      if num==4:
         return [.2,(0,-42),(42,0),(-42,0),(0,45)] # *shrug*
      else:
         return None

class Flaunches(TrueOrdinary,Charge):
   "Curved 'bites' from the sides.  Always come in pairs."
   # Always come in pairs.  *Shrug* WTH, we'll just have each object draw a
   # single flaunch, and patternWithOthers will arrange them.

   def process(self):
      # I don't think flaunches can take lines of partition.
      # Are they too big, you think?
      p=SVGdraw.pathdata()
      p.move(-6,-Ordinary.FESSPTY)
      p.ellarc(Ordinary.WIDTH/4,Ordinary.HEIGHT/2,0,1,1,
               -6,Ordinary.FESSPTY)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

   @staticmethod
   def patternWithOthers(num):
      # num had better be two.
      # This winds up reflecting any charges on the sinister flaunch too,
      # but yaknow, I think that's the Right Thing.
      return [1,(-Ordinary.FESSPTX,0),(Ordinary.FESSPTY,0,(-1,1))]

   @staticmethod
   def patternContents(num):
      W=Ordinary.WIDTH/5
      patterns=[[1],[.3,(W,-5)],
                [.3, (W,15),(W-2,-20)],
                [.25,(W,15),(W,-5),(W-2,-25)],
                [.23,(W-2,20),(W,0),(W,-20),(W-5,-40)],
                ]
      return patterns[num]

   @staticmethod
   def patternSiblings(num):
      # They go on a line down the center, only.
      return Pale.patternContents(num)

class Triangle(Charge):
   "Triangular charge"
   def process(self):
      p=SVGdraw.pathdata()
      p.move(0,-40)
      p.line(34.6,20)
      p.line(-34.6,20)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

class Billet(Charge):
   "rectangle"
   def process(self):
      self.clipPath=SVGdraw.rect(-22,-35,44,70)
      self.clipPathElt.addElement(self.clipPath)

class Square(Charge):
   "Square"
   def process(self):
      self.clipPath=SVGdraw.rect(-30,-30,60,60)
      self.clipPathElt.addElement(self.clipPath)

class Annulet(Charge):
   "empty ring"
   def process(self):
      # self.clipPath is used for fimbriation, which at 4 is
      # so wide it overwhelms the annulet.  Woops.
      self.fimbriation_width=2
      self.clipPath=SVGdraw.group()
      self.clipPath.attributes["id"]="ClipPath%04d"%Ordinary.id
      Ordinary.id+=1
      self.clipPath.addElement(SVGdraw.circle(cx=0,cy=0,r=36))
      # Using masks, so all we need to do is draw a black circle inside.
      self.clipPath.addElement(SVGdraw.circle(cx=0,cy=0,r=24,fill="black"))
      self.clipPathElt.addElement(self.clipPath)

"""
These are arj's thoughts on how ExtCharge/Symbol should be merged and changed:

Full parsing of the external XML file, using DOM or something
similar. Now we have a tree that we can traverse. We do a depth-first
search through the tree to find an element that contains data that we
think could be the shape that we want to extract. We extract this
data, and output it (when called from finalizeSVG) as a mask.
"""

class ExtCharge(Charge):
    # * Path, fimbriation-width, and default tincture (for "proper")
    # * Each ext charge should specify patternSiblings/patternContents.
    #   Perhaps through external metadata?
    "External charge: defined by some path in an SVG elsewhere."
    paths={
        "fleur":("data/Fleur.svg#fleur",4,None),
        "formy":("data/Charges.svg#formy",30,None),
        "pommee":("data/Charges.svg#pommee",300,None),
        "bottony":("data/Charges.svg#bottony",20,None),
        "goute":("data/Charges.svg#goute",1,None),
        "humetty":("data/Charges.svg#humetty",3,None),
        "flory":("data/Charges.svg#flory",100,None),
        "crosscrosslet":("data/Cross-Crosslet-Heraldry.svg#cross-crosslet",2,None),
        "mullet":("data/Charges.svg#mullet",2,None),
        "crescent":("data/Charges.svg#crescent",2,None),
        "escutcheon":("data/Charges.svg#escutcheon",3,None),
        "shakefork":("data/Charges.svg#shakefork",3,None),
        "escallop":("data/Escallop.svg#escallop",2,None),
        "firtwig":("data/Firtwig.svg#firtwig",2,None),
        "question":("data/Charges.svg#question",2,None)
        }

    def __init__(self,name,*args,**kwargs):
       self.setup(*args)
       try:
          info=ExtCharge.paths[name]
          (self.path,self.fimbriation_width,self.tincture)=info
          if kwargs.get("extension"): # Not sure this is so great.
             self.path+=str(kwargs["extension"][0])
       except KeyError:
          self.path=name              # Punt.
       if kwargs.get("transform"):
          self.transform=kwargs.get("transform")
       if kwargs.get("fimbriation_width"):
          self.fimbriation_width=kwargs.get("fimbriation_width")
       # On one hand, this is a hack.  On the other hand, there is
       # something to be said for it.  It is potentially awfully
       # generic.
       if kwargs.get("postprocessing"):
          kwargs['postprocessing'](self)


    def process(self):
       u=SVGdraw.use(self.path)
       if self.getBaseURL():
          u.attributes["xml:base"]=self.getBaseURL()
       if hasattr(self,"transform") and self.transform:
          if "transform" not in u.attributes:
             u.attributes["transform"]=""
          u.attributes["transform"]+=" "+self.transform
       if hasattr(self,"inverted") and self.inverted:
          if "transform" not in u.attributes:
             u.attributes["transform"]=""
          u.attributes["transform"]=" rotate(180)"+ u.attributes["transform"]
       self.use=u
       self.clipPathElt.addElement(u)

    def do_fimbriation(self):
       attributes={"xlink:href":"%s"%self.path,
                   "stroke":self.fimbriation,
                   "stroke-width":self.fimbriation_width,
                   "fill":"none",
                   "transform":self.clipPathElt.attributes.get("transform")
                   }
       if not attributes["transform"]:
          attributes["transform"]=""
       try:
          attributes["transform"]+=self.use.attributes["transform"]
       except AttributeError:
          pass
       except KeyError:
          pass
       try:
          attributes["transform"]=self.endtransforms+attributes["transform"]
       except AttributeError:
          pass
       if self.getBaseURL():
         attributes["xml:base"]=self.getBaseURL()
       self.maingroup.addElement(
          SVGdraw.SVGelement('use',attributes=attributes))


# Another external charge class, this one for things not used as clipping
# paths?

class Symbol(Charge):
   "External charge: defined by a <symbol> in an SVG elsewhere."
   paths={
      "lionpassant" : ("data/LionPassant.svg#lion",Treatment("or")),
      "lionrampant" : ("data/LionRampant.svg#lion",Treatment("or"))
      }

   def __init__(self,name,*args,**kwargs):
      self.setup(*args)
      try:
         (self.path,self.color)=Symbol.paths[name]
      except KeyError:
         self.path=name                 # Punt.
         self.color=Treatment("argent")

   def process(self):
      # baseRect is worth keeping around, for furs.  Otherwise the fur
      # gets scaled with the drawing, which can be extreme.
      # (still can't get it countercharged though)
      self.baseRect=SVGdraw.rect(-Ordinary.FESSPTX,
                                 -Ordinary.FESSPTY,
                                 Ordinary.WIDTH,
                                 Ordinary.HEIGHT)
      self.baseRect.charge=self

   def fimbriate(self,treatment):
      self.fimbriation=Treatment(treatment)

   # This so totally doesn't work.
   # This isn't much of an improvement.
   def do_fimbriation(self):
      self.fimb=SVGdraw.group()
      mask=SVGdraw.SVGelement('mask',
                              attributes={"id" : "Mask%04d"%Ordinary.id})
      Ordinary.id+=1
      for i in range(0,4):
         el=SVGdraw.use(self.path)
         if self.getBaseURL():
            el.attributes["xml:base"]=self.getBaseURL()
         el.attributes["transform"]="translate(%d,%d)"%([-2,2,0,0][i],
                                                        [0,0,-2,2][i])
         mask.addElement(el)
      Ordinary.defs.append(mask)
      self.fimb=SVGdraw.rect(-Ordinary.FESSPTX,
                             -Ordinary.FESSPTY,
                             Ordinary.WIDTH,
                             Ordinary.HEIGHT)
      self.fimb.attributes["mask"]="url(#%s)"%mask.attributes["id"]
      self.fimb=self.fimbriation.fill(self.fimb)

   def finalizeSVG(self):
      self.process()
      self.use=SVGdraw.use(self.path)
      if self.getBaseURL():
         self.use.attributes["xml:base"]=self.getBaseURL()
      self.clipPath=self.use
      self.clipPathElt.addElement(self.clipPath)
      self.maingroup.addElement(self.baseRect)
      self.maingroup.addElement(self.use)
      self.mask.attributes["id"]="Clip%04d"%Ordinary.id
      Ordinary.id+=1
      if hasattr(self,"clipPath"):
         # For fimbriation (at least one way to do it), need an id on the actual
         # path, not just the group:
         self.clipPath.attributes["id"]="ClipPath%04d"%Ordinary.id
         Ordinary.id+=1
         if hasattr(self,"clipTransforms"):
            if "transform" not in self.clipPath.attributes:
               self.clipPath.attributes["transform"]=""
            self.clipPath.attributes["transform"] += self.clipTransforms
      if hasattr(self,"fimbriation"):
           self.do_fimbriation()
      #self.maingroup=self.tincture.fill(self.maingroup)
      self.maingroup.attributes["fill"]="none"
      self.baseRect=self.tincture.fill(self.baseRect)
      self.maingroup.attributes["mask"]="url(#%s)"%self.mask.attributes["id"]
      # Last-minute transforms
      if hasattr(self,"endtransforms"):
         if "transform" not in self.use.attributes:
            self.use.attributes["transform"]=""
         self.use.attributes["transform"]+=self.endtransforms
      #newgroup=SVGdraw.group()
      #mask=SVGdraw.SVGelement('mask',attributes=
      #                         {"id" : "Mask%04d"%Ordinary.id})
      #Ordinary.id+=1
      #g=SVGdraw.group()
      #g.attributes["fill"]="white"
      #g.attributes["mask"]=mask.attributes["id"]
      #g.addElement(SVGdraw.use(self.path))
      #g.addElement(self.maingroup)
      #newgroup.addElement(mask)
      #newgroup.addElement(g)
      #self.maingroup=newgroup
      #if hasattr(self,"charges"):
      #   for charge in self.charges:
      #      self.maingroup.addElement(charge.finalizeSVG())
      #if hasattr(self,"newmaingroup"):
      #   self.maingroup=self.newmaingroup
      if hasattr(self,"fimbriation"):
         newmain=SVGdraw.group()
         newmain.addElement(self.fimb)
         newmain.addElement(self.maingroup)
         self.maingroup=newmain
      self.svg.addElement(self.maingroup)
      # Add another iteration of the use element, to fill in what was lost
      # in masking.
      last=copy.deepcopy(self.use)
      last.attributes["fill"]="none"
      try:
         last.attributes["transform"]=self.maingroup.attributes["transform"]
      except KeyError:
         pass
      # Gotta put in the last-minute transforms again; they got overwritten.
      if hasattr(self,"endtransforms"):
         if "transform" not in last.attributes:
            last.attributes["transform"]=""
         last.attributes["transform"]+=self.endtransforms
      self.svg.addElement(last)
      return self.svg


   def resize(self,x,y=None):
      if not y:
         y=x
      if "transform" not in self.maingroup.attributes:
         self.maingroup.attributes['transform']=""
      self.maingroup.attributes['transform']+=" scale(%.3f,%.3f)"%(x,y)

   # This helps, but screws up differently:
#   def moveto(self,*args):
#      self.shiftto(*args)

# Check the 2lions.svg file!!  Both the mask AND the later <use> have to be
# translated.

class Text(Charge):
   "Text (perhaps a single emoji) rendered as a charge."

   uure=re.compile(r'\\N\{[A-Z0-9_ -]*\}|\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}')

   def __init__(self, text, width, height, *args, **kwargs):
      self.setup(*args)
      self.text=text
      self.font=None
      (pre, delim, post)=self.text.rpartition('@')
      if pre:
         self.text=pre
         self.font=post
      # Want to allow both direct utf-8 and escaped
      #self.text=uure.sub(lambda m: bytes(m.group(0),'utf-8').decode('unicode-escape'), self.text)
      # Is this simpler and good enough?  Also not py3-dependent.
      # python2 had a string-escape encoding but python3 doesn't.
      # This is reasonably safe as it will error out if you try code-injection.
      self.text=ast.literal_eval('"""'+self.text+'"""')
      # Wow, even fimbriation works!  But usually needs it a bit narrower.
      self.fimbriation_width=2
      # self.width, self.height = width, height
      # Ignore height, compute from width?
      self.width=width
      self.height=width/len(self.text)
      if "transform" in kwargs:
         self.transform=kwargs["transform"]

   def process(self):
      # Placement by trial and error, needs fine-tuning
      # Can't get alignment-baseline="central" or "middle" to do anything,
      # baseline-shift="50%" doesn't work, dominant-baseline also doesn't help...
      # it isn't even really clear just how to shift in general.  Maybe we can
      # think of something.
      self.clipPath=SVGdraw.text(x= 0,
                                 y= 0,
                                 text=self.text,
                                 font_size=self.height, # ??
                                 dy=self.height/4.0,
                                 text_anchor="middle")
      # Can't do this in the constructor; won't translate _ to -.
      # self.ref.attributes["alignment-baseline"]="central"
      self.clipPathElt.addElement(self.clipPath)
      if hasattr(self,"transform"):
         if "transform" not in self.ref.attributes:
            self.clipPath.attributes["transform"]=""
         self.clipPath.attributes["transform"]+=self.transform
      if self.font:
         if self.font.startswith("style="):
            self.clipPath.attributes['style']=self.font.partition('=')[2]
         else:
            self.clipPathElt.attributes['font-family']=self.font

# A class for raster (non-vector) images.  Eww.
class Image(Charge):
   "External link to a non-vector image"

   def __init__(self, url, width, height, *args, **kwargs):
      self.setup(*args)
      self.url=url
      (self.width,self.height)=(width, height)
      if "transform" in kwargs:
         self.transform=kwargs["transform"]

   def process(self):
      self.ref=SVGdraw.image(self.url, x= -self.width/2.0,
                             y= -self.height/2.0,
                             width=self.width,
                             height=self.height)
      if self.getBaseURL():
         self.ref.attributes["xml:base"]=self.getBaseURL()
      if hasattr(self,"transform"):
         if "transform" not in self.ref.attributes:
            self.ref.attributes["transform"]=""
         self.ref.attributes["transform"]+=self.transform

   def invert(self):
      if not hasattr(self,"endtransforms"):
         self.endtransforms=""
      self.endtransforms += " rotate(180)"

   def shiftto(self, *args):
      self.moveto(*args)

   def resize(self, *args):
      self.scale(*args)

   def do_fimbriation(self):
      # Shyeah right.
      pass

   def finalizeSVG(self):
      # Need a special version for Image, overriding the default.
      self.process()
      # Last-minute transforms:
      if hasattr(self,"endtransforms"):
         # The transform goes on the ref, right?
         if "transform" not in self.ref.attributes:
            self.ref.attributes["transform"]=""
         self.ref.attributes["transform"]+=self.endtransforms
      # Images don't have clipPaths, so we won't output one
      # and we mustn't refer to one either:
      try:
         del(self.maingroup.attributes["mask"])
      except KeyError:
         pass
      if hasattr(self,'tincture') and self.tincture and not \
             (hasattr(self.tincture,'color') and self.tincture.color=="none"):
         # There's a color!  Have to do some brilliant filter stuff.
         # Let's get this straight: we make baserect which is filled with
         # the color/fur/whatever.  We mask it with the image's alpha,
         # which we get from a filter.  Then we put the image on top
         # of that, masking it with a filter that multiplies it by what's
         # underneath, and Bob's yer uncle!
         # Those two filters do not depend on anything, they only need
         # to be defined once.
         if not Ordinary.ImageFilters:
            filter1=SVGdraw.SVGelement("filter",
                                       attributes={'id' : 'AlphaFilter'})
            filter1.addElement(
               SVGdraw.SVGelement('feFlood',
                                  attributes={'flood-color': 'white',
                                              'result' : 'flood'}))
            filter1.addElement(
               SVGdraw.SVGelement('feComposite',
                                  attributes={'in':'flood',
                                              'in2':'SourceGraphic',
                                              'operator':'in'}))
            Ordinary.defs.append(filter1)
            filter2=SVGdraw.SVGelement("filter",
                                       attributes={'id': 'BlendFilter'})
            filter2.addElement(
               SVGdraw.SVGelement('feBlend',
                                  attributes={'in':'BackgroundImage',
                                              'in2':'SourceGraphic',
                                              'mode':'multiply'}))
            Ordinary.defs.append(filter2)
            Ordinary.ImageFilters=True  # Don't do this again.
         self.mask=SVGdraw.SVGelement('mask',
                                      attributes={'id': 'Mask%04d'%Ordinary.id})
         Ordinary.id+=1
         img=copy.deepcopy(self.ref)
         img.attributes['filter']='url(#AlphaFilter)'
         self.mask.addElement(img)
         Ordinary.defs.append(self.mask)
         self.baseRect=SVGdraw.rect(x=-Ordinary.FESSPTX,
                                    y=-Ordinary.FESSPTY,
                                    width=Ordinary.WIDTH,
                                    height=Ordinary.HEIGHT)
         self.baseRect.charge=self
         self.baseRect=self.tincture.fill(self.baseRect)
         self.baseRect.attributes['mask']='url(#%s)'%self.mask.attributes['id']
         self.ref.attributes['filter']='url(#BlendFilter)'
         self.maingroup.addElement(self.baseRect)
      self.maingroup.addElement(self.ref)
      return self.maingroup


# Other ideas...:

# Presumably each charge (esp. each Ordinary) will be its own <g> element,
# thus allowing a remapping of coordinates.  Obv. we don't want complete
# rescaling, but it's a step.

# I like the idea of a function parent-charges can call on their
# descendents, "suggesting" a transformation to apply, which the charges
# may or may not choose to listen to, or by how much.  By transforming
# their paths only, we can avoid transforming furs used to fill them in.

# A "between" function, which returns a list of points in the
# *surroundings* of this Ordinary suitable for putting n other charges.
# e.g. "a bend between two annulets sable" vs. three annulets vs. a chevron
# between three, etc etc etc.  This is something that relates to a charge's
# *siblings* on the field.

import plyyacc

class Blazon:
   """A blazon is a heraldic definition. We would like to be as liberal
   as possible in what we accept."""
   def __init__(self, blazon, base=None, outline=True):
      # Our parser is somewhat finicky, so we want to convert the raw,
      # user-provided text into something it can handle.
      self.base=base
      self.blazon=self.Normalize(blazon)
      self.outline=outline

   @staticmethod
   def Normalize(blazon):
      # Can't just toss all the non-alphanumeric chars, if we're going
      # to accept URLs...  Or text...
      # return re.sub("[^a-z0-9 ']+"," ",blazon.lower())
      seps=re.compile(r'([<>"])') # Group means keep delims!
      bits=seps.split(blazon)
      # Splitting on the <>s means that every odd-indexed element in the
      # list is one that belongs in <>s and thus literal
      # And no, it doesn't matter that maybe the string starts with a <.
      # Such a thing would be an invalid blazon anyway.
      # Should still be valid when splitting on <"> and keeping delims, except
      # multiplied by 2...
      # LIMITATION: can't have TEXT with < or > in it.  Yet.  (URLs with quotes
      # we can manage with escapes)
      i=0
      newbits=[]
      try:
         for i in range(0,len(bits)):
            if i%4 == 0:
               newbits.append(re.sub("[^a-z0-9() ⚜'-]+"," ",bits[i].lower()))
            elif i%4 == 2:
               newbits.append(bits[i-1]+bits[i]+bits[i+1])
      except IndexError:
         # Generally due to an odd number of delimiters, which shouldn't happen
         return ""              # ?
      return ' '.join(newbits)

   def GetBlazon(self):
      return self.blazon

   def getlookuptable(self):
      self.__class__.lookup={}
      try:
         fh=open('data/Chargelist','r')
         for line in fh:
            if line[0]!='#':            # Skip comments.
               (key, value)=line.split(':',1)
               # Compile 'em into regexps in advance.
               self.__class__.lookup[re.compile(key.strip())]=value.strip()
      except IOError:
         pass

   @classmethod
   def lookupcharge(cls,name):
      # No sense in doing a direct lookup; they're all compiled into REs.
      # Probably for the best to require that we find the *longest* match.
      found=None
      foundlen=0
      for (key,value) in cls.lookup.items():
         mtch=key.match(name)
         if mtch:
            # we're searching with "match"; the start is always the same place
            if foundlen<mtch.end():
               foundlen=mtch.end()
               found=value
      if found:
         return found
      raise KeyError

   @staticmethod
   def outside_element(data):
      """Handle URLs, either directly from blazon or from Chargelist file.
      The data may contain spaces, in which case it is *split* along those
      spaces in order to allow extra information, like SVG data.

      Apparently, system paths also work, though this is probably due
      to the way SVG handles embedded images and should not be abused"""
      # OK, here's how the data should be handled:
      # 1. If it has no internal whitespace, it's a (raster) image URL.
      #    So all the <http://foo.com/image.png> charges work, etc.  In theory
      #    an SVG image SHOULD work, but scaling of external SVGs doesn't work
      #    right, owing to silliness in SVG, see
      #    http://www.w3.org/Bugs/Public/show_bug.cgi?id=5560
      # 2. If there's whitespace, split at the whitespace so we can put in
      #    some other info.  Let's see what that split should be like...
      #
      # Maybe make it context-sensitive, at least for now.  So if the first
      # token after the spaces is "SVGpath", then expect the second token
      # in quotes, containing the transform for the path, and the third one
      # to be the fimbriation-width (defaulting to something).  Other data-types
      # will have to handle themselves as they get invented.
      pieces=re.split(r"\s+",data)
      if len(pieces) < 1:
         # Bweah!!  Shouldn't happen!  I dunno, complain.
         raise ArrangementError("Empty charge data!!")
      if len(pieces) == 1:
         # Image url
         return Image(pieces[0], 80, 80)
      if pieces[1] == "SVGpath":
         # SVG path ('ExtCharge') behavior.
         m=re.match(r'\S+\s+SVGpath\s+"([^"]*)"\s*([0-9.]+)?',data)
         if not m:
            # Match failed.  Error-handling is for wimps.
            raise ArrangementError("Invalid charge data")
         f=m.group(2)
         if f == None:
            f="3.0"
         return ExtCharge(pieces[0], transform=" "+m.group(1),
                          fimbriation_width=float(f))
      elif pieces[1] == "IMAGE":
         # long-form image.
         m=re.match(r'\S+\s+IMAGE\s+((\w+\s*=\s*"[^"]*"\s*)*)', data)
         if not m:
            raise ArrangementError("Invalid charge data")
         atts=re.findall(r'\s*(\w*)\s*=\s*"([^"]*)"',m.group(1))
         kw={}
         kw["width"]=80
         kw["height"]=80
         for t in atts:
            kw[t[0]]=t[1]
         kw["width"]=float(kw["width"]) # Transform back into numbers.
         kw["height"]=float(kw["height"])
         return Image(pieces[0], **kw)
      # Otherwise... hell if I know.
      return Image(data,80,80)


   def GetShield(self):
      if not hasattr(self.__class__,'lookup') or not self.__class__.lookup:
         self.getlookuptable()
      shield=plyyacc.yacc.parse(self.GetBlazon())
      if self.base:
         shield.setBase(self.base)
      shield.setOutline(self.outline)
      shield.setBlazon(self.GetBlazon())
      return shield

if __name__=="__main__":
   if len(sys.argv) < 1: # Read from stdin
      cmdlineinput = re.sub(r"\s+"," ",
                            sys.stdin.read())
   else: # The standard way of operation
      cmdlineinput = " ".join(sys.argv[1:])
   blazon = Blazon(cmdlineinput)
   # Old YAPPS parser:
   # return parse.parse('blazon', self.GetBlazon())
   # New YACC parser:
   print(plyyacc.yacc.parse(blazon))
