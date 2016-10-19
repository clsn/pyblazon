#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tinctures, furs, the main lines of division, and fields semy.
"""

import SVGdraw
from pathstuff import partLine
import blazon
import copy
import sys
import math
import arrangement

class Pattern: pass                     # gyronny, checky, etc.

class Treatment:                         # Metal or color.
    lookup={ "azure" : "blue",
             "de larmes" : "blue",
             "gules" : "red",
             "de sang" : "red",
             "or" : "yellow",
             "d'or" : "yellow",
             "argent" : "white",
             "d'eau" : "white",
             # Allows a hint of detail in sable image charges:
             "sable" : "#181818", 
             "de poix" : "#181818",
             "vert" : "green",
             "d'huile" : "green",
             "purpure" : "purple",
             "tenné" : "#cd5700",
             "tenne" : "#cd5700",
             "tawny" : "#cd5700",
             "sanguine" : "#c00000",
             "murrey" : "#800040",
             "bleu celeste" : "#8080ff",
             "rose" : "#fba0e3",
             "copper" : "#b87333",
             "proper" : "proper",       # Not none, to keep things out of the colorless array
             "fieldless" : "proper",    # syntactic sugar for fields.
             "none" : "none"
             }
   
    def __init__(self,color):
        try:
            self.color=Treatment.lookup[color]
        except KeyError:
            sys.stderr.write("Warning: invalid tincture: %s\n"%color)
            # So people can use '#bab1e5' if they want...
            self.color=color
        if self.color == "proper":
            self.color="none"

    def fill(self, elt):
        elt.attributes["fill"]=self.color
        return elt

    def invert(self):
        pass

    def modify(self, name, *args, **kwargs):
        if name == "inverted":
            self.invert()

    def orient(self,direction,*args,**kwargs):
        pass

class Fur(Treatment): pass

class VairInPale(Fur):
   def __init__(self,color1="argent",color2="azure"):
      try:
         if type(color1) is type("x"):
            color1=Treatment(color1)
         if type(color2) is type("x"):
            color2=Treatment(color2)
      except KeyError:
         sys.stderr.write("Invalid tinctures: %s,%s\n"%(color1,color2))
         (self.color1,self.color2)=(Treatment("argent"),Treatment("azure"))
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
      pattern.addElement(self.color1.fill(SVGdraw.rect(x="0", y="0", width="8",
                                                       height="18")))
      pattern.addElement(self.color2.fill(SVGdraw.SVGelement('path',
                                                             attributes={"d":
                                                                         "M0,8 l2,-2 l0,-4 l2,-2 l2,2 l0,4 l2,2 l-2,2 l0,4 l-2,2 l-2,-2 l0,-4 z"})))
      elt.attributes["fill"]="url(#%s)"%pattern.attributes["id"]
      blazon.Ordinary.defs.append(pattern)
      return elt

class Ermine(Fur):
   def __init__(self,color1="argent",color2="sable"):
      try:
         if type(color1) is type("x"):
            color1=Treatment(color1)
         if type(color2) is type("x"):
            color2=Treatment(color2)
      except KeyError:
         sys.stderr.write("Invalid tinctures: %s,%s\n"%(color1,color2))
         (self.color1,self.color2)=(Treatment("argent"),Treatment("sable"))
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

class Fretty(Ermine):
    def fill(self,elt):
        pattern=SVGdraw.SVGelement('pattern',attributes=
                                   {"height":"20", "width":"20",
                                    "patternUnits": "userSpaceOnUse",
                                    "patternContentUnits": "userSpaceOnUse",
                                    "id": "fret%04d"%blazon.Ordinary.id})
        blazon.Ordinary.id+=1
        # Why do I need a background rectangle in the pattern???
        # pattern.addElement(self.color1.fill(SVGdraw.rect(x="0",y="0",width="22",
#                                                         height="22")))
        group=SVGdraw.group()
        group.attributes["stroke"]="#888888"
        group.attributes["stroke-width"]=".1"
        rect1=self.color2.fill(SVGdraw.rect(x="-2",y="-20",
                                            width="4",height="50"))
        rect1.attributes["transform"]="translate(0,10) rotate(45)"
        
        rect2=self.color2.fill(SVGdraw.rect(x="-2",y="-20",
                                            width="4",height="50"))
        rect2.attributes["transform"]="translate(20,10) rotate(45)"
                           
        rect3=self.color2.fill(SVGdraw.rect(x="-2",y="-20",
                                            width="4",height="50"))
        rect3.attributes["transform"]="translate(0,10) rotate(-45)"
        
        rect4=self.color2.fill(SVGdraw.rect(x="-2",y="-20",
                                            width="4",height="50"))
        rect4.attributes["transform"]="translate(20,10) rotate(-45)"
        for e in [rect1,rect2,rect3,rect4]:
            group.addElement(e)
        pattern.addElement(group)
        blazon.Ordinary.defs.append(pattern)
        elt=self.color1.fill(elt)
        newelt=SVGdraw.group()
        newelt.addElement(elt)
        newbase=SVGdraw.rect(x=-blazon.Ordinary.FESSPTX,
                             y=-blazon.Ordinary.FESSPTY,
                             width=blazon.Ordinary.WIDTH,
                             height=blazon.Ordinary.HEIGHT,
                             fill="url(#%s)"%pattern.attributes["id"])
        newelt.addElement(newbase)
        return newelt

class Masoned(Fretty):
    def fill(self,elt):
        pattern=SVGdraw.SVGelement('pattern',attributes=
                                   {"height":"20", "width":"20",
                                    "patternUnits":"userSpaceOnUse",
                                    "patternContentUnits":"userSpaceOnUse",
                                    "id": "maso%04d"%blazon.Ordinary.id})
        blazon.Ordinary.id+=1
        group=SVGdraw.group()
        group.addElement(self.color2.fill(SVGdraw.rect(x="0",y="9",width="20",height="2")))
        group.addElement(self.color2.fill(SVGdraw.rect(x="0",y="10",width="1",height="10")))
        group.addElement(self.color2.fill(SVGdraw.rect(x="19",y="10",width="1",height="10")))
        group.addElement(self.color2.fill(SVGdraw.rect(x="9",y="0",width="2", height="10")))
        group.addElement(self.color2.fill(SVGdraw.rect(x="0",y="0",width="20",height="1")))
        group.addElement(self.color2.fill(SVGdraw.rect(x="0",y="19",width="20",height="1")))
        pattern.addElement(group)
        blazon.Ordinary.defs.append(pattern)
        elt=self.color1.fill(elt)
        newelt=SVGdraw.group()
        newelt.addElement(elt)
        newbase=SVGdraw.rect(x=-blazon.Ordinary.FESSPTX,
                             y=-blazon.Ordinary.FESSPTY,
                             width=blazon.Ordinary.WIDTH,
                             height=blazon.Ordinary.HEIGHT,
                             fill="url(#%s)"%pattern.attributes["id"])
        newelt.addElement(newbase)
        return newelt                               

class Semy(Fur):
    def __init__(self,background,charge):
        self.background=background
        self.charge=charge

    def fill(self,elt):
        pattern=SVGdraw.SVGelement('pattern',attributes=
                                   {"height":"20", "width":"20",
                                    "patternUnits": "userSpaceOnUse",
                                    "patternContentUnits": "userSpaceOnUse",
                                    "id": "semy%04d"%blazon.Ordinary.id})
        blazon.Ordinary.id+=1
        # Just in case we try to countercharge it.  It doesn't work anyway.
        self.colors=(self.background,self.charge.tincture)
        charge2=copy.deepcopy(self.charge)
        self.charge.moveto((5,15))
        self.charge.scale(.1)
        charge2.moveto((15,5))
        charge2.scale(.1)
        #pattern.addElement(SVGdraw.rect(0,0,30,30,stroke="black",
        #                                stroke_width=".3",fill="none"))
        pattern.addElement(self.charge.finalizeSVG())
        pattern.addElement(charge2.finalizeSVG())
        blazon.Ordinary.defs.append(pattern)
        newelt=SVGdraw.group()
        elt=self.background.fill(elt)
        newelt.addElement(elt)
        newbase=SVGdraw.rect(x=-blazon.Ordinary.FESSPTX,
                             y=-blazon.Ordinary.FESSPTY,
                             width=blazon.Ordinary.WIDTH,
                             height=blazon.Ordinary.HEIGHT,
                             fill="url(#%s)"%pattern.attributes["id"])
        newelt.addElement(newbase)
        return newelt

class Estencelly(Semy):
    def __init__(self, background, color):
        self.background=background
        cg=blazon.ChargeGroup(3,blazon.Roundel(tincture=color))
        cg.arrangement=arrangement.ByNumbers([1,2])
        self.charge=blazon.BigRect()
        self.charge.addCharge(cg)
                           
# I wonder if this'll work...

class Countercharged(Treatment):
    def __init__(self):
        pass
    
    def fill(self,elt):
        realtincture=copy.copy(elt.charge.parent.tincture)
        realtincture.colors=(realtincture.colors[1],
                             realtincture.colors[0])
        elt=realtincture.fill(elt)
        return elt

class Paly(Treatment):
   def parseColors(self,color1,color2):
      """For internal use, to simplify subclasses"""
      if type(color1)==type("x"):
         color1=Treatment(color1)
      if type(color2)==type("x"):
         color2=Treatment(color2)
      self.colors=(color1,color2)

   def assemble(self):
      """For internal use, to simplify assembly of subclasses"""
      p=partLine(linetype=self.lineType) # Start to support partition lines
      width=float(blazon.Ordinary.WIDTH)/self.pieces
      for i in range(1,self.pieces-1,2):
         p.rect(-blazon.Ordinary.FESSPTX+i*width,-blazon.Ordinary.HEIGHT,
                width,2*blazon.Ordinary.HEIGHT)
      if not self.pieces%2:
          # Make the last one extra-big, so things don't show through
          # if the line-type isn't plain.
          p.rect(-blazon.Ordinary.FESSPTX+(self.pieces-1)*width,
                 -blazon.Ordinary.HEIGHT,
                 2*width,2*blazon.Ordinary.HEIGHT)
      self.path=SVGdraw.path(p)
      
   def __init__(self,bars=8,color1="argent",color2="sable",linetype="plain"):
      self.parseColors(color1,color2)
      self.lineType=linetype
      # Need to have a dummy color here so things don't wind up in the
      # colorless list. ref: "fountain"
      self.color="X"
      if bars:
          self.pieces=bars
      else:
          self.pieces=8
            
   def fill(self, elt,symbol=False):
      self.assemble()
      self.foreground=blazon.Ordinary()        # treat it like an blazon.Ordinary
      self.foreground.clipPath=self.path
      self.foreground.clipPathElt.addElement(self.path)
      self.foreground.tincture=self.colors[1]
      #self.background=SVGdraw.rect(-blazon.Ordinary.FESSPTX,
      #                             -blazon.Ordinary.FESSPTY,
      #                             blazon.Ordinary.WIDTH,
      #                             blazon.Ordinary.HEIGHT)
      #self.background=self.colors[0].fill(self.background)
      self.background=self.colors[0].fill(elt)
      if symbol:
          self.foreground.clipPathElt.addElement(SVGdraw.use(symbol))
      g=SVGdraw.group()
      g.addElement(self.background)
      g.addElement(self.foreground.finalizeSVG())
      return g

class Barry(Paly):
   def assemble(self):
      p=partLine(linetype=self.lineType)
      height=float(blazon.Ordinary.HEIGHT)/self.pieces
      # Problem.  Optical center is at 0.  Geometric center is a little lower,
      # owing to the placement of the coordinates.
      for i in range(1,self.pieces-1,2):
         p.rect(-blazon.Ordinary.WIDTH, -blazon.Ordinary.FESSPTY+i*height,
                3*blazon.Ordinary.WIDTH, height)
      # Last piece is extra-wide because everything is shifted up to correct
      # for optical center.  Only matters when pieces is even.
      # Also compensates for non-plain lines.
      if not self.pieces%2:
          p.rect(-blazon.Ordinary.WIDTH, -blazon.Ordinary.FESSPTY+(self.pieces-1)*height,
                 3*blazon.Ordinary.WIDTH, 3*height)
      self.path=SVGdraw.path(p)
      # Shift to bring center into place.
      self.path.attributes["transform"]=" translate(0,%.4f)"%\
                                         -(blazon.Ordinary.HEIGHT/2 - blazon.Ordinary.FESSPTY)

class Pily(Paly):
    def assemble(self):
        p=partLine(linetype=self.lineType)
        width=float(blazon.Ordinary.WIDTH)/self.pieces
        for i in range(0,self.pieces):
            p.move(-blazon.Ordinary.FESSPTX+i*width,-blazon.Ordinary.FESSPTY)
            p.makelinerel(width/2,blazon.Ordinary.HEIGHT)
            p.makelinerel(width/2,-blazon.Ordinary.HEIGHT)
            p.closepath()
        self.path=SVGdraw.path(p)

class BarryPily(Pily):
    # Same as above, but horizontal
    def assemble(self):
        p=partLine(linetype=self.lineType)
        height=float(blazon.Ordinary.HEIGHT)/self.pieces
        for i in range(0,self.pieces):
            p.move(-blazon.Ordinary.FESSPTX,-blazon.Ordinary.FESSPTY+i*height)
            p.makelinerel(blazon.Ordinary.WIDTH,height/2)
            p.makelinerel(-blazon.Ordinary.WIDTH,height/2)
            p.closepath()
        self.path=SVGdraw.path(p)

class BendyPily(Pily):
    # As above, but slantwise
    # Not a good Bendy Pily, but it's something.
    def assemble(self):
        p=partLine(linetype=self.lineType)
        breadth=math.sqrt(blazon.Ordinary.HEIGHT**2 +
                          blazon.Ordinary.WIDTH**2)
        unit=breadth/self.pieces
        for i in range(0,self.pieces):
            p.move(-breadth/2+i*unit, -breadth/2)
            p.makelinerel(unit/2, breadth)
            p.makelinerel(unit/2, -breadth)
            p.closepath()
        self.path=SVGdraw.path(p)
        self.path.attributes["transform"]=" rotate(45)"

class Bendy(Paly):
   def assemble(self):
      p=partLine(linetype=self.lineType)
      # OK, let's map things on the *square* HEIGHTxHEIGHT
      # Because HEIGHT > WIDTH!!!
      fullwidth=math.sqrt(2)*blazon.Ordinary.HEIGHT
      # Oh, this is going to be much easier to do orthogonally and rotating.
      if self.pieces>3:
          width=fullwidth*.87/self.pieces # Compensate for round corner.
      else:                             # Otherwise Per Bend doesn't work.
          width=fullwidth/self.pieces
      for i in range(0,self.pieces+2,2):
          p.rect(fullwidth/2-i*width, -blazon.Ordinary.HEIGHT,
                 width,2*blazon.Ordinary.HEIGHT)
      self.path=SVGdraw.path(p)
      self.path.attributes["transform"]="rotate(-45)"
      
class BendySinister(Paly):
   def assemble(self):
      # Can't really do this by rotating Bendy, since the round corner is
      # on the other side.
      p=partLine(linetype=self.lineType)
      fullwidth=math.sqrt(2)*blazon.Ordinary.HEIGHT
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

# I'm thinking the pattern for a PerPale shield should be the same as normal.

#    @staticmethod
#    def patternContents(num):
#        patterns=[[1],[1,(0,0)]]
#        try:
#            return patterns[num]
#        except IndexError:
#            pass
#        return blazon.Pale.patternSiblings(num)

class PerFesse(Barry):
    def __init__(self,*args,**kwargs):
        Barry.__init__(self,2,*args,**kwargs)

    @staticmethod
    def patternContents(num):
        patterns=[[1],[1,(0,0)]]
        try:
            return patterns[num]
        except IndexError:
            pass
        return blazon.Fesse.patternSiblings(num)

class PerBend(Bendy):
    def __init__(self,*args,**kwargs):
        Bendy.__init__(self,2,*args,**kwargs)

    @staticmethod
    def patternContents(num):
        patterns=[[1],[1,(0,0)]]
        try:
            return patterns[num]
        except IndexError:
            pass
        return blazon.Bend.patternSiblings(num)

class PerBendSinister(BendySinister):
    def __init__(self,*args,**kwargs):
        BendySinister.__init__(self,2,*args,**kwargs)

    @staticmethod
    def patternContents(num):
        patterns=[[1],[1,(0,0)]]
        try:
            return patterns[num]
        except IndexError:
            pass
        return blazon.BendSinister.patternSiblings(num)

class PerPall(Paly):
    def __init__(self,color1="argent",color2="sable",color3="gules",linetype="plain"):
        # Boy am I lazy
        self.parseColors(color1,color3)
        hold=self.colors[1]
        self.parseColors(color1,color2)
        self.colors=(self.colors[0],self.colors[1],hold)
        self.lineType=linetype
        self.inverted=False

    def assemble(self):
        p=partLine()
        p.lineType=self.lineType
        p.move(0,blazon.Ordinary.HEIGHT)
        p.makeline(0,0,align=1)
        p.makeline(-blazon.Ordinary.WIDTH, -blazon.Ordinary.WIDTH)
        p.vline(blazon.Ordinary.HEIGHT)
        p.closepath()
        self.path1=SVGdraw.path(p)
        p=partLine()
        p.lineType=self.lineType
        p.move(0,blazon.Ordinary.HEIGHT)
        p.makeline(0,0,align=1,shift=1)
        p.makeline(blazon.Ordinary.WIDTH, -blazon.Ordinary.WIDTH)
        p.vline(blazon.Ordinary.HEIGHT)
        p.closepath()
        self.path2=SVGdraw.path(p)
        if self.inverted:
            # Have to rearrange the colors too
            self.colors=(self.colors[2],self.colors[1],self.colors[0])
            self.path1.attributes["transform"]="rotate(180)"
            self.path2.attributes["transform"]="rotate(180)"

    def fill(self,elt):
        self.assemble()
        self.fg1=blazon.Ordinary()
        self.fg1.clipPath=self.path1
        self.fg1.clipPathElt.addElement(self.path1)
        self.fg1.tincture=self.colors[1]
        self.fg2=blazon.Ordinary()
        self.fg2.clipPath=self.path2
        self.fg2.clipPathElt.addElement(self.path2)
        self.fg2.tincture=self.colors[2]
        #self.bg=SVGdraw.rect(-blazon.Ordinary.FESSPTX,
        #                     -blazon.Ordinary.FESSPTY,
        #                     blazon.Ordinary.WIDTH,
        #                     blazon.Ordinary.HEIGHT)
        #self.bg=self.colors[0].fill(self.bg)
        self.bg=self.colors[0].fill(elt)
        g=SVGdraw.group()
        g.addElement(self.bg)
        g.addElement(self.fg1.finalizeSVG())
        g.addElement(self.fg2.finalizeSVG())
        return g

    def invert(self):
        self.inverted=True

    # Like PerChevron, we need a dummy object
    def patternContents(self,num):
        patterns=[[1],[1,(0,0)]]
        try:
            return patterns[num]
        except IndexError:
            pass
        tmp=blazon.Pall()
        tmp.inverted=self.inverted
        return tmp.patternSiblings(num)        

class PerCross(Paly):
   def __init__(self,color1="argent",color2="sable",linetype="plain"):
      # reverse order of colors  so I don't have to bother rewriting assemble()
      self.parseColors(color2,color1)
      self.lineType=linetype

   @staticmethod
   def patternContents(num):
       patterns=[[1],[1,(0,0)]]
       try:
           return patterns[num]
       except IndexError:
           pass
       return blazon.Cross.patternSiblings(num)        

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

   @staticmethod
   def patternContents(num):
       patterns=[[1],[1,(0,0)]]
       try:
           return patterns[num]
       except IndexError:
           pass
       return blazon.Saltire.patternSiblings(num)        


class Gyronny(Paly):
    def assemble(self):
        # Yes, everything with HEIGHT, so I'm working in a square.
        # May have the colors backwards.
        p=partLine(linetype=self.lineType)
        if self.pieces == 8:
            # No reason to do this as a special case, but it was working
            # first, so why mess with it.
            p.move(0,-blazon.Ordinary.HEIGHT)
            p.makeline(0,blazon.Ordinary.HEIGHT)
            p.hline(-blazon.Ordinary.HEIGHT)
            p.makeline(blazon.Ordinary.HEIGHT,-blazon.Ordinary.HEIGHT)
            p.closepath()
            p.move(-blazon.Ordinary.HEIGHT,0)
            p.makeline(blazon.Ordinary.HEIGHT,0)
            p.vline(blazon.Ordinary.HEIGHT)
            p.makeline(-blazon.Ordinary.HEIGHT,-blazon.Ordinary.HEIGHT)
            p.closepath()
        else:
            angle=2*math.pi/self.pieces
            pi_2=math.pi/2
            for i in range(0,self.pieces,2):
                p.move(blazon.Ordinary.HEIGHT*math.cos(pi_2+i*angle),
                       blazon.Ordinary.HEIGHT*math.sin(pi_2+i*angle))
                p.makeline(0,0)
                p.makeline(blazon.Ordinary.HEIGHT*math.cos(pi_2+(i+1)*angle),
                           blazon.Ordinary.HEIGHT*math.sin(pi_2+(i+1)*angle))
                p.closepath()
        self.path=SVGdraw.path(p)
        self.path.attributes["fill-rule"]="evenodd"

class PerChevron(Paly):
    def __init__(self,color1="argent", color2="sable", linetype="plain"):
        self.parseColors(color1,color2)
        self.lineType=linetype
        self.inverted=False

    # Can't make this static, because have to check for invertedness
    def patternContents(self,num):
        patterns=[[1],[1,(0,0)]]
        try:
            return patterns[num]
        except IndexError:
            pass
        tmp=blazon.Chevron()
        tmp.inverted=self.inverted
        return tmp.patternSiblings(num)
   
    def assemble(self):
        p=partLine(linetype=self.lineType)
        p.move(-blazon.Ordinary.FESSPTX,35)
        p.makeline(0,-5,1)
        p.makeline(blazon.Ordinary.FESSPTX,35,shift=-1)
        p.relvline(blazon.Ordinary.FESSPTY)
        p.relhline(-blazon.Ordinary.WIDTH)
        p.closepath()
        self.path=SVGdraw.path(p)
        if self.inverted:
            self.path.attributes["transform"]="rotate(180)"

    def invert(self):
        self.inverted=True
        # ALSO!  Have to reverse the orders of the colors, so the correct
        # one remains on top.
        self.colors=(self.colors[1], self.colors[0])

       
class Chevronny(Paly):
    def assemble(self):
        p=partLine(linetype=self.lineType)
        height=float(blazon.Ordinary.HEIGHT)/self.pieces
        #"Chevronny of n" doesn't make all that much sense anyway.
        for i in range(0,self.pieces+2,2):
            p.move(-blazon.Ordinary.FESSPTX,
                   blazon.Ordinary.FESSPTY-(i-2)*height)
            p.makelinerel(blazon.Ordinary.FESSPTX,-25,align=1)
            p.makelinerel(blazon.Ordinary.FESSPTX,25)
            p.relvline(-height)
            p.makelinerel(-blazon.Ordinary.FESSPTX,-25,align=1)
            p.makelinerel(-blazon.Ordinary.FESSPTX,25)
            p.closepath()
        self.path=SVGdraw.path(p)
        if (self.inverted):
            self.path.attributes['transform']=" rotate(180)"

    def __init__(self, bars=8, color1="argent", color2="sable", linetype="plain", inverted=False):
        self.parseColors(color1, color2)
        self.lineType=linetype
        self.pieces=bars
        self.inverted=inverted

# Barry-bendy and paly-bendy are easy now: just do:
# paly of 8 barry of 8 or and sable and barry of 8 sable and or
# except we'll want to adjust the quantities because the shield is longer
# than it is wide.

# Ditto checky/chequy, lozengy, etc.
