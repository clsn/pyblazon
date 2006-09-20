#!/usr/bin/python

import SVGdraw
import math
import sys
import copy
import re

from pathstuff import partLine

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

   def fimbriate(self,color):
      # Only plain colors ATM
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
      
   def __repr__(self):
      self.finalizeSVG()
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
#       self.svg.addElement(SVGdraw.path(p,stroke="black",
#                                        stroke_width=2,
#                                        fill="none"))
        
class Saltire(Ordinary):
    def process(self):
        g=SVGdraw.group()
        self.clipPathElt.addElement(g)
        p=partLine()
        p.lineType=self.lineType
        p.rect(-10,-Ordinary.HEIGHT,20,Ordinary.HEIGHT*3)
        p.rect(-Ordinary.WIDTH,-10,Ordinary.WIDTH*3,20)
        self.clipPath=SVGdraw.path(p)
        g.addElement(self.clipPath)
#         g.addElement(SVGdraw.rect(x=-10,y=-Ordinary.HEIGHT,width=20,
#                                   height=Ordinary.HEIGHT*3))
#         g.addElement(SVGdraw.rect(x=-Ordinary.WIDTH,y=-10,
#                                   width=Ordinary.WIDTH*3,height=20))
        g.attributes["transform"]="rotate(45)"

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
        p.rect(-Ordinary.WIDTH,-Ordinary.FESSPTY-Ordinary.HEIGHT,
               Ordinary.WIDTH*3,Ordinary.HEIGHT+23)
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)

class Chevron(Ordinary):
    def process(self):
        p=partLine()
        p.lineType=self.lineType
        p.move(-Ordinary.FESSPTX,20)
        p.makeline(0,-20)
        p.makeline(Ordinary.FESSPTX,20)
        p.relvline(30)
        p.makeline(0,10)
        p.makeline(-Ordinary.FESSPTX,50)
        p.closepath
        self.clipPath=SVGdraw.path(p)
        self.clipPathElt.addElement(self.clipPath)

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
        p.makeline(-Ordinary.FESSPTX/2,-Ordinary.FESSPTY)
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
        else:                           # Too damn many.
            raise "Too many elements in charge group: %d"%num
        

class Charge:
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

class SubOrdinary(Charge, Ordinary):
   def __init__(self,*args,**kwargs):
      self.setup(*args,**kwargs)
      
class Roundel(SubOrdinary):
   def process(self):
      self.clipPathElt.addElement(SVGdraw.circle(cx=0,cy=0,r=30))
      if not self.maingroup.attributes.has_key("transform"):
         self.maingroup.attributes["transform"]=""
         # This is not handled well.  but it's a start.
         self.maingroup.attributes["transform"] +=" scale(.3)"

class Lozenge(SubOrdinary):
   def process(self):
      p=SVGdraw.pathdata()
      p.move(0,-20)
      p.line(15,0)
      p.line(0,20)
      p.line(-15,0)
      p.closepath()
      self.clipPath=SVGdraw.path(p)
      self.clipPathElt.addElement(self.clipPath)

class Pattern: pass                     # gyronny, checky, etc.

class Tincture:                         # Metal or color.
   lookup={ "azure" : "blue",
            "gules" : "red",
            "or" : "yellow",
            "argent" : "white",
            "sable" : "black",
            "vert" : "green",
            "purpure" : "purple",
            "none" : "none"
            }
   
   def __init__(self,color):
      try:
         self.color=Tincture.lookup[color]
      except KeyError:
         sys.stderr.write("Invalid tincture: %s\n"%color)
         self.color="white"

   def fill(self, elt):
      sys.stderr.write("Being called to fill something with %s\n"%self.color)
      elt.attributes["fill"]=self.color
      return elt

class Fur(Tincture): pass

