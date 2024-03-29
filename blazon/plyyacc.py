#!/usr/bin/env python3

import blazon
import sys
import ply.yacc as yacc
import treatment
import copy
import functools

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
#    'blazon : multitreatment'
#    shield=blazon.Field()
#    shield.tincture=p[1]
#    Globals.shield=shield
#    p[0]=shield
#    return shield

def p_empty(p):
    "empty : "
    pass

def p_blazon_2(p):
    "blazon : multitreatment optcharges"
#    sys.stderr.write("top: %s %s %s %s\n"%
#                     tuple(map(str,p[1:])))
    shield=blazon.Field()
    shield.tincture=p[1]
    if p[2]:
        # shield.extendCharges(p[2])
        ## The following should also be done for Chiefs, doesn't quite work yet
        justcharges=[i for i in p[2]
                     if not isinstance(i,blazon.Bordure)]
        shield.extendCharges(justcharges)
        bord=[i for i in p[2] if isinstance(i,blazon.Bordure)]
        if bord:
            shield.addBordure(bord[0])
    p[0]=shield
    Globals.shield=shield
    return shield

def p_optcharges(p):
    """optcharges : charges
                  | empty"""
    p[0]=p[1]

def p_multitreatment_1(p):
    "multitreatment : treatment"
    p[0]=p[1]

def p_division_1(p):
    "division : PARTYPER ORDINARY mods optlinetype"
    z=functools.partial(lookup("per "+p[2]),linetype=p[4])
    if p[3]:
        m=p[3]
        def rv(*ar, **kw):
            v=z(*ar,**kw)
            for i in m:
                # sys.stderr.write("%s\n"%i)
                v.modify(i)
            return v
        p[0]=rv
    else:
        p[0]=z

def p_division_1_0(p):
    """division : QUARTERLY PARTYPER ORDINARY LINETYPE"""
    # For handling "quarterly per pale indented"
    # ORDINARY had better be "pale" or "fess"
    lines = {'linetype':'plain', 'linetypefess':'plain'}
    if p[3] == "pale":
        key = 'linetype'
    else:
        key = 'linetypefess'
    lines[key] = p[4]
    p[0] = functools.partial(lookup(p[1]), **lines)

def p_division_1_1(p):
    """division : PARTYPER ORDINARY mods AND PARTYPER ORDINARY mods"""
    # Kind of a special case, to handle "per pale and per chevron"
    # What about "per pale indented and per chevron"?
    # or "per pale and per chevron indented"?
    # or "per pale wavy and per chevron indented"?
    # (or for that matter, "per pale wavy and per fess indented",
    # as an alternative to/improvement on  "quarterly per pale
    # indented" above?)
    # At least let's handle "per pale and per chevron inverted".
    if frozenset([p[2], p[6]]) != frozenset(["pale", "chevron"]):
        raise Exception("Must be per pale and per chevron.")
    res = treatment.PerPaleAndChevron
    # There really should be only one of the optinverteds.
    mods = p[3] or p[7]
    # When will I break this out into a function of its own?
    # (have to pass the current variables in as locals...)
    def rv(*ar, **kw):
        z = res(*ar, **kw)
        for m in mods:
            z.modify(m)
        return z
    p[0] = rv

def p_division_2(p):
    "division : QUARTERLY optinverted optlinetype"
    p[0]=functools.partial(lookup(p[1]), linetype=p[4])

def p_multitreatment_2(p):
    "multitreatment : division multitreatment AND multitreatment"
    p[0]=p[1](p[2],p[4])

def p_multitreatment_2_1(p):
    "multitreatment : PARTYPER PALL optinverted optlinetype multitreatment multitreatment AND multitreatment"
    p[0]=lookup("per "+p[2])(p[5],p[6],p[8],linetype=p[4])
    for f in p[3]:
        f(p[0])

def p_treatment_1(p):
    "treatment : COLOR"
    p[0]=treatment.Treatment(p[1])
    Globals.colors.append(p[0])
    fillin(p[0])
    extrafillin(p[0])

def p_treatment_1_b(p):
    "treatment : LP multitreatment RP"
    # for debugging and creating really weird treatments
    p[0]=p[2]

