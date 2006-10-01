import math
import sys

# Bleah, I think I need to rewrite the pathdata class completely; it's not
# smart enough for me.
class partLine:
    # Copied from SVGdraw, to be overwritten...
    """class used to create a pathdata object which can be used for a path.
    although most methods are pretty straightforward it might be useful to look at the SVG specification."""
    #I didn't test the methods below. 
    def __init__(self,x=None,y=None,linetype="plain"):
        self.path=[]
        if x is not None and y is not None:
            self.path.append('M '+str(x)+' '+str(y))
            self.curX=x
            self.curY=y
        self.lineType=linetype
    def update(self,x,y):
        """Internal function only!!"""
        (self.curX,self.curY)=(x,y)
    def relupdate(self,x,y):
        """Internal function only!!"""
        self.curX += x
        self.curY += y
    def closepath(self):
        """ends the path"""
        self.path.append('z')
    def move(self,x,y):
        """move to absolute"""
        self.path.append('M '+str(x)+' '+str(y))
        self.update(x,y)
    def relmove(self,x,y):
        """move to relative"""
        self.path.append('m '+str(x)+' '+str(y))
        self.relupdate(x,y)
    def line(self,x,y):
        """line to absolute"""
        self.path.append('L '+str(x)+' '+str(y))
        self.update(x,y)
    def relline(self,x,y):
        """line to relative"""
        self.path.append('l '+str(x)+' '+str(y))
        self.relupdate(x,y)
    def hline(self,x):
        """horizontal line to absolute"""
        self.path.append('H'+str(x))
        self.update(x,self.curY)
    def relhline(self,x):
        """horizontal line to relative"""
        self.path.append('h'+str(x))
        self.relupdate(x,0)
    def vline(self,y):
        """verical line to absolute"""
        self.path.append('V'+str(y))
        self.update(self.curX,y)
    def relvline(self,y):
        """vertical line to relative"""
        self.path.append('v'+str(y))
        self.relupdate(0,y)
    def bezier(self,x1,y1,x2,y2,x,y):
        """bezier with xy1 and xy2 to xy absolut"""
        self.path.append('C'+str(x1)+','+str(y1)+' '+str(x2)+','+str(y2)+' '+str(x)+','+str(y))
        self.update(x,y)
    def relbezier(self,x1,y1,x2,y2,x,y):
        """bezier with xy1 and xy2 to xy relative"""
        self.path.append('c'+str(x1)+','+str(y1)+' '+str(x2)+','+str(y2)+' '+str(x)+','+str(y))
        self.relupdate(x,y)
    def smbezier(self,x2,y2,x,y):
        """smooth bezier with xy2 to xy absolut"""
        self.path.append('S'+str(x2)+','+str(y2)+' '+str(x)+','+str(y))
        self.update(x,y)
    def relsmbezier(self,x2,y2,x,y):
        """smooth bezier with xy2 to xy relative"""
        self.path.append('s'+str(x2)+','+str(y2)+' '+str(x)+','+str(y))
        self.relupdate(x,y)
    def qbezier(self,x1,y1,x,y):
        """quadratic bezier with xy1 to xy absolut"""
        self.path.append('Q'+str(x1)+','+str(y1)+' '+str(x)+','+str(y))
        self.update(x,y)
    def relqbezier(self,x1,y1,x,y):
        """quadratic bezier with xy1 to xy relative"""
        self.path.append('q'+str(x1)+','+str(y1)+' '+str(x)+','+str(y))
        self.relupdate(x,y)
    def smqbezier(self,x,y):
        """smooth quadratic bezier to xy absolut"""
        self.path.append('T'+str(x)+','+str(y))
        self.update(x,y)
    def relsmqbezier(self,x,y):
        """smooth quadratic bezier to xy relative"""
        self.path.append('t'+str(x)+','+str(y))
        self.relupdate(x,y)
    def ellarc(self,rx,ry,xrot,laf,sf,x,y):
        """elliptival arc with rx and ry rotating with xrot using large-arc-flag and sweep-flag  to xy absolut"""
        self.path.append('A'+str(rx)+','+str(ry)+' '+str(xrot)+' '+str(laf)+' '+str(sf)+' '+str(x)+' '+str(y))
        self.update(x,y)
    def relellarc(self,rx,ry,xrot,laf,sf,x,y):
        """elliptival arc with rx and ry rotating with xrot using large-arc-flag and sweep-flag  to xy relative"""
        self.path.append('a'+str(rx)+','+str(ry)+' '+str(xrot)+' '+str(laf)+' '+str(sf)+' '+str(x)+' '+str(y))
        self.relupdate(x,y)
    def __repr__(self):
        return ' '.join(self.path)
    
    def makeline(self,x,y,align=0):
        """draw a line using whatever linetype is called for"""
        # TODO: add parameter "align": if align is 0 (default), then put
        # the leftover part (that doesn't make up a complete oscillation)
        # at the other end.  If it's 1, put it on the near end.  This will
        # be easier to do when the whole functioning of this method is made
        # neater.

        if not hasattr(self,"lineType") or self.lineType == "plain":
            self.line(x,y)
        else:
            # Calculate the direct line and offset vector here.
            angle=math.atan2(y-self.curY,x-self.curX)
            leng=math.sqrt((x-self.curX)**2+(y-self.curY)**2)
            # Can I factor all the work out into a big dictionary and get
            # rid of redundant code?
            # Maybe a dictionary referring to objects with drawing
            # functions on them...
            # There has to be a neater way to do this.
            if self.lineType == "indented" or self.lineType=="dancetty" or self.lineType == "wavy":
                if self.lineType=="indented":
                    wavelength=2
                    amplitude=1
                else:
                    wavelength=8
                    amplitude=5
                # NOTE: del[XY] and shift[XY] were ints, but that didn't work
                # with some lines (notably the pile).  I've de-inted them for
                # now, leaving the parens.  May want to re-int them, after
                # significantly upping the resolution of the integer grid.
                delX=(wavelength*math.cos(angle))
                delY=(wavelength*math.sin(angle))
                # sys.stderr.write("delX: %d, delY: %d\n" % (delX, delY))
                (uptoX,uptoY)=(self.curX,self.curY)
                direction=1
                (shiftX,shiftY)=((amplitude*math.cos(angle+math.pi/2)),
                                 (amplitude*math.sin(angle+math.pi/2)))
                # sys.stderr.write("shiftX: %d, shiftY: %d\n"%(shiftX,shiftY))
                for i in range(1,int(leng/wavelength)):
                    uptoX+=delX
                    uptoY+=delY
                    if self.lineType == "wavy":
                        self.path.append(" Q%.3f,%.3f %.3f,%.3f"%
                                         (uptoX-delX/2+shiftX*direction,
                                          uptoY-delY/2+shiftY*direction,
                                          uptoX,uptoY))
                    else:
                        self.path.append(" L"+str(uptoX+shiftX*direction)+
                                         ","+str(uptoY+shiftY*direction))
                    direction *= -1
                if self.lineType=="wavy":
                    self.path.append(" T%d,%d"%(x,y))
                else:
                    self.path.append(" L"+str(x)+","+str(y))
            elif self.lineType == "embattled":
                # I'm going to assume equal up/down lengths
                wavelength=6
                amplitude=2
                delX=(wavelength*math.cos(angle))
                delY=(wavelength*math.sin(angle))
                (uptoX,uptoY)=(self.curX, self.curY)
                direction=1
                (shiftX,shiftY)=((amplitude*math.cos(angle+math.pi/2)),
                                 (amplitude*math.sin(angle+math.pi/2)))
                for i in range(1,int(leng/wavelength)):
                    self.path.append(" L"+str(uptoX+shiftX*direction)+
                                     ","+str(uptoY+shiftY*direction))
                    uptoX+=delX
                    uptoY+=delY
                    self.path.append(" L"+str(uptoX+shiftX*direction)+
                                     ","+str(uptoY+shiftY*direction))
                    direction *= -1
                self.path.append(" L"+str(x)+","+str(y))
            elif self.lineType == "invected" or self.lineType == "engrailed":
                if self.lineType=="invected":
                    # I'm pretty sure this isn't correct in the general case.
                    sweep=1
                else:
                    sweep=0
                wavelength=10
                amplitude=5
                delX=(wavelength*math.cos(angle))
                delY=(wavelength*math.sin(angle))
                (uptoX,uptoY)=(self.curX,self.curY)
                #(shiftX,shiftY)=((amplitude*math.cos(angle+math.pi/2)),
                #                 (amplitude*math.sin(angle+math.pi/2)))
                for i in range(0,int(leng/wavelength)):
                    uptoX+=delX
                    uptoY+=delY
                    self.path.append(" A%f,%f 0 1 %d %f,%f"%
                                     (amplitude,amplitude,sweep,uptoX,uptoY))
                self.path.append(" A%f,%f 0 1 %d %f,%f"%
                                 (amplitude, amplitude,sweep,x,y))
            else:
                self.line(x,y)
            self.update(x,y)

    def makelinerel(self,x,y):
        """draw a line with the current linetype to xy relative"""
        self.makeline(x+self.curX,y+self.curY)

    def rect(self,x,y,width,height):
        """draw a rectangle using the current linetype"""
        self.move(x,y)
        self.makelinerel(width,0)
        self.makelinerel(0,height)
        self.makelinerel(-width,0)
        self.makelinerel(0,-height)
        self.closepath()