class VairInPale(Fur):
   def __init__(self,color1="argent",color2="azure"):
      try:
         if type(color1) is type("x"):
            color1=Tincture(color1)
         if type(color2) is type("x"):
            color2=Tincture(color2)
      except KeyError:
         sys.stderr.write("Invalid tinctures: %s,%s\n"%(color1,color2))
         (self.color1,self.color2)=(Tincture("argent"),Tincture("azure"))
      (self.color1,self.color2)=(color1,color2)

   def VairPattern(self):
      pattern=SVGdraw.SVGelement(type="pattern",attributes=
                                 {"patternContentUnits":"userSpaceOnUse",
                                  "height":"8",
                                  "id":"vair-in-pale%04d"%Ordinary.id,
                                  "patternUnits":"userSpaceOnUse",
                                  "width":"8"})
      pattern.addElement(self.color1.fill(SVGdraw.rect(x="0", y="0", width="8", height="8")))
      pattern.addElement(self.color2.fill(SVGdraw.SVGelement(type='path',
                                                             attributes=
                                            {"d":"M0,8 l2,-2 l0,-4 l2,-2 l2,2 l0,4 l2,2 z"})))
      self.color="vair-in-pale%04d"%Ordinary.id
      Ordinary.id+=1
      return pattern

   def fill(self,elt):
      pattern=self.VairPattern()
      Ordinary.defs.append(pattern)
      elt.attributes["fill"]="url(#%s)"%pattern.attributes["id"]
      return elt

class Vair(VairInPale):
   def fill(self,elt):
      VIPpattern=self.VairPattern()
      Ordinary.defs.append(VIPpattern)
      pattern=SVGdraw.SVGelement('pattern',attributes=
                                 {"width":"16", "height":"16",
                                  "patternUnits":"userSpaceOnUse",
                                  "patternContentUnits":"userSpaceOnUse",
                                  "id":"vair%04d"%Ordinary.id})
      self.color="vair%04d"%Ordinary.id
      Ordinary.id+=1
      pattern.addElement(SVGdraw.rect(x="0", y="0", width="16", height="8",
                                      fill="url(#%s)"%VIPpattern.attributes["id"]))
      pattern.addElement(SVGdraw.rect(x="0", y="8", width="20", height="8",
                                      fill="url(#%s)"%VIPpattern.attributes["id"],
                                      transform="translate(-4,0)"))
      Ordinary.defs.append(pattern)
      elt.attributes["fill"]="url(#%s)"%pattern.attributes["id"]
      return elt

class CounterVair(VairInPale):
   def fill(self,elt):
      pattern=SVGdraw.SVGelement('pattern',attributes=
                                 {"width":"8", "height":"16",
                                  "patternUnits":"userSpaceOnUse",
                                  "patternContentUnits":"userSpaceOnUse",
                                  "id":"counter-vair%04d"%Ordinary.id})
      Ordinary.id+=1
      pattern.addElement(SVGdraw.rect(x="0", y="0", width="8", height="18",
                                      fill=self.color1))
      pattern.addElement(SVGdraw.SVGelement('path',
                                            attributes={"d":
                                                        "M0,8 l2,-2 l0,-4 l2,-2 l2,2 l0,4 l2,2 l-2,2 l0,4 l-2,2 l-2,-2 l0,-4 z",
                                                        "fill":self.color2}))
      elt.attributes["fill"]="url(#%s)"%pattern.attributes["id"]
      Ordinary.defs.append(pattern)
      return elt

class Ermine(Fur):
   def __init__(self,color1="argent",color2="sable"):
      try:
         if type(color1) is type("x"):
            color1=Tincture(color1)
         if type(color2) is type("x"):
            color2=Tincture(color2)
      except KeyError:
         sys.stderr.write("Invalid tinctures: %s,%s\n"%(color1,color2))
         (self.color1,self.color2)=(Tincture("argent"),Tincture("sable"))
      (self.color1,self.color2)=(color1,color2)

   def fill(self,elt):
      pattern=SVGdraw.SVGelement('pattern',attributes=
                                 {"height":"15","width":"15",
                                  "patternUnits":"userSpaceOnUse",
                                  "patternContentUnits":"userSpaceOnUse",
                                  "id":"ermine%04d"%Ordinary.id})
      Ordinary.id+=1
      pattern.addElement(self.color1.fill(SVGdraw.rect(x="0",y="0",width="15",height="15")))
      pattern.addElement(self.color2.fill(SVGdraw.SVGelement('path',
                                                             attributes={"d":
                                                        "M1,5 c1,-1 1.5,-4 1.5,-4 c0,0 .5,3 1.5,4 l-1.5,1.5 z"})))
      pattern.addElement(self.color2.fill(SVGdraw.circle(cx="1.5",cy="2",
                                                         r=".5")))
      pattern.addElement(self.color2.fill(SVGdraw.circle(cx="2.5",cy="1",
                                                         r=".5")))
      pattern.addElement(self.color2.fill(SVGdraw.circle(cx="3.5",cy="2",
                                                         r=".5")))
      pattern.addElement(self.color2.fill(SVGdraw.SVGelement('path',
                                            attributes={"d":
                                                        "M8.5,12.5 c1,-1 1.5,-4 1.5,-4 c0,0 .5,3 1.5,4 l-1.5,1.5 z"})))
      pattern.addElement(self.color2.fill(SVGdraw.circle(cx="9",cy="9.5",
                                                         r=".5")))
      pattern.addElement(self.color2.fill(SVGdraw.circle(cx="10",cy="8.5",
                                                         r=".5")))
      pattern.addElement(self.color2.fill(SVGdraw.circle(cx="11",cy="9.5",
                                                         r=".5")))

      Ordinary.defs.append(pattern)
      elt.attributes["fill"]="url(#%s)"%pattern.attributes["id"]
      return elt



