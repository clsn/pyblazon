#!/usr/bin/python

import blazon
import sys
import ply.yacc as yacc
import treatment
import copy

from plylex import tokens,lookup
from arrangement import ByNumbers

class Globals:
    colorless=[]
    extracolorless=[]
    colors=[]
    shield=None
    lastnum=0

def fillin(col):
    for obj in Globals.colorless:
        obj.tincture=col
    Globals.colorless=[]

def extrafillin(col):
    """This and Globals.extracolorless are hacks in order not to get into
    infinite regress with things like 'gules billetty a lion rampant
    argent'.  Otherwise the billet goes into colorless which is then filled
    in by the billetty treatment... ugh.  It's a hack, but it works.  Oh,
    and extrafillin is only called by treatments that are just "COLOR"s."""
    for obj in Globals.extracolorless:
        obj.tincture=col
    Globals.extracolorless=[]

start='blazon'

#def p_blazon_1(p):
#    'blazon : fulltreatment'
#    shield=blazon.Field()
#    shield.tincture=p[1]
#    Globals.shield=shield
#    p[0]=shield
#    return shield

def p_blazon_2(p):
    "blazon : fulltreatment optcharges bordure chief"
#    sys.stderr.write("top: %s %s %s %s\n"%
#                     tuple(map(str,p[1:])))
    shield=blazon.Field()
    shield.tincture=p[1]
    if p[2]:
        shield.extendCharges(p[2])
    if p[3]:
        shield.addBordure(p[3])
    if p[4]:
        shield.addChief(p[4])
    p[0]=shield
    Globals.shield=shield
    return shield

def p_optcharges(p):
    """optcharges : charges
                  | empty"""
    p[0]=p[1]

def p_fulltreatment_1(p):
    "fulltreatment : treatment"
    p[0]=p[1]
    fillin(p[0])
    
def p_fulltreatment_2(p):
    "fulltreatment : PARTYPER ORDINARY optinverted optlinetype fulltreatment AND fulltreatment"
    p[0]=lookup("per "+p[2])(p[5],p[7],linetype=p[4])
    for f in p[3]:
        f(p[0])
    fillin(p[0])

def p_fulltreatment_2_1(p):
    "fulltreatment : PARTYPER PALL optinverted optlinetype fulltreatment fulltreatment AND fulltreatment"
    p[0]=lookup("per "+p[2])(p[5],p[6],p[8],linetype=p[4])
    for f in p[3]:
        f(p[0])
    fillin(p[0])

def p_treatment_1(p):
    "treatment : COLOR"
    p[0]=treatment.Treatment(p[1])
    Globals.colors.append(p[0])
    fillin(p[0])
    extrafillin(p[0])

def p_treatment_1_b(p):
    "treatment : LP fulltreatment RP"
    # for debugging and creating really weird treatments
    p[0]=p[2]

def p_fulltreatment_3(p):
    "fulltreatment : LINEY optlinetype optamt treatment AND treatment"
    p[0]=lookup(p[1])(p[3],p[4],p[6],linetype=p[2])
    fillin(p[0])

def p_fulltreatment_4(p):
    "fulltreatment : LINEY LINEY treatment AND treatment"
    # special case for barrypily:
    check=lookup(p[1]+p[2])
    try:
        test=issubclass(check,treatment.Treatment)
    except:
        test=False
    if test:
        p[0]=check(0,p[3],p[5])
    else:
        p[0]=lookup(p[1])(0,lookup(p[2])(0,p[3],p[5]),lookup(p[2])(0,p[5],p[3]))
    fillin(p[0])

def p_treatment_4(p):
    """treatment : FUR
                 | COUNTERCHARGED"""
    p[0]=lookup(p[1])()
    fillin(p[0])

def p_treatment_5(p):
    "treatment : FURRY treatment AND treatment"
    p[0]=lookup(p[1])(p[2],p[4])
    fillin(p[0])