def p_lineyness_1(p):
    "lineyness : LINEY optlinetype optamt"
    p[0]=functools.partial(lookup(p[1]),p[3],linetype=p[2])

def p_lineyness_2(p):
    "lineyness : LINEY LINEY optamt"
    # LINEY LINEY can't have linetype.
    check=lookup(p[1]+p[2])
    if callable(check) and issubclass(check, treatment.Treatment):
        p[0]=functools.partial(check,0)
    else:
        c1, c2=p[1],p[2]
        def rv(x, y, *args, **kwargs):
            return lookup(c1)(0,lookup(c2)(0,x,y,*args,**kwargs),
                              lookup(c2)(0,y,x,*args,**kwargs))
        p[0]=rv

def p_multitreatment_3(p):
    "multitreatment : lineyness treatment AND treatment"
    p[0]=p[1](p[2],p[4])

def p_treatment_4(p):
    """treatment : FUR
                 | COUNTERCHARGED"""
    p[0]=lookup(p[1])()

def p_multitreatment_5(p):
    "treatment : FURRY treatment AND treatment"
    p[0]=lookup(p[1])(p[2],p[4])

def p_multitreatment_6(p):
    "treatment : COLOR ALTERED treatment"
    # "treatment : treatment ALTERED treatment"
    p[0]=lookup(p[2])(p[1],p[3])

def p_multitreatment_7(p):
    "treatment : QUARTERLY multitreatment AND multitreatment"
    p[0]=lookup(p[1])(p[2],p[4])

def p_treatment_8(p):
    "treatment : OF THE CARDINAL"
    # Not sure we can assume field is in colors[0], but maybe okay.
    d={"field":1, "first":1, "second":2, "third":3, "fourth":4, "fifth":5,
       "sixth":6, "seventh":7, "eighth":8, "ninth":9, "tenth":10, "last":0}
    n=d[p[3]]
    p[0]=Globals.colors[n-1]
    fillin(p[0])

