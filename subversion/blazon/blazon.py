#!/usr/bin/python
# -*- coding: latin-1 -*-
import SVGdraw
import math
import sys
import copy
import re

from pathstuff import partLine
from tinctures import *

# For the sake of argument, let's assume the base background SVG is 100x125
# in user-units, starting from 0,0 at top left.  Most ordinaries will also
# be the same size and same location--only they'll have clipping paths,
# which may also be stroked.  Then we can just fill the whole ordinary (or
# a rectangle filling it).

class Ordinary:
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

   def setup(self,tincture="argent",linetype="plain"):
      self.done=False
      self.tincture=Tincture(tincture)
      self.lineType=linetype
      self.charges=[]
      if not hasattr(self,"svg"):
         self.svg=SVGdraw.svg(x=-Ordinary.FESSPTX,
                              y=-Ordinary.FESSPTY,
                              width=Ordinary.WIDTH,
                              height=Ordinary.HEIGHT,
                              viewBox=(-Ordinary.FESSPTX,
                                       -Ordinary.FESSPTY,
                                       Ordinary.WIDTH,
                                       Ordinary.HEIGHT))
      self.clipPathElt=SVGdraw.SVGelement('clipPath',
                                          id=('Clip%04d'%Ordinary.id))
      Ordinary.id=Ordinary.id+1
      self.svg.addElement(self.clipPathElt)
      self.maingroup=SVGdraw.group()
      self.maingroup.attributes["clip-path"]="url(#%s)"%self.clipPathElt.attributes["id"]
      self.baseRect=SVGdraw.rect(x=-Ordinary.FESSPTX,
                                 y=-Ordinary.FESSPTY,
                                 width=Ordinary.WIDTH,
                                 height=Ordinary.HEIGHT)
      # Not the best solution...
      self.baseRect.charge=self

   def fimbriate(self,color):
      # Only plain colors ATM
      # sys.stderr.write("fimbriating with %s\n"%color)
      self.fimbriation=Tincture.lookup[color]

   # Is this too brittle a way to do it?
   def do_fimbriation(self):
      self.maingroup.addElement(SVGdraw.SVGelement('use',
                                                   attributes={"xlink:href":"#%s"%self.clipPath.attributes["id"],
                                                               "stroke":self.fimbriation,
                                                               "stroke-width":"4",
                                                               "fill":"none"}))

   def process(self): pass

   def addCharge(self,charge):
      charge.parent=self
      self.charges.append(charge)

   def extendCharges(self,charges):
      for elt in charges:
         elt.parent=self
      self.charges.extend(charges)

   def invert(self):
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
            self.maingroup.addElement(charge.finalizeSVG())
      if hasattr(self,"newmaingroup"):
         self.maingroup=self.newmaingroup
      self.svg.addElement(self.maingroup)
      # Add in all the defs...
      for i in self.mydefs:
         defs.addElement(i)
      # self.done=True
      return self.svg


class Field(Ordinary):
   def __init__(self,tincture="argent"):
      self.svg=SVGdraw.svg(x=0,y=0,width="10cm",height="12.5cm",
                           viewBox=(-Ordinary.FESSPTX-3,
                                    -Ordinary.FESSPTY-3,
                                    Ordinary.WIDTH+6,
                                    Ordinary.HEIGHT+6))
      #        self.svg.attributes["transform"]="scale(1,-1)"
      self.pdata=SVGdraw.pathdata()
      self.pdata.move(-Ordinary.FESSPTX,-Ordinary.FESSPTY)
      self.pdata.bezier(-Ordinary.FESSPTX,
                        Ordinary.HEIGHT*7/8-Ordinary.FESSPTY,
                        0,Ordinary.HEIGHT-Ordinary.FESSPTY,
                        0,Ordinary.HEIGHT-Ordinary.FESSPTY)
      self.pdata.bezier(0,Ordinary.HEIGHT-Ordinary.FESSPTY,
                        Ordinary.FESSPTX,
                        Ordinary.HEIGHT*7/8-Ordinary.FESSPTY,
                        Ordinary.FESSPTX,-Ordinary.FESSPTY)
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
      
   def __repr__(self):
      if hasattr(self,"chief"):
         # Do I need to worry to *append* rather than replace the transform?
         # Hm.  Somehow I need add something outside the main group
         # AFTER things have happened...
         #
         # TODO: Currently this doesn't work when the chief is filled with
         # a pattern.  The pattern def happens *after* the chief.
         g=SVGdraw.group()
         g.attributes["clip-path"]=self.maingroup.attributes["clip-path"]
         g.addElement(self.maingroup)
         self.maingroup.attributes["transform"]="scale(1,.8) translate(0,15)"
         self.newmaingroup=g
         g2=SVGdraw.group()
         g2.attributes["clip-path"]=self.maingroup.attributes["clip-path"]
         g2.addElement(self.chief.finalizeSVG())
         #self.svg.addElement(g)
      self.finalizeSVG()
      if hasattr(self,"chief"):
         self.svg.addElement(g2)        # ugh.
      drawing=SVGdraw.drawing()
      drawing.setSVG(self.svg)
      for thing in Ordinary.defs:
         self.defsElt.addElement(thing)
      return drawing.toXml()