def p_treatment_6(p):
    "treatment : treatment ALTERED treatment"
    p[0]=lookup(p[2])(p[1],p[3])
    fillin(p[0])

def p_treatment_7(p):
    "treatment : QUARTERLY fulltreatment AND fulltreatment"
    p[0]=lookup(p[1])(p[2],p[4])
    fillin(p[0])

def p_treatment_8(p):
    "treatment : OF THE CARDINAL"
    # Not sure we can assume field is in colors[0], but maybe okay.
    d={"field":1, "first":1, "second":2, "third":3, "fourth":4, "fifth":5,
       "sixth":6, "seventh":7, "eighth":8, "ninth":9, "tenth":10, "last":0}
    n=d[p[3]]
    p[0]=Globals.colors[n-1]
    fillin(p[0])

def p_treatment_9(p):
    """treatment : COLOR SEMY OF charge
                 | COLOR SEMYDELIS opttreatment
                 | COLOR SEMY OF GROUPS OF group
                 | COLOR BEZANTY"""
    # The second is actually syntactically like ALTERED
    if len(p)==5:
        p[0]=treatment.Semy(treatment.Treatment(p[1]),p[4])
    elif len(p)==4:
        f=lookup(p[2])()
        f.tincture=p[3]
        p[0]=treatment.Semy(treatment.Treatment(p[1]),f)
    elif len(p)==7:
        gp=blazon.BigRect()
        gp.tincture=treatment.Treatment("proper")
        gp.addCharge(copy.deepcopy(p[6]))
        p[0]=treatment.Semy(treatment.Treatment(p[1]),gp)
    else:                               # len(p)==3
        p[0]=treatment.Semy(treatment.Treatment(p[1]),lookup(p[2])())
    fillin(p[0])
    if len(p)==4 and not f.tincture:
        Globals.extracolorless.append(f)

def p_treatment_9a(p):
    "treatment : COLOR SEMY OF charge CHARGED WITH grouporcharge"
    p[4].addCharge(p[7])
    p[0]=treatment.Semy(treatment.Treatment(p[1]),p[4])
    
def p_opttreatment(p):
    """opttreatment : fulltreatment
                    | empty"""
    p[0]=p[1]

def p_optlinetype(p):
    """optlinetype : LINETYPE
                   | empty"""
    p[0]=p[1]

def p_charges(p):
    """charges : grouporcharge
               | charges optand optoverall grouporcharge"""
    if len(p)==2:
        p[0]=[p[1]]
    else:
        # OK, let's try to work out this business of "consolidating"
        # charges into chargegroups.  Charges conjoined with "and" can join
        # into a group.  Charges conjoined with "between" cannot.  Let's
        # see if we can do this without separate lexemes for "and" and
        # "between", just different values for it.
        #
        # We need to be able to consolidate in order to make things like
        # {azure a bend argent between a fusil and a roundel or}
        lastgroup=p[1][-1]
        if not p[2] == "between" and \
                 not isinstance(lastgroup.charges[0], blazon.TrueOrdinary) and \
                 not isinstance(p[4].charges[0], blazon.TrueOrdinary):
            lastgroup.charges.extend(p[4].charges)
            p[0]=p[1]
            # Works, but then we have two chargegroups that don't know how
            # to interact.
        else:
            p[0]=p[1]+[p[4]]
        if p[3]:
            p[4].setOverall()

def p_grouporcharge_a(p):
    """grouporcharge : group"""
    p[0]=p[1]

def p_grouporcharge_b(p):
    """grouporcharge : charge optarrange"""
    p[0]=blazon.ChargeGroup(1,p[1])
    if not p[1].tincture:
        Globals.colorless.append(p[0].charges[0])
    p[0].arrangement=p[2]

