#!/usr/bin/python
# -*- coding: latin-1 -*-

import SVGdraw
from pathstuff import partLine
import blazon
import copy
import sys
import math

class Pattern: pass                     # gyronny, checky, etc.

class Tincture:                         # Metal or color.
   lookup={ "azure" : "blue",
            "gules" : "red",
            "or" : "yellow",
            "argent" : "white",
            "sable" : "black",
            "vert" : "green",
            "purpure" : "purple",
            "tenné" : "#cd5700",
            "tenne" : "#cd5700",
            "tawny" : "#cd5700",
            "sanguine" : "#c00000",
            "murrey" : "#800040",
            "bleu celeste" : "#8080ff",
            "none" : "none"
            }
   
   def __init__(self,color):
      try:
         self.color=Tincture.lookup[color]
      except KeyError:
         sys.stderr.write("Invalid tincture: %s\n"%color)
         self.color="white"

   def fill(self, elt):
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
                                  "id":"vair-in-pale%04d"%blazon.Ordinary.id,
                                  "patternUnits":"userSpaceOnUse",
                                  "width":"8"})
      pattern.addElement(self.color1.fill(SVGdraw.rect(x="0", y="0", width="8", height="8")))
      pattern.addElement(self.color2.fill(SVGdraw.SVGelement(type='path',
                                                             attributes=
                                            {"d":"M0,8 l2,-2 l0,-4 l2,-2 l2,2 l0,4 l2,2 z"})))
      self.color="vair-in-pale%04d"%blazon.Ordinary.id
      blazon.Ordinary.id+=1
      return pattern

   def fill(self,elt):
      pattern=self.VairPattern()
      blazon.Ordinary.defs.append(pattern)
      elt.attributes["fill"]="url(#%s)"%pattern.attributes["id"]
      return elt

class Vair(VairInPale):
   def fill(self,elt):
      VIPpattern=self.VairPattern()
      blazon.Ordinary.defs.append(VIPpattern)
      pattern=SVGdraw.SVGelement('pattern',attributes=
                                 {"width":"16", "height":"16",
                                  "patternUnits":"userSpaceOnUse",
                                  "patternContentUnits":"userSpaceOnUse",
                                  "id":"vair%04d"%blazon.Ordinary.id})
      self.color="vair%04d"%blazon.Ordinary.id
      blazon.Ordinary.id+=1
      pattern.addElement(SVGdraw.rect(x="0", y="0", width="16", height="8",
                                      fill="url(#%s)"%VIPpattern.attributes["id"]))
      pattern.addElement(SVGdraw.rect(x="0", y="8", width="20", height="8",
                                      fill="url(#%s)"%VIPpattern.attributes["id"],
                                      transform="translate(-4,0)"))
      blazon.Ordinary.defs.append(pattern)
      elt.attributes["fill"]="url(#%s)"%pattern.attributes["id"]
      return elt

class CounterVair(VairInPale):
   def fill(self,elt):
      pattern=SVGdraw.SVGelement('pattern',attributes=
                                 {"width":"8", "height":"16",
                                  "patternUnits":"userSpaceOnUse",
                                  "patternContentUnits":"userSpaceOnUse",
                                  "id":"counter-vair%04d"%blazon.Ordinary.id})
      blazon.Ordinary.id+=1
      pattern.addElement(SVGdraw.rect(x="0", y="0", width="8", height="18",
                                      fill=self.color1))
      pattern.addElement(SVGdraw.SVGelement('path',
                                            attributes={"d":
                                                        "M0,8 l2,-2 l0,-4 l2,-2 l2,2 l0,4 l2,2 l-2,2 l0,4 l-2,2 l-2,-2 l0,-4 z",
                                                        "fill":self.color2}))
      elt.attributes["fill"]="url(#%s)"%pattern.attributes["id"]
      blazon.Ordinary.defs.append(pattern)
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
                                  "id":"ermine%04d"%blazon.Ordinary.id})
      blazon.Ordinary.id+=1
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

      blazon.Ordinary.defs.append(pattern)
      elt.attributes["fill"]="url(#%s)"%pattern.attributes["id"]
      return elt


# I wonder if this'll work...

class Countercharged(Tincture):
    def __init__(self):
        pass
    
    def fill(self,elt):
        realtincture=copy.copy(elt.charge.parent.tincture)
        realtincture.colors=(realtincture.colors[1],
                             realtincture.colors[0])
        elt=realtincture.fill(elt)
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
      width=float(blazon.Ordinary.WIDTH)/self.pieces
      # Make the lines a tiny bit too wide, so paly wavy doesn't show
      # an extra bit.
      if self.pieces>4 and self.lineType <> "plain":
         width*=1.03
      for i in range(1,self.pieces,2):
         p.rect(-blazon.Ordinary.FESSPTX+i*width,-blazon.Ordinary.HEIGHT,
                width,2*blazon.Ordinary.HEIGHT)
      self.path=SVGdraw.path(p)
      
   def __init__(self,bars=6,color1="argent",color2="sable",linetype="plain"):
      self.parseColors(color1,color2)
      self.lineType=linetype
      self.pieces=bars
            
   def fill(self, elt):
      self.assemble()
      self.foreground=blazon.Ordinary()        # treat it like an blazon.Ordinary
      self.foreground.clipPath=self.path
      self.foreground.clipPathElt.addElement(self.path)
      self.foreground.tincture=self.colors[1]
      self.background=SVGdraw.rect(-blazon.Ordinary.FESSPTX,
                                   -blazon.Ordinary.FESSPTY,
                                   blazon.Ordinary.WIDTH,
                                   blazon.Ordinary.HEIGHT)
      self.background=self.colors[0].fill(self.background)
   
      g=SVGdraw.group()
      g.addElement(self.background)
      g.addElement(self.foreground.finalizeSVG())
      return g