class Cross(Ordinary):
    def process(self):
        p=partLine()
        p.lineType=self.lineType
        p.rect(-10,-Ordinary.HEIGHT,20,Ordinary.HEIGHT*3)
        p.rect(-Ordinary.WIDTH,-10,Ordinary.WIDTH*3,20)
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)


class Fesse(Ordinary):
    def process(self):
        p=partLine(-Ordinary.WIDTH, -20)
        # Fesse is unusual: when "embattled", only the *top* line is
        # crenelated, unless it is blazoned "embattled counter-embattled"
        p.lineType=self.lineType
        p.rect(-Ordinary.WIDTH,-20,Ordinary.WIDTH*3,40)
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)
        
class Saltire(Ordinary):
    def process(self):
        p=partLine()
        p.lineType=self.lineType
        p.rect(-10,-Ordinary.HEIGHT,20,Ordinary.HEIGHT*3)
        p.rect(-Ordinary.WIDTH,-10,Ordinary.WIDTH*3,20)
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)
        self.clipPath.attributes["transform"]="rotate(45)"

class Pale(Ordinary):
    def process(self):
        p=partLine()
        p.lineType=self.lineType
        p.rect(-10,-Ordinary.HEIGHT,20,Ordinary.HEIGHT*3)
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)

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

class BendSinister(Bend):
    def __init__(self,*args,**kwargs):
        self.setup(*args,**kwargs)
        self.transform="rotate(45)"

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

class Bordure(Ordinary):
   # Doing lines of partition is going to be hard with this one.
   def process(self):
      # I don't like copying the field border the hard way like this.
      # Is there a more elegant way?
      pdata=SVGdraw.pathdata()
      pdata.move(-Ordinary.FESSPTX,-Ordinary.FESSPTY)
      pdata.bezier(-Ordinary.FESSPTX,
                   Ordinary.HEIGHT*7/8-Ordinary.FESSPTY,
                   0,Ordinary.HEIGHT-Ordinary.FESSPTY,
                   0,Ordinary.HEIGHT-Ordinary.FESSPTY)
      pdata.bezier(0,Ordinary.HEIGHT-Ordinary.FESSPTY,
                   Ordinary.FESSPTX,
                   Ordinary.HEIGHT*7/8-Ordinary.FESSPTY,
                   Ordinary.FESSPTX,-Ordinary.FESSPTY)
      pdata.closepath()
      self.clipPath=SVGdraw.path(pdata)
      self.clipPath.attributes["transform"]=" scale(.75)"
      self.clipPathElt.addElement(SVGdraw.rect(-Ordinary.WIDTH,-Ordinary.HEIGHT,
                                               Ordinary.WIDTH*4,
                                               Ordinary.HEIGHT*4))
      self.clipPathElt.attributes["fill-rule"]="evenodd"
      self.clipPathElt.addElement(self.clipPath)


class Chevron(Ordinary):
    def process(self):
        p=partLine()
        p.lineType=self.lineType
        p.move(-Ordinary.FESSPTX,20)
        p.makeline(0,-20,1)
        p.makeline(Ordinary.FESSPTX,20)
        p.relvline(30)
        p.makeline(0,10)
        p.makeline(-Ordinary.FESSPTX,50)
        p.closepath
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)

class Pall(Ordinary):
   pass
   # TODO: UNFINISHED!!!

class Pile(Ordinary):
    def process(self):
        p=partLine()
        p.lineType=self.lineType
        p.move(-Ordinary.FESSPTX/2,-Ordinary.FESSPTY)
        # The top line is always plain.
        # Need to draw more outside the box in case it is inverted
        p.line(0,-Ordinary.HEIGHT*2)
        p.line(Ordinary.FESSPTX/2,-Ordinary.FESSPTY)
        p.makeline(*Ordinary.BASEPT)
        p.makeline(-Ordinary.FESSPTX/2,-Ordinary.FESSPTY,align=1)
        p.closepath
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)

