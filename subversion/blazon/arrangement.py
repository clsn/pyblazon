#!/usr/bin/python

from blazon import *

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
         raise ArrangementException, \
               "Don't know how to arrange " + \
               str(num) + " charges " + self.__class__.__name__

class InPale(Arrangement):
   # Doesn't need to scale quite as much as the patternContents of Pale.
   patterns=[[1],[1,(0,0)],
             [.4,(0,-25),(0,25)],
             [.4,(0,-33),(0,0),(0,33)]
             ]

class InFesse(Arrangement):
   patterns=[[1],[1,(0,0)],
             [.4,(-22,0),(22,0)],
             [.4,(-32,0),(0,0),(32,0)]
             ]

class InBend(Arrangement):
   patterns=[[1],[1,(0,0)],
             [.5,(-20,-20),(18,18)],
             [.4,(-30,-30),(21,21),(-4,-4)],
             [.3,(-30,-30),(-12,-12),(8,8),(26,26)]
             ]

class InBendSinister(InBend):
   def pattern(self,num):
      rv=Arrangement.pattern(self,num)
      if rv:
         for i in range(1,len(rv)):
            rv[i]=(-rv[i][0],rv[i][1])
      return rv

class ByNumbers(Arrangement):
   def __init__(self,rows=None):
      self.rows=rows
   
   def setRows(self,rows):
      self.rows=rows                    # Let it be a list of numbers, top down.

   def pattern(self,num):
      # Barf if not set right
      if not self.rows:
         return None
      # num should equal the sum of the elements of the rows list.
      # We're going to assume it does.
      if sum(self.rows) <> num:
         sys.stderr.write("Whoa!  Number of elements is %d, but rows for %d given.\n"%
                          (num,sum(self.rows)))
         # Then go on and do it anyway.
      # Determine the scale by the larger of: the number of rows, and
      # the largest number of elements in a row.
      index=max(len(self.rows),max(self.rows))
      scale=[1, 1, .4, .3, .25, .2, .2][index]
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
