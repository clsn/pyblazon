#!/usr/bin/python
# -*- coding: latin-1 -*-
import SVGdraw
import math
import sys
import copy
import re

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

   def __init__(self,*args,**kwargs):
      self.setup(*args,**kwargs)

   def setup(self,tincture="none",linetype="plain"):
      self.done=False
      if type(tincture)==str:
         self.tincture=Treatment(tincture)
      else:
         self.tincture=tincture
      self.lineType=linetype
      self.charges=[]
      self.fimbriation_width=4          # default
      if not hasattr(self,"svg"):
         self.svg=SVGdraw.svg(x=-Ordinary.FESSPTX,
                              y=-Ordinary.FESSPTY,
                              width=Ordinary.WIDTH,
                              height=Ordinary.HEIGHT,
                              viewBox=(-Ordinary.FESSPTX,
                                       -Ordinary.FESSPTY,
                                       Ordinary.WIDTH,
                                       Ordinary.HEIGHT))
      self.clipPathElt=SVGdraw.SVGelement('mask',
                                          id=('Clip%04d'%Ordinary.id),
                                          attributes={"fill":"white"})
      Ordinary.id=Ordinary.id+1
      self.svg.addElement(self.clipPathElt)
      self.svg.attributes["xmlns:xlink"]="http://www.w3.org/1999/xlink"
      self.maingroup=SVGdraw.group()
      self.maingroup.attributes["mask"]="url(#%s)"%self.clipPathElt.attributes["id"]
      self.baseRect=SVGdraw.rect(x=-Ordinary.FESSPTX,
                                 y=-Ordinary.FESSPTY,
                                 width=Ordinary.WIDTH,
                                 height=Ordinary.HEIGHT)
      # Not the best solution...
      self.baseRect.charge=self

      self.inverted = False

   def fimbriate(self,color):
      # Only plain colors ATM
      # sys.stderr.write("fimbriating with %s\n"%color)
      self.fimbriation=Treatment.lookup[color]

   def void(self,color):
      self.fimbriate(color)
      self.tincture=Treatment("none")

   # Is this too brittle a way to do it?
   def do_fimbriation(self):
      t=self.clipPathElt.attributes.get("transform")
      if not t:
         t=""
      self.maingroup.addElement(SVGdraw.SVGelement('use',
                                                   attributes={"xlink:href":"#%s"%self.clipPath.attributes["id"],
                                                               "stroke":self.fimbriation,
                                                               "stroke-width":self.fimbriation_width,
                                                               "fill":"none",
                                                               "transform": t}))

   def process(self): pass

   def addCharge(self,charge):
      charge.parent=self
      self.charges.append(charge)
      # This'll be useful down the road.
      if not charge.maingroup.attributes.has_key("transform"):
         charge.maingroup.attributes["transform"]=""

   def extendCharges(self,charges):
      for elt in charges:
         self.addCharge(elt)

   def invert(self):
      self.inverted=True
      if not hasattr(self,"clipTransforms"):
         self.clipTransforms=""
      self.clipTransforms += " rotate(180)"

   def finalizeSVG(self):
      # we really should only ever do this once.
      # if self.done:
      #   return self.svg
      self.process()
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
      if hasattr(self,"clipPath"): 
         # For fimbriation (at least one way to do it), need an id on the actual
         # path, not just the group:
         self.clipPath.attributes["id"]="ClipPath%04d"%Ordinary.id
         Ordinary.id+=1
         if hasattr(self,"clipTransforms"):
            if not self.clipPath.attributes.has_key("transform"):
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
         pat[i]=tuple(x)


   def moveto(self,loc):
      pass
   def shiftto(self,loc):
      pass
   def resize(self,x,y=None):
      pass
   def scale(self,x,y=None):
      pass