def p_group_1(p):
    """group : amount charge optarrange opttreatment optfimbriation optrows
             | amount charge optarrange opttreatment optfimbriation optrows EACH CHARGED WITH charges"""
    # I don't have to worry about handling the opttreatment.  That's just in
    # case the treatment was omitted in the charge before the arrangement,
    # and the "missing color" code will handle it.  Right?
    p[0]=blazon.ChargeGroup(p[1],p[2])
    if len(p)>7:
        for elt in p[0].charges:
            elt.extendCharges(copy.deepcopy(p[10]))
    rows=p[6]
    if not p[2].tincture:
        Globals.colorless.extend(p[0].charges)
    # Doesn't matter if p[3] is empty; so we'll pass along an empty one.
    p[0].arrangement=p[3]
    if rows:
        p[0].arrangement=ByNumbers(rows)
    # We wind up having two different places for treatment and fimbriation,
    # but that's okay.  If you specify both, one wins, but GIGO after all.
    p[5](p[0])

def p_group_1a(p):
    "group : amount GROUPS optarrange optrows OF charges"
    # The same as above, just taking it to mean "areas proper each charged with"
    area=blazon.BigRect()
    area.tincture=blazon.Treatment("proper")
    res=blazon.ChargeGroup(p[1],area)
    for elt in res.charges:
        elt.extendCharges(copy.deepcopy(p[6]))
    res.arrangement=p[3]
    if p[4]:
        res.arrangement=ByNumbers(p[4])
    p[0]=res
    

def p_group_2(p):
    """group : LP charges RP"""
    p[0]=blazon.ChargeGroup()
    p[0].fromarray(p[2])

def p_ordinary(p):
    """ordinary : ORDINARY
                | PALL
                | CHARGE
                | CHIEF """
    p[0]=lookup(p[1])()

# mullets have to be a special case, because the "of X points" interferes
# with "of the second"

def p_ordinary_2(p):
    "ordinary : mullet"
    p[0]=p[1]

def p_mullet(p):
    """mullet : MULLET
              | MULLET OF amount WORD"""
    n=5
    try:
        n=p[3]
    except IndexError:
        pass
    p[0]=lookup(p[1])(n)

def p_charge_1(p):
    "charge : optA ordinary optinverted optlinetype opttreatment optfimbriation"
    res=p[2]
    for f in p[3]:
        f(res)
    res.lineType=p[4]
    if not p[5]:
        if not res.tincture or not hasattr(res.tincture,"color") or not res.tincture.color or res.tincture.color == "none":
            Globals.colorless.append(res)
            res.tincture=None
    else:
        res.tincture=p[5]
    p[6](res)
    p[0]=res

def p_charge_2(p):
    "charge : ON A charge optA grouporcharge"
    p[3].addCharge(p[5])
    p[0]=p[3]

def p_ordinary_3(p):
    "ordinary : optA URL"
    p[0]=blazon.Blazon.outside_element(p[2])

def p_ordinary_4(p):
    "ordinary : optA NAME"
    try:
        p[0]=blazon.Blazon.outside_element(blazon.Blazon.lookupcharge(p[2]))
    except KeyError:
        # Punt.
        p[0]=blazon.Image(p[2], 80, 80)

def p_tokenlist(p):
    """tokenlist : TOKEN
                 | TOKEN tokenlist"""
    if len(p)==2:
        p[0]=p[1]
    else:
        p[0]=p[1]+" "+p[2]

def p_ordinary_5(p):
    "ordinary : optA tokenlist"
    # How about we treat these as a form of (name)?
    try:
        p[0]=blazon.Blazon.outside_element(blazon.Blazon.lookupcharge(p[2]))
    except KeyError:
        p[0]=blazon.ExtCharge("question")
        # p[0]=blazon.Image(p[2], 80, 80)

def p_ordinary_6(p):
    "ordinary : optA TEXT"
    p[0]=blazon.Text(p[2], 80, 80) # these magic 80 numbers...?