class ChargeGroup:
    def __init__(self,num=None,charge=None):
        self.elts=[]
        if num and charge:
           self.numcharges(num,charge)

    def numcharges(self,num,charge):
        for i in range(0,num):
            self.elts.append(copy.deepcopy(charge))
        self.arrange()

    def arrange(self):
        # This can only work for a relatively small number, say up to 3
        # TODO: check for sibling ordinaries to be "between", or parent
        # ordinaries to be "on", or "in pale/fesse/bend/cross/saltire"
        # And scaling?
        num=len(self.elts)
        if num<1:
            # nothing to do!
            pass
        elif num==1:
            # only for completeness
            obj=self.elts[0]
            obj.moveto(Ordinary.FESSEPT)
            # Maybe scale it?
            obj.scale(2)
        elif num==2 or num==3:
            self.elts[0].moveto(Ordinary.DEXSIDE)
            self.elts[1].moveto(Ordinary.SINSIDE)
            if num==3:
                self.elts[0].moveto((0,-10))
                self.elts[1].moveto((0,-10))
                self.elts[2].moveto(Ordinary.FESSEPT)
                self.elts[2].moveto((0,15))
        elif num > 3 and num < 6:
           # Scale the charges down a bit so they don't merge
           for elt in self.elts:
              elt.scale(0.8)
           if num==4:
              self.elts[0].moveto(Ordinary.DEXSIDE)
              self.elts[1].moveto(Ordinary.SINSIDE)
              self.elts[2].moveto(Ordinary.DEXSIDE)
              self.elts[3].moveto(Ordinary.SINSIDE)
              self.elts[0].moveto((0,-25))
              self.elts[1].moveto((0,-25))
              self.elts[2].moveto((0,20))
              self.elts[3].moveto((0,20))
           if num==5:
              self.elts[0].moveto(Ordinary.DEXSIDE)
              self.elts[1].moveto(Ordinary.SINSIDE)
              self.elts[3].moveto(Ordinary.DEXSIDE)
              self.elts[4].moveto(Ordinary.SINSIDE)
              self.elts[0].moveto((-10,-25))
              self.elts[1].moveto((10,-25))
              self.elts[3].moveto((-10,20))
              self.elts[4].moveto((10,20))
        else:                           # Too damn many.
            raise "Too many elements in charge group: %d"%num
        

class Charge(Ordinary):
    def moveto(self,*args):
        # Remember, args[0] is a tuple!
        if not self.svg.attributes.has_key("transform"):
            self.svg.attributes["transform"]=""
        self.svg.attributes["transform"]+=" translate(%d,%d)" % args[0]

    def scale(self,x,y=None):
       if y==None:
          y=x
       if not self.svg.attributes.has_key("transform"):
          self.svg.attributes["transform"]=""
       self.svg.attributes["transform"] += " scale(%.2f,%.2f)"%(x,y)
              
    def dexterchief(self):
        self.moveto(Ordinary.DEXCHIEF)

    def sinisterchief(self):
        self.moveto(Ordinary.SINCHIEF)

    def chief(self):
        self.moveto(Ordinary.CHIEFPT)

class Roundel(Charge):
   def process(self):
      self.clipPathElt.addElement(SVGdraw.circle(cx=0,cy=0,r=40))
      if not self.maingroup.attributes.has_key("transform"):
         self.maingroup.attributes["transform"]=""
         # This is not handled well.  but it's a start.
      self.maingroup.attributes["transform"] +=" scale(.3)"

class Lozenge(Charge):
   def process(self):
      p=SVGdraw.pathdata()
      p.move(0,-20)
      p.line(15,0)
      p.line(0,20)
      p.line(-15,0)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

class ExtCharge(Charge):
    def __init__(self,path,*args,**kwargs):
        self.setup(*args,**kwargs)
        self.path=path

    def process(self):
        self.clipPathElt.addElement(SVGdraw.use(self.path))

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
        self.blazon = self.Normalize(blazon)
    def Normalize(self, blazon):
        return re.sub("[^a-z0-9 ]+"," ",blazon.lower())
    def GetBlazon(self):
        return self.blazon
    def GetShield(self):
        # Old YAPPS parser:
        # return parse.parse('blazon', self.GetBlazon())
        # New YACC parser:
        return plyyacc.yacc.parse(self.GetBlazon())

if __name__=="__main__":
    cmdlineinput = " ".join(sys.argv[1:])
    blazon = Blazon(cmdlineinput)
    # Old YAPPS parser:
    # return parse.parse('blazon', self.GetBlazon())
    # New YACC parser:
    print plyyacc.yacc.parse(self.GetBlazon())