class Barry(Paly):
   def assemble(self):
      p=partLine(linetype=self.lineType)
      height=float(blazon.Ordinary.HEIGHT)/self.pieces
      # Make the lines a LITTLE wider, so "wavy" doesn't show an extra bit
      # at the bottom.
      if self.pieces>4 and self.lineType <> "plain":
         height*=1.03
      # Problem.  Optical center is at 0.  Geometric center is a little lower,
      # owing to the placement of the coordinates.
      for i in range(1,self.pieces,2):
         p.rect(-blazon.Ordinary.FESSPTX, -blazon.Ordinary.FESSPTY+i*height,
                2*blazon.Ordinary.WIDTH, height)
      self.path=SVGdraw.path(p)

class Bendy(Paly):
   def assemble(self):
      p=partLine(linetype=self.lineType)
      # OK, let's map things on the *square* WIDTHxWIDTH
      fullwidth=math.sqrt(2)*blazon.Ordinary.WIDTH
      # Oh, this is going to be much easier to do orthogonally and rotating.
      if self.pieces>3:
         width=fullwidth*.87/self.pieces # Compensate for round corner.
      else:                             # Otherwise Per Bend doesn't work.
         width=fullwidth/self.pieces
      for i in range(0,self.pieces+2,2): # Add two to handle odd numbers, just in case.
         p.rect(fullwidth/2-i*width, -blazon.Ordinary.HEIGHT,
                width,2*blazon.Ordinary.HEIGHT)
      self.path=SVGdraw.path(p)
      self.path.attributes["transform"]="rotate(-45)"
      
class BendySinister(Paly):
   def assemble(self):
      # Can't really do this by rotating Bendy, since the round corner is
      # on the other side.
      p=partLine(linetype=self.lineType)
      fullwidth=math.sqrt(2)*blazon.Ordinary.WIDTH
      if self.pieces>3:
         width=fullwidth*.87/self.pieces # Compensate for round corner.
      else:
         width=fullwidth/self.pieces
      for i in range(1,self.pieces+2,2):
         p.rect(-fullwidth/2+i*width, -blazon.Ordinary.HEIGHT,
                width, 2*blazon.Ordinary.HEIGHT)
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
      p.move(-blazon.Ordinary.WIDTH-blazon.Ordinary.FESSPTX,-blazon.Ordinary.HEIGHT-blazon.Ordinary.FESSPTY)
      p.hline(0)
      p.makeline(0,blazon.Ordinary.HEIGHT)
      p.hline(blazon.Ordinary.WIDTH)
      p.vline(0)
      p.makeline(-blazon.Ordinary.WIDTH,0)
      p.closepath()
      self.path=SVGdraw.path(p)
      self.path.attributes["fill-rule"]="evenodd"

class PerSaltire(PerCross):
   def assemble(self):
      PerCross.assemble(self)
      self.path.attributes["transform"]="rotate(-45)"

# start with default: Gyronny of eight.
class Gyronny(Paly):
    def assemble(self):
        # Yes, everything with HEIGHT, so I'm working in a square.
        # May have the colors backwards.
        p=partLine(linetype=self.lineType)
        p.move(0,-blazon.Ordinary.HEIGHT)
        p.makeline(0,blazon.Ordinary.HEIGHT)
        p.hline(blazon.Ordinary.HEIGHT)
        p.makeline(-blazon.Ordinary.HEIGHT,-blazon.Ordinary.HEIGHT)
        p.closepath()
        p.move(-blazon.Ordinary.HEIGHT,0)
        p.makeline(blazon.Ordinary.HEIGHT,0)
        p.vline(-blazon.Ordinary.HEIGHT)
        p.makeline(-blazon.Ordinary.HEIGHT,blazon.Ordinary.HEIGHT)
        p.closepath
        self.path=SVGdraw.path(p)
        self.path.attributes["fill-rule"]="evenodd"

class PerChevron(Paly):
   def __init__(self,color1="argent", color2="sable", linetype="plain"):
      self.parseColors(color1,color2)
      self.lineType=linetype
   
   def assemble(self):
      p=partLine(linetype=self.lineType)
      p.move(-blazon.Ordinary.FESSPTX,35)
      p.makeline(0,-5,1)
      p.makeline(blazon.Ordinary.FESSPTX,35)
      p.relvline(blazon.Ordinary.FESSPTY)
      p.relhline(-blazon.Ordinary.WIDTH)
      p.closepath()
      self.path=SVGdraw.path(p)

# Leaving Chevronny for another day...

# Barry-bendy and paly-bendy are easy now: just do:
# paly of 8 barry of 8 or and sable and barry of 8 sable and or
# except we'll want to adjust the quantities because the shield is longer
# than it is wide.

# Ditto checky/chequy, lozengy, etc.