def p_bordure(p):
    """bordure : empty
               | WITHIN A BORDURE optlinetype opttreatment
               | WITHIN A BORDURE optlinetype opttreatment CHARGED WITH charges"""
    if len(p)<=2:
        p[0]=None
    else:
        p[0]=lookup(p[3])()
        if not(p[5]):
            Globals.colorless.append(p[0])
        else:
            p[0].tincture=p[5]
        if len(p)>=9 and p[8]:
            p[0].extendCharges(p[8])
        p[0].lineType=p[4]

def p_chief(p):
    """chief : empty
             | WITH A CHIEF optlinetype opttreatment
             | WITH A CHIEF optlinetype opttreatment CHARGED WITH charges""" 
    #| optand ON A CHIEF optlinetype opttreatment charges"""
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
    elif len(p)==9:
        p[0]=blazon.Chief()
        if not p[5]:
            Globals.colorless.append(p[0])
        else:
            p[0].tincture=p[5]
        p[0].extendCharges(p[8])
        p[0].lineType=p[4]
    else:
        # Drop back ten and punt
        p[0]=None

def p_optarrange(p):
    """optarrange : IN optdir ORDINARY optinverted
                  | IN optdir PALL optinverted
                  | IN optdir CHIEF
                  | IN optdir BORDURE
                  | IN optdir ANNULO
                  | empty"""
    if not p[1]:
        p[0]=None
    else:
        if not p[2]:
            side=""
        else:
            side=p[2]
        if len(p)>4:
            # WRONG!!!
            act=p[4]
        else:
            act=None
        p[0]=lookup("in "+side+p[3])(action=act)

def p_optdir(p):
    """optdir : DIRECTION
              | empty"""
    p[0]=p[1]

def p_optrows(p):
    """optrows : rows
               | empty"""
    p[0]=p[1]

def p_rows(p):
    """rows : amount rows
            | amount AND amount"""
    if len(p)==3:
        p[0]=[p[1]] + p[2]                # Just concatenate
    else:
        p[0]=[p[1], p[3]]
    
def p_amount(p):
    """amount : NUM
              | NUMWORD"""
    if p[1] == -1:
        p[0]=Globals.lastnum
    else:
        Globals.lastnum=p[1]
        p[0]=p[1]

def p_optamt(p):
    """optamt : OF amount
              | empty"""
    if len(p) == 3:
        p[0]=p[2]
    else:
        p[0]=8

# Have to allow for multiple INVERTEDs, for "palewise contourny" etc.
def p_optinverted(p):
    """optinverted : INVERTED optinverted
                   | empty"""
    if not p[1]:
        p[0]=[(lambda x:x)]
    else:
        s=p[1]
        p[0]=[(lambda x:x.modify(s))] + p[2]
        
def p_optfimbriation(p):
    """optfimbriation : FIMBRIATED COLOR
                      | empty"""
    if len(p)<=2:
        p[0]=lambda x:x
    else:
        col=p[2]
        if p[1]=="voided":
            p[0]=lambda x:x.void(col)
        else:
            p[0]=lambda x:x.fimbriate(col)

def p_optand(p):
    """optand : AND
              | empty"""
    p[0]=p[1]

def p_optoverall(p):
    """optoverall : OVERALL
                  | empty"""
    p[0]=p[1]

def p_optA(p):
    """optA : A
            | empty"""
    pass

def p_empty(p):
    "empty : "
    pass

def p_error(p):
    ""
    sys.stderr.write("Something unexpected: %s\n"%p)
    pass

def show_grammar(all=dir()):
    all=list(filter((lambda x: x[0:2] == 'p_'), all))
    all.sort()
    for f in all:
        print(getattr(sys.modules[__name__],f).__doc__)

yacc.yacc(method="LALR")

if __name__=="__main__":
#    line=sys.stdin.readline()
#    while line:
#        sh=yacc.parse(line)
#        print sh
#        line=sys.stdin.readline()
   sh=yacc.parse(" ".join(sys.argv[1:]))
   print(sh)
    
