#!/usr/bin/python

from blazon import *
import blazon

import math
import sys

class Arrangement:
   """
   An object that specifies how the charges in a group are to be arranged.
   This is for use with things like "in pale" and "in bend", overriding the
   default patterning of ChargeGroups and such.  Maybe it could be used
   to take over that job, moving the methods out of Ordinary and Treatment?
   """
   # These are the default placements.  Subclasses will override, right?
   
   placements=[[1],[1,(0,0)],    # 0 charges, 1 charge ...
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

   def pattern(self,num):               # This is it?
      if len(self.__class__.patterns) - 1 >= num:
         return self.__class__.patterns[num]
      else: # Can't arrange that many charges.
         raise blazon.ArrangementError, \
               "Don't know how to arrange " + \
               str(num) + " charges " + self.__class__.__name__

class InPale(Arrangement):
   # Doesn't need to scale quite as much as the patternContents of Pale.
   patterns=[[1],[1,(0,0)],
             [.4,(0,-25),(0,25)],
             [.4,(0,-33),(0,0),(0,33)],
             [.3,(0,-36),(0,-12),(0,12),(0,36)],
             [.2,(0,-40),(0,-20),(0,0),(0,20),(0,40)]
             ]

class InFesse(Arrangement):
   patterns=[[1],[1,(0,0)],
             [.4,(-22,0),(22,0)],
             [.4,(-32,0),(0,0),(32,0)],
             [.3,(-36,0),(-12,0),(12,0),(36,0)],
             [.2,(-40,0),(-20,0),(0,0),(20,0),(40,0)]
             ]

class InBend(Arrangement):
   patterns=[[1],[1,(0,0)],
             [.5,(-20,-20),(18,18)],
             [.4,(-29,-29),(21,21),(-4,-4)],
             [.3,(-34,-34),(-14,-14),(6,6),(26,26)]
             ]

class InCross(Arrangement):
   # It only makes sense for 4 or more items in cross, really.
   # Ought to be able to infer this from InFesse and InPale.

   def pattern(self,num):
      if num < 4:
         return InFesse.patterns[num]
      # If the number is not congruent to zero or one modulo four,
      # we can't do anything anyway.
      if num%4 > 1:
         raise blazon.ArrangementError, "Can't arrange %d things in cross"%num
      # When num is 4, we can get away with this.  Otherwise we have to
      # leave the center blank:
      if num==4:
         return InFesse.patterns[2]+InPale.patterns[2][1:]
      half=num/2+1                      # center blank.
      rv=InFesse.patterns[half]+InPale.patterns[half][1:]
      # Remove all (<=2) the (0,0) elements, and put one back if needed.
      try:
         rv.remove((0,0))
         rv.remove((0,0))
      except ValueError:
         pass
      if num%4:
         rv+=[(0,0)]
      return rv

class InBendSinister(InBend):
   def pattern(self,num):
      # Have to copy this or else if there's more than one it gets unreversed!
      rv=copy.deepcopy(Arrangement.pattern(self,num))
      if rv:
         for i in range(1,len(rv)):
            rv[i]=(-rv[i][0],rv[i][1])
      return rv

class InChief(Arrangement):
   def __init__(self,side=None):
      self.side=side

   def shiftover(self,arr):
      mindist=10000
      # Wonder if I need to do something less clever.
      # They're going to be in order and all horizontal anyway.
      for i in range(1,len(arr)):
         c=arr[i]
         arr[i]=((c[0]+blazon.Ordinary.FESSPTX)/2.0-blazon.Ordinary.FESSPTX,
                 c[1])
         if self.side=="sinister":
            arr[i]=(arr[i][0]+blazon.Ordinary.FESSPTX,arr[i][1])
         if i==1:
            mindist=abs(arr[i][0] - blazon.Ordinary.FESSPTX)
         elif abs(arr[i][0]-arr[i-1][0])<mindist:
            mindist=abs(arr[i][0]-arr[i-1][0])
      if mindist<80*arr[0]:
         arr[0]=mindist/80.0
      return arr
         
   def pattern(self,num):
      arr=blazon.Chief.patternContents(num)
      # That's ordered around the origin, since chiefs get translated
      for i in range(1,len(arr)):
         c=arr[i]
         arr[i]=(c[0],c[1]-36)
      if self.side:
         arr=self.shiftover(arr)
      return arr

class InBase(InChief):
   def pattern(self,num):
      arr=blazon.Base.patternContents(num)
      if self.side:
         # Darn.  I can't just use InChief's shiftover, because the
         # shield is narrower down here.
         # Maybe I can use it and twiddle it some...
         arr=self.shiftover(arr)
         for i in range(1,len(arr)):
            if self.side=="sinister":
               arr[i]=(arr[i][0]-12,arr[i][1])
            else:
               arr[i]=(arr[i][0]+12,arr[i][1])
            # And reduce the scale
         arr[0]*=.6
      # Probably won't work well for most numbers, but it's unlikely that
      # num > 1 anyway.
      return arr

class InOrle(Arrangement):
   def pattern(self,num):
      return blazon.Bordure.patternContents(num)

class ByNumbers(Arrangement):
   def __init__(self,rows=None):
      self.rows=rows
   
   def setRows(self,rows):
      self.rows=rows                    # Let it be a list of numbers, top down.

   def pattern(self,num):
      # Barf if not set right
      if not self.rows:
         raise blazon.ArrangementError, "Tried to arrange something by numbers, but number of rows is not specified."
      # num should equal the sum of the elements of the rows list.
      if sum(self.rows) <> num:
         raise blazon.ArrangementError, "Whoa!  Number of elements is %d, but rows for %d given.\n"% (num,sum(self.rows))
      # Determine the scale by the larger of: the number of rows, and
      # the largest number of elements in a row.
      index=max(len(self.rows),max(self.rows))
      scale=[1, 1, .4, .3, .25, .2, .2, .2, .15, .15, .15, .1, .1, .1][index]
      # Assemble the return value...
      rv=[scale]
      totalrows=len(self.rows)
      for i in range(0,totalrows):
         row=self.rows[i]
         y=(-(totalrows-1)/2.0+i)*blazon.Ordinary.HEIGHT*.8*scale
         for j in range(0,row):
            x=((row-1)/2.0-j)*blazon.Ordinary.WIDTH*.8*scale
            rv.append((x,y))
      return rv
