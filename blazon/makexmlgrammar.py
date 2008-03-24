import plyyacc
import sys

def make_xml_grammar(all=dir(plyyacc)):
    # OUTPUT another Python program that recreates this one's grammar, by
    # copying the function names and __doc__ strings.  The functions just
    # build an XML doc of the parse tree.
    all=filter((lambda x: x[0:2] == 'p_'), all)
    print """
import sys
import ply.yacc as yacc
import copy
from xml.dom.minidom import parse, parseString, getDOMImplementation
from blazon import Blazon

# For bizarre reasons I don't fully understand, you can't import tokens
# from plylex, but it's okay if you make fakeplylex.py a symlink to plylex.

from fakeplylex import tokens,lookup

impl=getDOMImplementation()
doc=impl.createDocument(None,"shield",None)
docelt=doc.documentElement

start="blazon"

"""
    for f in all:
        indent=0
        d=getattr(plyyacc,f).__doc__
        if not d:
            continue
        nt=d.split(':')[0]
        if nt:
            nt=nt.strip()
        if nt=="empty":
            print '''
def p_empty(p):
    "empty : "
    p[0]=None   # doc.createElement('empty')


'''
            continue
        print '''
def %(f)s(p):
    """%(d)s"""
    rv=doc.createElement('%(nt)s')
    for i in range(1,len(p)):
       e=p[i]
       if isinstance(e,int):
           e=str(e)
       if isinstance(e,str):
          elt=doc.createElement(str(p.slice[i].type))
          elt.setAttribute("value", e)
       else:
          elt=e
       if elt:
           rv.appendChild(elt)
    if any(p):
        p[0]=rv
    else:
        p[0]=None

''' % {'f':f, 'd':d, 'nt':nt}

    print """
yacc.yacc(method="LALR")
if __name__=="__main__":
    j=yacc.parse(Blazon.Normalize(" ".join(sys.argv[1:])))
    print j.toprettyxml()
"""
make_xml_grammar()