class Field(Ordinary):
   def __init__(self,tincture="argent"):
      self.svg=SVGdraw.svg(x=0,y=0,width="10cm",height="11cm",
                           viewBox=(-Ordinary.FESSPTX-3,
                                    -Ordinary.FESSPTY-3,
                                    Ordinary.WIDTH+6,
                                    Ordinary.HEIGHT+6))
      #        self.svg.attributes["transform"]="scale(1,-1)"
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
      self.clipPath=SVGdraw.path(self.pdata)
      self.clipPathElt.addElement(self.clipPath)
      self.svg.addElement(SVGdraw.path(self.pdata,stroke="black",
                                       stroke_width=1,fill="none"))
      Ordinary.defs=[]                  # This is a hack.
      # self.maingroup.addElement(SVGdraw.circle(cx=0,cy=0,r=20,fill="red"))

   # A chief is different.  Adding one depresses the rest of the field.
   def addChief(self, chief):
      """Add a chief, depressing the rest of the field"""
      self.chief=chief                  # Have to handle this later.

   def addBordure(self,bordure):
      self.bordure=bordure
      bordure.parent=self
      
   def __repr__(self):
      """Output the SVG of the whole thing."""
      if not self.maingroup.attributes.has_key("transform"):
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
   def moveto(self,*args):
      # Remember, args[0] is a tuple!
      if not self.maingroup.attributes.has_key("transform"):
         self.maingroup.attributes["transform"]=""
      self.maingroup.attributes["transform"]+=" translate(%.4f,%.4f)" % args[0]
         
   # Lousy name, but we need a *different* kind of moving, to slide
   # the outline but not the innards/tincture.
   def shiftto(self,*args):
      if not self.clipPathElt.attributes.has_key("transform"):
         self.clipPathElt.attributes["transform"]=""
      self.clipPathElt.attributes["transform"]+=" translate(%.4f,%.4f)"%args[0]

   def scale(self,x,y=None):
      if not y:                        # I can't scale by 0 anyway.
         y=x
      if not self.maingroup.attributes.has_key("transform"):
         self.maingroup.attributes["transform"]=""
      self.maingroup.attributes["transform"] += " scale(%.2f,%.2f)"%(x,y)

   # Same as shiftto: changes the size of the outline only. 
   def resize(self,x,y=None):
      if not y:
         y=x
      if not self.clipPathElt.attributes.has_key("transform"):
         self.clipPathElt.attributes["transform"]=""
      self.clipPathElt.attributes["transform"] += " scale(%.2f,%.2f)"%(x,y)
              
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


class Cross(Ordinary):
    """A cross in the heraldic sense (it goes all the way to the edges of the
    shield) NOT a cross couped."""
    def process(self):
        p=partLine()
        p.lineType=self.lineType
        p.move(-10,-Ordinary.HEIGHT)
        p.makeline(-10,-10,align=1)
        p.makeline(-Ordinary.WIDTH,-10)
        p.line(-Ordinary.WIDTH,10)
        p.makeline(-10,10,align=1)
        p.makeline(-10,Ordinary.HEIGHT)
        p.line(10,Ordinary.HEIGHT)
        p.makeline(10,10,align=1)
        p.makeline(Ordinary.WIDTH,10)
        p.line(Ordinary.WIDTH,-10)
        p.makeline(10,-10,align=1)
        p.makeline(10,-Ordinary.HEIGHT)
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


class Fesse(Ordinary):
    def process(self):
        p=partLine(-Ordinary.WIDTH, -20)
        # Fesse is unusual: when "embattled", only the *top* line is
        # crenelated, unless it is blazoned "embattled counter-embattled"
        # FIXME:
        # Currently, "embattled" renders it "embattled counter-embattled".
        p.lineType=self.lineType
        p.rect(-Ordinary.WIDTH,-20,Ordinary.WIDTH*3,40)
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)

    @staticmethod
    def patternContents(num):
       patterns=[[.5],[.5,(0,0)],
                 [.5,(-20,0),(20,0)],
                 [.35,(-28,0),(28,0),(0,0)],
                 [.29,(-33,0),(-11,0),(11,0),(33,0)]
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
                 
class Bar(Fesse,Charge):
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
                [(1,.5), (0,30), (0,15), (0,0), (0,-15), (0,-30)]
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
   def process(self):
      p=partLine()
      p.lineType=self.lineType
      p.rect(-Ordinary.WIDTH,-6,Ordinary.WIDTH*3,5)
      p.rect(-Ordinary.WIDTH,1,Ordinary.WIDTH*3,5)
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

class Saltire(Cross):
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

class Pall(Ordinary):
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
                 [.2,(-25,-25),(25,-25)],
                 [.2,(-25,-25),(25,-25),(0,25)],
                 [.2,(-25,-25),(25,-25),(0,25),(0,0)]
                 ]
       try:
          res=patterns[num]
          if hasattr(self,"inverted") and self.inverted:
             self.invertPattern(res)
          return res
       except IndexError:
          return None