class Paly(Tincture):
   def parseColors(self,color1,color2):
      """For internal use, to simplify subclasses"""
      if type(color1)==type("x"):
         color1=Tincture(color1)
      if type(color2)==type("x"):
         color2=Tincture(color2)
      self.colors=(color1,color2)

   def assemble(self):
      """For internal use, to simplify assembly of subclasses"""
      p=partLine(linetype=self.lineType) # Start to support partition lines
      width=float(Ordinary.WIDTH)/self.pieces
      for i in range(1,self.pieces,2):
         p.rect(-Ordinary.FESSPTX+i*width,-Ordinary.HEIGHT,
                width,2*Ordinary.HEIGHT)
      self.path=SVGdraw.path(p)
      
   def __init__(self,bars=6,color1="argent",color2="sable",linetype="plain"):
      self.parseColors(color1,color2)
      self.lineType=linetype
      self.pieces=bars
            
   def fill(self, elt):
      self.assemble()
      self.foreground=Ordinary()        # treat it like an Ordinary
      self.foreground.clipPath=self.path
      self.foreground.clipPathElt.addElement(self.path)
      self.foreground.tincture=self.colors[1]
      self.background=SVGdraw.rect(-Ordinary.FESSPTX, -Ordinary.FESSPTY,
                                   Ordinary.WIDTH, Ordinary.HEIGHT)
      self.background=self.colors[0].fill(self.background)
   
      g=SVGdraw.group()
      g.addElement(self.background)
      g.addElement(self.foreground.finalizeSVG())
      return g

class Barry(Paly):
   def assemble(self):
      p=partLine(linetype=self.lineType)
      height=float(Ordinary.HEIGHT)/self.pieces
      # Problem.  Optical center is at 0.  Geometric center is a little lower,
      # owing to the placement of the coordinates.
      for i in range(1,self.pieces,2):
         p.rect(-Ordinary.FESSPTX, -Ordinary.FESSPTY+i*height,
                Ordinary.WIDTH, height)
      self.path=SVGdraw.path(p)

class Bendy(Paly):
   def assemble(self):
      p=partLine(linetype=self.lineType)
      # OK, let's map things on the *square* WIDTHxWIDTH
      fullwidth=math.sqrt(2)*Ordinary.WIDTH
      # Oh, this is going to be much easier to do orthogonally and rotating.
      if self.pieces>3:
         width=fullwidth*.87/self.pieces # Compensate for round corner.
      else:                             # Otherwise Per Bend doesn't work.
         width=fullwidth/self.pieces
      for i in range(1,self.pieces+2,2): # Add two to handle odd numbers, just in case.
         p.rect(fullwidth/2-i*width, -Ordinary.HEIGHT,
                width,2*Ordinary.HEIGHT)
      self.path=SVGdraw.path(p)
      self.path.attributes["transform"]="rotate(-45)"
      
class BendySinister(Paly):
   def assemble(self):
      # Can't really do this by rotating Bendy, since the round corner is
      # on the other side.
      p=partLine(linetype=self.lineType)
      fullwidth=math.sqrt(2)*Ordinary.WIDTH
      if self.pieces>3:
         width=fullwidth*.87/self.pieces # Compensate for round corner.
      else:
         width=fullwidth/self.pieces
      for i in range(1,self.pieces+2,2):
         p.rect(-fullwidth/2+i*width, -Ordinary.HEIGHT,
                width, 2*Ordinary.HEIGHT)
      self.path=SVGdraw.path(p)
      self.path.attributes["transform"]="rotate(45)"


