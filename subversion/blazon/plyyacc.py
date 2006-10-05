#!/usr/bin/python

import blazon
import sys
import yacc
import tinctures
import copy

from plylex import tokens,lookup

class Globals:
    colorless=[]
    colors=[]
    shield=None

def p_blazon_1(p):
    'blazon : treatment'
    shield=blazon.Field()
    shield.tincture=p[1]
    Globals.shield=shield
    p[0]=shield
    return shield

def p_blazon_2(p):
    "blazon : treatment charges chief"
    shield=blazon.Field()
    shield.tincture=p[1]
    shield.extendCharges(p[2])
    if p[3]:
        shield.addChief(p[3])
    p[0]=shield
    Globals.shield=shield
    return shield

def p_treatment_1(p):
    "treatment : COLOR"
    p[0]=tinctures.Tincture(p[1])
    Globals.colors.append(p[0])

def p_treatment_2(p):
    "treatment : PARTYPER ORDINARY optlinetype treatment AND treatment"
    p[0]=lookup("per "+p[2])(p[4],p[6],linetype=p[3])

def p_treatment_3(p):
    "treatment : LINEY optlinetype optamt treatment AND treatment"
    p[0]=lookup(p[1])(p[3],p[4],p[6],linetype=p[2])

def p_treatment_4(p):
    """treatment : FUR
                 | COUNTERCHARGED"""
    p[0]=lookup(p[1])()

def p_treatment_5(p):
    "treatment : FURRY treatment AND treatment"
    p[0]=lookup(p[1])(p[2],p[4])

def p_treatment_6(p):
    "treatment : treatment ALTERED treatment"
    p[0]=lookup(p[2])(p[1],p[3])

def p_treatment_7(p):
    "treatment : QUARTERLY treatment AND treatment"
    p[0]=lookup(p[1])(p[2],p[4])

def p_treatment_8(p):
    "treatment : OF THE CARDINAL"
    # Not sure we can assume field is in colors[0], but maybe okay.
    d={"field":1, "first":1, "second":2, "third":3, "fourth":4, "fifth":5,
       "sixth":6, "seventh":7, "eighth":8, "ninth":9, "tenth":10}
    n=d[p[3]]
    p[0]=Globals.colors[n-1]

def p_treatment_9(p):
    """treatment : COLOR SEMY OF charge
                 | COLOR SEMYDELIS treatment"""
    if len(p)==5:
        p[0]=tinctures.Semy(tinctures.Tincture(p[1]),p[4])
    else:
        f=blazon.ExtCharge("fleur")
        f.tincture=p[3]
        p[0]=tinctures.Semy(tinctures.Tincture(p[1]),f)

def p_opttreatment(p):
    """opttreatment : treatment
                    | empty"""
    p[0]=p[1]
    if p[1]:
        for obj in Globals.colorless:
            obj.tincture=p[1]
        Globals.colorless=[]

def p_optlinetype(p):
    """optlinetype : LINETYPE
                   | empty"""
    p[0]=p[1]

def p_charges(p):
    """charges : grouporcharge
               | charges optand grouporcharge"""
    if len(p)==2:
        p[0]=[p[1]]
    else:
        p[0]=p[1]+[p[3]]

def p_grouporcharge(p):
    """grouporcharge : group
                     | charge"""
    p[0]=p[1]

def p_group(p):
    """group : amount charge
             | amount charge EACH CHARGED WITH charges"""
    p[0]=blazon.ChargeGroup(p[1],p[2])
    if len(p)>3:
        for elt in p[0].charges:
            elt.extendCharges(copy.deepcopy(p[6]))

def p_ordinary(p):
    """ordinary : ORDINARY
                | CHIEF
                | CHARGE"""
    p[0]=lookup(p[1])()

def p_charge_1(p):
    "charge : optA ordinary optinverted optlinetype opttreatment optfimbriation"
    res=p[2]
    p[3](res)
    res.lineType=p[4]
    if not p[5]:
        Globals.colorless.append(res)
    else:
        res.tincture=p[5]
    p[6](res)
    p[0]=res

def p_charge_2(p):
    "charge : ON A charge optA grouporcharge"
    p[3].addCharge(p[5])
    p[0]=p[3]

def p_chief(p):
    """chief : empty
             | optand A CHIEF optlinetype opttreatment
             | optand ON A CHIEF optlinetype opttreatment charges"""
    if len(p)<=2:
        p[0]=None
    elif len(p)==6:
        p[0]=blazon.Chief()
        if not p[5]:
            Globals.colorless.append(p[0])
        else:
            # sys.stderr.write("Coloring a chief: (%s)\n"%p[5])
            p[0].tincture=p[5]
        p[0].lineType=p[4]
    elif len(p)==8:
        p[0]=blazon.Chief()
        if not p[6]:
            Globals.colorless.append(p[0])
        else:
            p[0].tincture=p[6]
        p[0].extendCharges(p[7])
        p[0].lineType=p[5]
    else:
        # Drop back ten and punt
        p[0]=None
    
def p_amount(p):
    """amount : NUM
              | NUMWORD"""
    p[0]=p[1]

def p_optamt(p):
    """optamt : OF amount
              | empty"""
    if len(p) == 3:
        p[0]=p[2]
    else:
        p[0]=8

def p_optinverted(p):
    """optinverted : INVERTED
                   | empty"""
    if p[1]=="inverted":
        p[0]=lambda x:x.invert()
    else:
        p[0]=lambda x:x
        
def p_optfimbriation(p):
    """optfimbriation : FIMBRIATED COLOR
                      | empty"""
    if len(p)<=2:
        p[0]=lambda x:x
    else:
        col=p[2]
        p[0]=lambda x:x.fimbriate(col)

def p_optand(p):
    """optand : AND
              | empty"""
    pass

def p_optA(p):
    """optA : A
            | empty"""
    pass

def p_empty(p):
    "empty :"
    pass

def p_error(p):
    ""
    pass

yacc.yacc(method="LALR")

if __name__=="__main__":
#    line=sys.stdin.readline()
#    while line:
#        sh=yacc.parse(line)
#        print sh
#        line=sys.stdin.readline()
   sh=yacc.parse(" ".join(sys.argv[1:]))
   print sh
    
