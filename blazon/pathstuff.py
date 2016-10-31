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
        """vertical line to absolute"""
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

    # Table of linetype, wavelength, and amplitude (for now)
    lineInfo={
        "indented": (4,2),
        "dancetty": (8,5),
        "rayonny": (2,6),
        "wavy": (8,5),
        "embattled": (6,2),
        "dovetailed": (6,2),
        "nebuly": (6,4),
        "urdy": (6,6),
        "raguly": (6,3),
        "engrailed": (10,5),
        "invected": (10,5),
        "potenty": (2,6),
        }
    def makeline(self,x,y,align=0,shift=1,*args,**kwargs):
        """draw a line using whatever linetype is called for"""        
        # If align is False (default), then put the leftover part (that
        # doesn't make up a complete oscillation) at the other end.  If
        # it's True, put it on the near end.  This will be easier to do
        # when the whole functioning of this method is made neater.

        if not hasattr(self,"lineType") or not self.lineType or self.lineType == "plain":
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
            try:
                (wavelength,amplitude)=partLine.lineInfo[self.lineType]
            except KeyError:
                # Probably the wrong way to handle this error, but okay for now.
                (wavelength,amplitude)=(6,6)
            # NOTE: del[XY] and shift[XY] were ints, but that didn't work
            # with some lines (notably the pile).  I've de-inted them for
            # now, leaving the parens.  May want to re-int them, after
            # significantly upping the resolution of the integer grid.
            delX=(wavelength*math.cos(angle))
            delY=(wavelength*math.sin(angle))
            # sys.stderr.write("delX: %d, delY: %d\n" % (delX, delY))
            (uptoX,uptoY)=(self.curX,self.curY)
            # WRONG: need to account for waviness
            if align:
                rem=leng%wavelength
                (remX,remY)=(rem*math.cos(angle),
                             rem*math.sin(angle))
                self.path.append(" L%.4f,%.4f"%
                                 (uptoX+remX,uptoY+remY))
                uptoX+=remX
                uptoY+=remY
            if int(leng/wavelength)%2:
                direction= shift
            else:
                direction= -shift
            (shiftX,shiftY)=((amplitude*math.cos(angle+math.pi/2)),
                             (amplitude*math.sin(angle+math.pi/2)))
            # sys.stderr.write("shiftX: %d, shiftY: %d\n"%(shiftX,shiftY))
            if self.lineType in ["indented","dancetty","wavy"]:
                for i in range(1,int(leng/wavelength)+1):
                    uptoX+=delX
                    uptoY+=delY
                    if self.lineType == "wavy":
                        self.path.append(" Q%.3f,%.3f %.3f,%.3f"%
                                         (uptoX-delX/2+shiftX*direction,
                                          uptoY-delY/2+shiftY*direction,
                                          uptoX,uptoY))
                    else:
                        self.path.append(" L%.3f,%.3f L%.3f,%.3f"%
                                         (uptoX-delX/2+shiftX*direction,
                                          uptoY-delY/2+shiftY*direction,
                                          uptoX,uptoY))
                    direction *= -1
                if self.lineType=="wavy":
                    self.path.append(" T%d,%d"%(x,y))
                else:
                    self.path.append(" L"+str(x)+","+str(y))
            elif self.lineType == "embattled":
                # I'm going to assume equal up/down lengths
                for i in range(1,int(leng/wavelength)+1):
                    self.path.append(" L"+str(uptoX+shiftX*direction)+
                                     ","+str(uptoY+shiftY*direction))
                    uptoX+=delX
                    uptoY+=delY
                    self.path.append(" L"+str(uptoX+shiftX*direction)+
                                     ","+str(uptoY+shiftY*direction))
                    direction *= -1
                self.path.append(" L"+str(x)+","+str(y))
            elif self.lineType == "raguly":
                for i in range(1,int(leng/wavelength)+1):
                    # up and over.  Use relative paths.
                    self.path.append(" l%f,%f"%(direction*(shiftX+delX/3),
                                                direction*(shiftY+delY/3)))
                    uptoX+=delX
                    uptoY+=delY
                    self.path.append(" l%f,%f"%(delX,delY))
                    direction *= -1
                self.path.append(" L"+str(x)+","+str(y))
            elif self.lineType == "dovetailed":
                for i in range(1,int(leng/wavelength)+1):
                    self.path.append(" L%f,%f"%(uptoX+direction*shiftX-delX/3,
                                                uptoY+direction*shiftY-delY/3))
                    self.path.append(" L%f,%f"%(uptoX+delX+direction*shiftX,
                                                uptoY+delY+direction*shiftY))
                    uptoX+=delX
                    uptoY+=delY
                    direction *= -1
                self.path.append(" L%f,%f"%(x,y))
            elif self.lineType == "nebuly":
                for i in range(1,int(leng/wavelength)+1):
                    self.path.append(" Q%f,%f %f,%f Q%f,%f %f,%f"%
                                     (uptoX+direction*shiftX-.8*delX,
                                      uptoY+direction*shiftY-.8*delY,
                                      uptoX+direction*shiftX+delX/2,
                                      uptoY+direction*shiftY+delY/2,
                                      uptoX+direction*shiftX+1.8*delX,
                                      uptoY+direction*shiftY+1.8*delY,
                                      uptoX+delX,uptoY+delY))
                    uptoX+=delX
                    uptoY+=delY
                    direction *= -1
                self.path.append(" L%f,%f"%(x,y))
            elif self.lineType == "urdy" or self.lineType == "champaine":
                for i in range(1,int(leng/wavelength)+1):
                    self.path.append("L%f,%f l%f,%f l%f,%f l%f,%f"%
                                     (uptoX,uptoY,
                                      direction*shiftX/2,
                                      direction*shiftY/2,
                                      direction*shiftX/2+delX/2,
                                      direction*shiftY/2+delY/2,
                                      -direction*shiftX/2+delX/2,
                                      -direction*shiftY/2+delY/2))
                    uptoX+=delX
                    uptoY+=delY
                    direction *= -1
            elif self.lineType == "invected" or self.lineType == "engrailed":
                if self.lineType=="invected":
                    # I'm pretty sure this isn't correct in the general case.
                    sweep=1
                    # Shifting them over like this keeps the lines from
                    # being too wide or narrow.
                    uptoX+=shiftX
                    uptoY+=shiftY
                else:
                    sweep=0
                    uptoX-=shiftX
                    uptoY-=shiftY
                for i in range(0,int(leng/wavelength)-1):
                    uptoX+=delX
                    uptoY+=delY
                    self.path.append(" A%f,%f 0 1 %d %f,%f"%
                                     (amplitude,amplitude,sweep,uptoX,uptoY))
                self.path.append(" A%f,%f 0 1 %d %f,%f"%
                                 (amplitude, amplitude,sweep,x,y))
                
            elif self.lineType == "rayonny":
                for i in range(0,int(leng/wavelength)):
                    self.path.append("l%.4f,%.4f %.4f,%.4f %.4f,%.4f "%
                                     (delX/4+shiftX/2*direction,
                                      delY/4+shiftY/2*direction,
                                      -delX/4+shiftX/2*direction,
                                      -delY/4+shiftY/2*direction,
                                      delX-shiftX*direction,
                                      delY-shiftY*direction,))
                    uptoX+=delX
                    uptoY+=delY
                    direction*= -1
                self.path.append(" L%.4f,%.4f"%(x,y))
            elif self.lineType == 'potenty':
                direction = -1  # potenty is special...
                # Shift to keep the midpoint on the line...
                self.path.append(" l %f %f "%(-direction*shiftX/2,
                                              -direction*shiftY/2))
                uptoX += -direction*shiftX/2
                uptoY += -direction*shiftY/2
                # Wavelength means something slightly different,
                for i in range(0, int(leng/wavelength/2)):
                    self.path.append("l%f,%f %f,%f %f,%f %f,%f "%
                                     (direction*shiftX/3, direction*shiftY/3,
                                      -delX*1, -delY*1,
                                      direction*shiftX/3, direction*shiftY/3,
                                      delX*3, delY*3,))
                    uptoX+=delX
                    uptoY+=delY
                    direction*=-1
                self.path.append(" L%f,%f"%(x,y))
            else:                       # Just pretend it's plain.
                self.line(x,y)
            self.update(x,y)

    def makelinerel(self,x,y,align=0,shift=1):
        """draw a line with the current linetype to xy relative"""
        self.makeline(x+self.curX,y+self.curY,align=align,shift=shift)

    def rect(self,x,y,width,height):
        """draw a rectangle using the current linetype"""
        self.move(x,y)
        self.makelinerel(width,0)
        self.makelinerel(0,height)
        self.makelinerel(-width,0,1,-1)
        self.makelinerel(0,-height,1,-1)
        self.closepath()