def p_treatment_9(p):
    """treatment : COLOR SEMY OF almostfullcharge
                 | COLOR SEMYDELIS opttreatment
                 | COLOR SEMY OF GROUPS OF grpcharge
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
    if len(p)==4 and not f.tincture:
        Globals.extracolorless.append(f)

def p_treatment_9a(p):
    """treatment : COLOR SEMY OF almostfullcharge CHARGED WITH almostfullcharge
               | COLOR SEMY OF almostfullcharge CHARGED WITH grpcharge"""
    p[4].addCharge(p[7])
    p[0]=treatment.Semy(treatment.Treatment(p[1]),p[4])

def p_opttreatment(p):
    """opttreatment : multitreatment
                    | empty"""
    p[0]=p[1]

def p_optlinetype(p):
    """optlinetype : LINETYPE
                   | empty"""
    p[0]=p[1]

def p_grouporcharge(p):
    """grouporcharge : grpcharge
                 | fullcharge"""
    p[0]=p[1]

def p_charges(p):
    """charges : optand optplacement grouporcharge
               | charges optand optplacement optoverall grouporcharge"""
    if len(p)==4:
        if p[2]:
            # ???
            if isinstance(p[3], blazon.ChargeGroup):
                p[3].arrangement=p[2]
                gp=p[3]
            else:
                gp=blazon.ChargeGroup(1,p[3])
                gp.arrangement=p[2]
        else:
            gp=p[3]
        p[0]=[gp]
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

        # Always make it a ChargeGroup if it isn't?
        # ... unless it's a TrueOrdinary?
        if p[3] or (not isinstance(p[5], blazon.ChargeGroup)
                    and not isinstance(p[5], blazon.TrueOrdinary)):
            newthing=blazon.ChargeGroup(1, p[5])
            if p[3]:
                newthing.arrangement=p[3]
        else:
            newthing=p[5]
        p[0]=p[1] + [newthing]
        ########
        # if isinstance(lastgroup, blazon.ChargeGroup) and not p[3]:
        #     lastthing=lastgroup.charges[0]
        #     thegroup=lastgroup
        # else:
        #     lastthing=lastgroup
        #     thegroup=blazon.ChargeGroup()
        #     if p[3]:
        #         thegroup.arrangement=p[3]
        #         thegroup.charges=[p[5]]
        #     else:
        #         thegroup.charges=[lastthing]
        # if not p[2] == "between" and \
        #    not isinstance(lastthing, blazon.TrueOrdinary) and \
        #    not isinstance(p[5], blazon.TrueOrdinary):
        #     thegroup.charges.append(p[5])
        #     p[1][-1]=thegroup
        #     p[0]=p[1]
        # else:
        #     p[0]=p[1] + [p[5]]
        # if p[3]:
        #     p[0]=p[1] + [p[5]]
        # if p[3]:
        #     p[5].setOverall()

def p_grpcharge_3(p):
    """grpcharge : amount almostfullcharge optarrange opttreatment optfimbriation optrows
             | amount almostfullcharge optarrange opttreatment optfimbriation optrows EACH CHARGED WITH charges"""
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

def p_grpcharge_1a(p):
    "grpcharge : amount GROUPS optarrange optrows OF charges"
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


def p_basecharge(p):
    """basecharge : ORDINARY
                | PALL
                | CHARGE
                | BORDURE
                | CHIEF
                | BASE"""
    p[0]=lookup(p[1])

# mullets have to be a special case, because the "of X points" interferes
# with "of the second"

def p_basecharge_2(p):
    """basecharge : mullet
                  | basecharge TOKEN""" # to eat extraneous tokens!
    # That's for things like "a cross moline" so it turns into just a cross.
    # It's really only for debugging though!!
    p[0]=p[1]

def p_mullet(p):
    """mullet : MULLET
              | MULLET OF amount WORD"""
    if p[1].startswith('mullet'):
        n=5
    elif p[1]=='label':
        n=3
    else:
        n=3                     # ????
    try:
        n=p[3]
    except IndexError:
        pass
    p[0]=functools.partial(lookup(p[1]),n)

def p_midcharge(p):
    "midcharge : basecharge mods optlinetype"
    if p[3]:
        res=functools.partial(p[1], linetype=p[3])
    else:
        res=functools.partial(p[1])
    if p[2]:
        mods=p[2]
        def rv(*args, **kw):
            z=res(*args, **kw)
            for m in mods:
                z.modify(m)
            return z
        p[0]=rv
    else:
        p[0]=res

# Multiple INVERTEDs, for "inverted enhanced" or "palewise contourny"
def p_mods(p):
    """mods : INVERTED mods
            | empty"""
    if not p[1]:
        p[0]=[]
    else:
        p[0]=[p[1]]+p[2]

def p_almostfullcharge_1(p):
    "almostfullcharge : midcharge opttreatment optfimbriation optendorsed"
    res=p[1]()
    try:
        p[2], p[4][1] = (p[2] or p[4][1]), (p[4][1] or p[2])
    except TypeError:
        pass
    if not p[2]:
        if (not res.tincture or not hasattr(res.tincture,"color") or
            not res.tincture.color or res.tincture.color == "none"):
            Globals.colorless.append(res)
            res.tincture=None
    else:
        res.tincture=p[2]
    if p[4]:
        res.modify(*p[4])
    p[3](res)
    p[0]=res

def p_fullcharge_1(p):
    "fullcharge : optA almostfullcharge"
    if isinstance(p[2],blazon.TrueOrdinary):
        p[0]=p[2]
    else:
        ## Sigh, this busts simple things like a fess between 6 lozenges.
        ## This should be doable.
        # gp=blazon.ChargeGroup(1, p[2])
        # p[0]=gp
        p[0]=p[2]

#def p_fullcharge_1a(p):
#    "fullcharge : grpcharge"
#    p[0]=p[1]

def p_optendorsed(p):
    """optendorsed : ENDORSED opttreatment
                   | empty"""
    try:
        p[0]=p[1], p[2]
    except IndexError:
        pass

# def p_fullcharge_2(p):
#     """fullcharge : ON A almostfullcharge A almostfullcharge
#                   | ON A almostfullcharge grpcharge"""
#     res=p[3]
#     if len(p)==6:
#         gp=blazon.ChargeGroup(1,p[5])
#         res.addCharge(gp)
#         #res.addCharge(p[5])
#     else:
#         res.addCharge(p[4])
#     p[0]=res