class Pale(Ordinary):
    def process(self):
        p=partLine()
        p.lineType=self.lineType
        p.rect(-10,-Ordinary.HEIGHT,20,Ordinary.HEIGHT*3)
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)

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

class Pallet(Pale,Charge):
   # Or would this be better done as Paly of an odd number?
   def process(self):
      p=partLine(linetype=self.lineType)
      p.rect(-5,-Ordinary.HEIGHT,10,Ordinary.HEIGHT*3)
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

   def patternWithOthers(self,num):
      patterns=[[1],[1,(0,0)],
                [1,(-10,0),(10,0)],     
                [1,(-20,0),(0,0),(20,0)], # They should be wide-spaced.
                [1,(-30,0),(-10,0),(10,0),(30,0)],
                [1,(-30,0),(-15,0),(0,0),(15,0),(30,0)],
                [1,(-35,0),(-21,0),(-7,0),(7,0),(21,0),(35,0)],
                [1,(-45,0),(-30,0),(-15,0),(0,0),(15,0),(30,0),(45,0)]
                ]
      try:
         return patterns[num]
      except IndexError:
         return None

   def moveto(self,loc):
      Charge.moveto(self,loc)
   def shiftto(self,loc):
      Charge.moveto(self,loc)
   def resize(self,x,y=None):
      Charge.resize(self,x,y)
   def scale(self,x,y=None):
      Charge.scale(self,x,y)


class Bend(Ordinary):
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
        r.rect(-10,-Ordinary.HEIGHT,20,Ordinary.HEIGHT*3)
        p=SVGdraw.path(r)
        p.attributes["transform"]=self.transform
        self.clipPath=p
        self.clipPathElt.addElement(p)
        # Hrm.  But now the outer clipping path (?) is clipping the end of
        # the bend??

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
       # Should have something to rotate the charges too...
       patterns=[[.25],[.25,(0,0)],
                 [.25,(-30,-30),(26,26)],
                 [.25,(-30,-30),(26,26),(0,0)],
                 [.25,(-30,-30),(-12,-12),(8,8),(26,26)]
                 ]
       try:
          return patterns[num]
       except IndexError:
          return None


