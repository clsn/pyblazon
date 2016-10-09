#!/usr/bin/python

import SVGdraw

class ExternalSVG(SVGdraw.SVGelement):
    def __init__(self,filename,type='',attributes=None,elements=None,text='',namespace='',cdata=None,**args):
        f = open(filename)
        self.xmldata = []
        for line in f:
            self.xmldata.append(line)
        # super(ExternalSVG, self).__init__(type, attributes,elements,text,namespace,cdata,**args)
        SVGdraw.SVGelement.__init__(self,type,attributes,elements,text,namespace,cdata,**args)
    def toXml(self, level, f):
        # "level" refers to how deeply recursed we are. Since we
        # just have to blat out our contents, we can safely ignore it.
        for line in self.xmldata:
            f.write(line)

if __name__ == '__main__':
    import sys
    foo = ExternalSVG("data/Fleur.svg")
    print(foo.toXml(0, sys.stdout))