def p_fullcharge_2(p):
    """fullcharge : ON A almostfullcharge charges"""
    if not (len(p[4])==1 and isinstance(p[4][0], blazon.ChargeGroup)):
        res=blazon.ChargeGroup()
        res.extendCharges(p[4])
        res=[res]
    else:
        res=p[4]
    p[3].extendCharges(res)
    p[0]=p[3]

def p_almostfullcharge_4(p):
    "almostfullcharge : fullcharge CHARGED WITH charges"
    res=p[1]
    res.extendCharges(p[4])
    p[0]=res

def p_fullcharge_5(p):
    "fullcharge : LP charges RP"
    p[0]=blazon.ChargeGroup()
    p[0].fromarray(p[2])

def p_basecharge_3(p):
    "basecharge : URL"
    url=p[1]
    p[0]=blazon.Blazon.outside_element(url)

def p_basecharge_4(p):
    "basecharge : NAME"
    try:
        p[0]=blazon.Blazon.outside_element(blazon.Blazon.lookupcharge(p[1]))
    except KeyError:
        # Punt.
        p[0]=blazon.Image(p[1], 80, 80)

## PERHAPS DISALLOW OR ABSORB INTO PREVIOUS?
def p_tokenlist(p):
    """tokenlist : TOKEN
                 | TOKEN tokenlist"""
    if len(p)==2:
        p[0]=p[1]
    else:
        p[0]=p[1]+" "+p[2]

def p_basecharge_5(p):
    "basecharge : tokenlist"
    # How about we treat these as a form of (name)?
    try:
        p[0]=blazon.Blazon.outside_element(blazon.Blazon.lookupcharge(p[1]))
    except KeyError:
        p[0]=lambda *x:blazon.ExtCharge("question")
        # p[0]=blazon.Image(p[2], 80, 80)

def p_basecharge_6(p):
    "basecharge : TEXT"
    txt=p[1]
    p[0]=lambda *x: blazon.Text(txt, 80, 80) # these magic 80 numbers...?

def p_bordure(p):
    """bordure : empty
               | WITHIN A BORDURE optlinetype opttreatment
               | empty A BORDURE optlinetype opttreatment
               | WITHIN A BORDURE optlinetype opttreatment CHARGED WITH charges
               | empty A BORDURE optlinetype opttreatment CHARGED WITH charges

    """
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

def p_optplacement(p):
    """optplacement : IN optdir CHIEF
                    | IN optdir BASE
                    | empty"""
    if not p[1]:
        p[0]=None
    else:
        if not p[2]:
            side=""
        else:
            side=p[2]
        p[0]=lookup("in "+side+p[3])()

def p_optarrange(p):
    """optarrange : IN ORDINARY optinverted
                  | IN PALL optinverted
                  | IN BORDURE
                  | IN ANNULO
                  | empty"""
    if not p[1]:
        p[0]=None
    else:
        if len(p)>3:
            act=p[3]
        else:
            act=None
        p[0]=lookup("in "+p[2])(action=act)

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

def p_optinverted(p):
    """optinverted : INVERTED
                   | empty"""
    if not p[1]:
        p[0]=[(lambda x:x)]
    else:
        s=p[1]
        p[0]=(lambda x:x.modify(s))

def p_optfimbriation(p):
    """optfimbriation : FIMBRIATED COLOR
                      | empty"""
    if len(p)<=2:
        p[0]=lambda x:x
    else:
        col=p[2]
        fillin(col)
        extrafillin(col)
        if p[1]=="voided":
            p[0]=lambda x:x.void(col)
        elif p[1]=="fimbriated":
            p[0]=lambda x:x.fimbriate(col)
        else:
            p[0]=lambda x:x.modify(p[1])(col)

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

def p_error(p):
    ""
    sys.stderr.write("Something unexpected: %s\n"%p)
    raise Exception("Parse Error")

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