class Bendlet(Bend,Charge):
    def process(self):
       r=partLine()
       r.lineType=self.lineType
       r.rect(-5,-Ordinary.HEIGHT,10,Ordinary.HEIGHT*3)
       p=SVGdraw.path(r)
       p.attributes["transform"]=self.transform
       self.clipPath=p
       self.clipPathElt.addElement(p)

    @staticmethod
    def patternWithOthers(num):
       patterns=[[1],[1,(0,0)],
                 [1,(7,-7),(-7,7)],
                 [1,(-10,10),(0,0),(10,-10)],
                 [1,(-21,21),(-7,7),(7,-7),(21,-21)],
                 [1,(-24,24),(-12,12),(0,0),(12,-12),(24,-24)]
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

class BendSinister(Bend):
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
          rv.append((-b[i][0],b[i][1]))
       return rv

    @staticmethod
    def patternSiblings(num):
       b=Bend.patternSiblings(num)
       rv=[]
       rv.append(b[0])
       for i in range(1,len(b)):
          rv.append((-b[i][0],b[i][1]))
       return rv

class BendletSinister(BendSinister,Bendlet):
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

   def moveto(self,loc):
      Charge.moveto(self,loc)
   def shiftto(self,loc):
      Charge.shiftto(self,loc)
   def scale(self,x,y=None):
      Charge.scale(x,y)
   def resize(self,x,y=None):
      Charge.resize(self,x,y)

class Baton(BendletSinister):
   def __init__(self,*args,**kwargs):
      BendletSinister.__init__(self,*args,**kwargs)

   def process(self):
      sys.stderr.write("transform: %s\n"%self.transform)
      self.clipPath=SVGdraw.rect(-5,-Ordinary.FESSPTY+10,
                                 10,Ordinary.HEIGHT-30)
      if hasattr(self,"transform"):
         self.clipPath.attributes["transform"]=self.transform
      self.clipPathElt.addElement(self.clipPath)

class Chief(Ordinary):
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
        if p.lineType and p.lineType <> "plain":
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

class Bordure(Ordinary):
   # Doing lines of partition is going to be hard with this one.
   def process(self):
      if self.lineType and self.lineType <> "plain":
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


    
class Chevron(Ordinary):

    def __init__(self,*args,**kwargs):
       Ordinary.__init__(self,*args,**kwargs)
       self.chevronwidth=25
       
    def drawme(self,width):
        p=partLine()
        p.lineType=self.lineType
        p.move(-Ordinary.FESSPTX,20)
        p.makeline(0,-20,align=1,shift=-1)
        p.makeline(Ordinary.FESSPTX,20)
        p.relvline(width)
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

    def moveto(self,*args):
      if not self.maingroup.attributes.has_key("transform"):
         self.maingroup.attributes["transform"]=""
      self.maingroup.attributes["transform"]+=" translate(%.4f,%.4f)" % args[0]
         
    def shiftto(self,*args):
       if not self.clipPathElt.attributes.has_key("transform"):
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
           

class Chevronel(Chevron):
   def __init__(self,*args,**kwargs):
      Chevron.__init__(self,*args,**kwargs)
      self.chevronwidth=10

class Pile(Ordinary,Charge):
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

    def moveto(self,loc):
       Charge.moveto(self,loc)
    def shiftto(self,loc):
       Charge.shiftto(self,loc)
    def scale(self,x,y=None):
       Charge.scale(x,y)

    def resize(self,x,y=None):
       # I don't really care about y anyway.
       if not self.clipPathElt.attributes.has_key("transform"):
          self.clipPathElt.attributes["transform"]=""
       self.clipPathElt.attributes["transform"]+=" scale(%.4f,1)"%x
       
class Base(Ordinary):
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

class Label(Ordinary):
   def __init__(self,points=3,*args,**kwargs):
      self.points=points
      self.setup(*args,**kwargs)

   def process(self):
      p=SVGdraw.pathdata()              # Labels don't get lines of partition.
      p.move(-Ordinary.FESSPTX,-25)
      p.relhline(Ordinary.WIDTH)
      p.relvline(4)
      p.relhline(-2)                    # There's a reason for this.
      for i in range(0,self.points):
         p.relhline((-Ordinary.WIDTH+self.points*4)/(self.points+2.0)-4)
         p.relvline(10)
         p.relhline(-4)
         p.relvline(-10)
      p.hline(-Ordinary.FESSPTX)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

class ChargeGroup:            # Kind of an invisible ordinary
    def __init__(self,num=None,charge=None):
        self.charges=[]
        self.svg=SVGdraw.svg(x=-Ordinary.FESSPTX,
                             y=-Ordinary.FESSPTY,
                             width=Ordinary.WIDTH,
                             height=Ordinary.HEIGHT,
                             viewBox=(-Ordinary.FESSPTX,
                                      -Ordinary.FESSPTY,
                                      Ordinary.WIDTH,
                                      Ordinary.HEIGHT))
        self.maingroup=SVGdraw.group()
        self.svg.addElement(self.maingroup)
        if num and charge:
           self.numcharges(num,charge)

    def fromarray(self,array):
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
        placements=None
        # Explicit arrangement takes precedence
        try:
           placements=self.arrangement.pattern(len(self.charges))
        except AttributeError:
           pass
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
              placements=defaultplacements[num]
           except AttributeError:
              pass
        if not placements:
           raise "Too many objects"
        scale=placements[0]
        if type(scale) is not type(()):
           scale=(scale,scale)
        for i in range(1,num+1):
           move(self.charges[i-1], (placements[i][0],placements[i][1]))
           if len(placements[i])>2 and len(placements[2]):
              self.charges[i-1].resize(*placements[i][2])
           else:
              self.charges[i-1].resize(*scale)

    def patternSiblings(self,num):
       # Just use the first charge.
       return self.charges[0].patternSiblings(num)
                    
class Orle(ChargeGroup):
    # We will define an Orle as a bordure detached from the edge of the shield
    # (and narrower).  A Tressure is either a synonym for Orle, or else one that
    # is narrower, and may be doubled.  We'll work on it...

    # Copying the field border again...
    # OK... right, an orle has to be something *on top of* a bordure,
    # which happens to be the same color as the field.

    def __init__(self):
       self.charges=[]
       self.svg=SVGdraw.svg(x=-Ordinary.FESSPTX,
                            y=-Ordinary.FESSPTY,
                            width=Ordinary.WIDTH,
                            height=Ordinary.HEIGHT,
                            viewBox=(-Ordinary.FESSPTX,
                                     -Ordinary.FESSPTY,
                                     Ordinary.WIDTH,
                                     Ordinary.HEIGHT))
       # First, add a bordure in the color of the field.  Somehow.
       self.bord=Bordure()                   # How to set its color??
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
   def process(self):
      Orle.makebord(self,.85,.8)
      

class Roundel(Charge):
   def process(self):
      self.clipPath=SVGdraw.circle(cx=0,cy=0,r=36) # make it 36
      self.clipPathElt.addElement(self.clipPath)

class Lozenge(Charge):
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

class Canton(Ordinary):
    # This one can't be an ExtCharge, because it has a special placement.
    def process(self):
        # Make the rectangle around the fess point, let the usual Ordinary
        # patternContents do its thing, then just diddle its
        # positioning.
        # Do not touch the scaling, lest furs and stuff get unduly resized.
        self.clipPath=SVGdraw.rect(-Ordinary.WIDTH/3/2, -Ordinary.WIDTH/3/2,
                                   Ordinary.WIDTH/3, Ordinary.HEIGHT/3)
        self.clipPathElt.addElement(self.clipPath)
        # Is the fimbriation right, though?  And does anyone fimbriate cantons?
        # We can always move the upper left corner a little offscreen.
        if not self.maingroup.attributes.has_key("transform"):
            self.maingroup.attributes["transform"]=""
        self.maingroup.attributes["transform"]=" translate(-%f,-%f)"%(Ordinary.FESSPTX*.7,Ordinary.FESSPTY*.7)

class Gyron(Ordinary):
    # Should we consider the possibility of more than one?  Or of a canton?
    def process(self):
        p=SVGdraw.pathdata()
        p.move(-Ordinary.FESSPTX, -Ordinary.FESSPTY)
        p.relline(Ordinary.WIDTH/3, Ordinary.HEIGHT/3)
        p.relhline(-Ordinary.WIDTH/3)
        p.closepath()
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)