class PerPale(Paly):
    def __init__(self,*args,**kwargs):
        # Per Pale is just Paly of two!!
        Paly.__init__(self,2,*args,**kwargs)

class PerFesse(Barry):
    def __init__(self,*args,**kwargs):
        Barry.__init__(self,2,*args,**kwargs)

class PerBend(Bendy):
    def __init__(self,*args,**kwargs):
        # Winds up in the wrong place. :(
        Bendy.__init__(self,2,*args,**kwargs)

class PerBendSinister(BendySinister):
    def __init__(self,*args,**kwargs):
        BendySinister.__init__(self,2,*args,**kwargs)

class PerCross(Paly):
   def __init__(self,color1="argent",color2="sable",linetype="plain"):
      # reverse order of colors  so I don't have to bother rewriting assemble()
      self.parseColors(color2,color1)
      self.lineType=linetype
   
   def assemble(self):
      p=partLine()
      p.lineType=self.lineType
      p.move(-Ordinary.WIDTH-Ordinary.FESSPTX,-Ordinary.HEIGHT-Ordinary.FESSPTY)
      p.hline(0)
      p.makeline(0,Ordinary.HEIGHT)
      p.hline(Ordinary.WIDTH)
      p.vline(0)
      p.makeline(-Ordinary.WIDTH,0)
      p.closepath()
      self.path=SVGdraw.path(p)
      self.path.attributes["fill-rule"]="evenodd"

class PerSaltire(PerCross):
   def assemble(self):
      PerCross.assemble(self)
      self.path.attributes["transform"]="rotate(-45)"

class PerChevron(Paly):
   def __init__(self,color1="argent", color2="sable", linetype="plain"):
      self.parseColors(color1,color2)
      self.lineType=linetype
   
   def assemble(self):
      p=partLine(linetype=self.lineType)
      p.move(-Ordinary.FESSPTX,35)
      p.makeline(0,-5)
      p.makeline(Ordinary.FESSPTX,35)
      p.relvline(Ordinary.FESSPTY)
      p.relhline(-Ordinary.WIDTH)
      p.closepath()
      self.path=SVGdraw.path(p)

# Leaving Chevronny for another day...

# Barry-bendy and paly-bendy are easy now: just do:
# paly of 8 barry of 8 or and sable and barry of 8 sable and or
# except we'll want to adjust the quantities because the shield is longer
# than it is wide.

# Ditto checky/chequy, lozengy, etc.

# Other ideas...:

# Presumably each charge (esp. each Ordinary) will be its own <g> element,
# thus allowing a remapping of coordinates.  Obv. we don't want complete
# rescaling, but it's a step.

# A "between" function, which returns a list of points in the
# *surroundings* of this Ordinary suitable for putting n other charges.
# e.g. "a bend between two annulets sable" vs. three annulets vs. a chevron
# between three, etc etc etc.  This is something that relates to a charge's
# *siblings* on the field.

import parse

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
        return parse.parse('blazon', self.GetBlazon())

if __name__=="__main__":
    cmdlineinput = " ".join(sys.argv[1:])
    blazon = Blazon(cmdlineinput)
    print blazon.GetShield()

## Old test stuff goes here:
#     d=SVGdraw.drawing()
#     s=SVGdraw.svg(x=0,y=0,width="10cm",height="10cm",viewBox=(0,0,50,50))
#     d.setSVG(s)
#     p=partLine(10,10)
#     p.lineType="indented"
#     p.makeline(40,40)
#     s.addElement(SVGdraw.path(p,stroke="black", stroke_width=".2", fill="none"))
#     print d.toXml()
   # Parsing "or a pale sable" from argv.
#   import __main__                      # !!
#   shield=Field(sys.argv[1])
   #charge=__main__.__dict__[sys.argv[3].capitalize()](sys.argv[4],"plain")
#   shield.tincture=Gyronny("or","azure")
   #shield.charges.append(charge)

#   d=SVGdraw.drawing()
#   s=SVGdraw.svg()
#   s.addElement(vair)
#   d.setSVG(s)
#   print d.toXml()

#   print shield