class Fret(Ordinary):
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

class Flaunches(Ordinary):
    # Always come in pairs.  Maybe each object draws the pair, and
    # we'll just have duplicates on top of each other?  Bleah.
    # Or just find a way to ignore number for flaunches

    def process(self):
        # I don't think flaunches can take lines of partition.
        # Are they too big, you think?
        p=SVGdraw.pathdata()
        p.move(-Ordinary.FESSPTX-6,-Ordinary.FESSPTY)
        p.ellarc(Ordinary.WIDTH/4,Ordinary.HEIGHT/2,0,1,1,
                 -Ordinary.FESSPTX-6,Ordinary.FESSPTY)
        p.closepath()
        p.move(Ordinary.FESSPTX+6,-Ordinary.FESSPTY)
        p.ellarc(Ordinary.WIDTH/4,Ordinary.HEIGHT/2,0,1,0,
                 Ordinary.FESSPTX+6,Ordinary.FESSPTY)
        p.closepath()
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)

    def patternSiblings(self,num):
        # They go on a line down the center, only.
        return Pale.patternContents(num)

class Triangle(Charge):
    def process(self):
        p=SVGdraw.pathdata()
        p.move(0,-40)
        p.line(34.6,20)
        p.line(-34.6,20)
        p.closepath()
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)

class Billet(Charge):
    def process(self):
        self.clipPath=SVGdraw.rect(-15,-25,30,50)
        self.clipPathElt.addElement(self.clipPath)

class Annulet(Charge):
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
    #   Perhaps through external matadata?
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
        "firtwig":("data/Firtwig.svg#firtwig",2,None)
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
            

    def process(self):
        u=SVGdraw.use(self.path)
        if hasattr(self,"inverted") and self.inverted:
           if not u.attributes.has_key("transform"):
              u.attributes["transform"]=""
           u.attributes["transform"]+=" rotate(180)"
        self.clipPathElt.addElement(u)

    def do_fimbriation(self):
       self.maingroup.addElement(SVGdraw.SVGelement('use',
                                                    attributes={"xlink:href":"%s"%self.path,
                                                                "stroke":self.fimbriation,
                                                                "stroke-width":self.fimbriation_width,
                                                                "fill":"none",
                                                                "transform":self.clipPathElt.attributes.get("transform")}))


# Another external charge class, this one for things not used as clipping
# paths?

class Symbol(Charge):
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
      self.clipPath=SVGdraw.use(self.path)
      self.clipPathElt.addElement(self.clipPath)
      self.maingroup.addElement(self.baseRect)
      self.maingroup.addElement(SVGdraw.use(self.path))

   def fimbriate(self,treatment):
      self.fimbriation=Treatment(treatment)

   # This so totally doesn't work.
   # This isn't much of an improvement.
   def do_fimbriation(self):
      self.fimb=SVGdraw.group()
      mask=SVGdraw.SVGelement('mask',attributes={"id" : "Mask%04d"%Ordinary.id})
      Ordinary.id+=1
      for i in range(0,4):
         el=SVGdraw.use(self.path)
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
      if hasattr(self,"clipPath"): 
         # For fimbriation (at least one way to do it), need an id on the actual
         # path, not just the group:
         self.clipPath.attributes["id"]="ClipPath%04d"%Ordinary.id
         Ordinary.id+=1
         if hasattr(self,"clipTransforms"):
            if not self.clipPath.attributes.has_key("transform"):
               self.clipPath.attributes["transform"]=""
            self.clipPath.attributes["transform"] += self.clipTransforms
      if hasattr(self,"fimbriation"):
           self.do_fimbriation()
      #self.maingroup=self.tincture.fill(self.maingroup)
      self.maingroup.attributes["fill"]="none"
      self.baseRect=self.tincture.fill(self.baseRect)
      self.maingroup.attributes["mask"]="url(#%s)"%self.clipPathElt.attributes["id"]
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
      last=SVGdraw.use(self.path)
      last.attributes["fill"]="none"
      try:
         last.attributes["transform"]=self.maingroup.attributes["transform"]
      except KeyError:
         pass
      self.svg.addElement(last)
      return self.svg


   def resize(self,x,y=None):
      if not y:
         y=x
      if not self.maingroup.attributes.has_key("transform"):
         self.maingroup.attributes['transform']=""
      self.maingroup.attributes['transform']+=" scale(%.3f,%.3f)"%(x,y)

   # This helps, but screws up differently:
#   def moveto(self,*args):
#      self.shiftto(*args)

# Check the 2lions.svg file!!  Both the mask AND the later <use> have to be
# translated.


# A class for raster (non-vector) images.  Eww.
class Image(Charge):
   "External link to a non-vector image"

   def __init__(self, url, width, height, *args, **kwargs):
      self.setup(*args)
      self.url=url
      (self.width,self.height)=(width, height)

   def process(self):
      u=SVGdraw.image(self.url, x= -self.width/2.0, y= -self.height/2.0,
                      width=self.width,
                      height=self.height)
      if self.maingroup.attributes.has_key("transform"):
         u.attributes["transform"]=self.maingroup.attributes["transform"]
      self.ref=u

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
      return self.ref


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

# Old YAPPS parser:
# import parse
# New YACC parser:
import plyyacc

class Blazon:
   """A blazon is a heraldic definition. We would like to be as liberal
   as possible in what we accept."""
   def __init__(self, blazon):
      # Our parser is somewhat finicky, so we want to convert the raw,
      # user-provided text into something it can handle.
      self.blazon=self.Normalize(blazon)
   def Normalize(self, blazon):
      # Can't just toss all the non-alphanumeric chars, if we're going
      # to accept URLs...
      # return re.sub("[^a-z0-9 ']+"," ",blazon.lower())
      bits=re.split("[<>]",blazon)
      # Splitting on the <>s means that every odd-indexed element in the
      # list is one that belongs in <>s and thus literal
      i=0
      for i in range(0,len(bits)):
         if i%2 == 0:
            bits[i]=re.sub("[^a-z0-9() -]+"," ",bits[i].lower())
         else:
            bits[i]='<'+bits[i]+'>'
      return ' '.join(bits)
   def GetBlazon(self):
      return self.blazon
   def getlookuptable(self):
      self.__class__.lookup={}
      try:
         fh=open('data/Chargelist','r')
         for line in fh:
            (key, value)=line.split(':',1)
            self.__class__.lookup[key.strip()]=value.strip()
      except IOError:
         pass
   def GetShield(self):
      if not hasattr(self.__class__,'lookup') or not self.__class__.lookup:
         self.getlookuptable()
      return plyyacc.yacc.parse(self.GetBlazon())

if __name__=="__main__":
   cmdlineinput = " ".join(sys.argv[1:])
   blazon = Blazon(cmdlineinput)
   # Old YAPPS parser:
   # return parse.parse('blazon', self.GetBlazon())
   # New YACC parser:
   print plyyacc.yacc.parse(self.GetBlazon())
   
