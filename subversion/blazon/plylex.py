#!/usr/bin/python
# -*- coding: latin-1 -*-

import lex
import re
import blazon
import sys
import treatment
import arrangement
import copy

tokens=("COLOR","ORDINARY","CHARGE","LINEY","CHIEF","ON","COUNTERCHARGED",
        "LINETYPE","FUR","FURRY","NUM","NUMWORD","INVERTED","ALTERED",
        "PARTYPER","FIMBRIATED","QUARTERLY","AND","OF","A","WS","EACH",
        "CHARGED","WITH","THE","CARDINAL","SEMY","SEMYDELIS","WORD",
        "PALL","WITHIN","BORDURE","BEZANTY","LP","RP","IN","DIRECTION")

# For some reason, things seem to work better when functions are defined,
# even if they don't do anything.  e.g. "vair" would overshadow "vairy"
# when they were just strings.

t_ignore=" \n\t"


# Hmm.  How to handle "*in* a bordure..." ?
def t_BORDURE(t):
    r"bordure|orle|tressure|double.tressure"
    return t

# The gutty colors don't work quite right yet...
def t_COLOR(t):
    r"((d')?or|argent|sable|azure|gules|purpure|vert|tenné|tenne|tawny|sanguine|murrey|bleu[ ]celeste|rose|copper|de.larmes|de.poix|de.sang|d'huile|d'eau)"
    return t

def t_AND(t):
    r"(and|between)"                    # FOR NOW, between is a synonym of and.
    return t

def t_BEZANTY(t):
    r"bezanty|platey|pellety|hurty|tortoilly"
    return t

t_OF=r"of"
t_EACH=r"each"
t_CHARGED=r"charged"
t_WITH=r"with"
t_THE=r"the"
t_IN="in"
t_SEMY=r"semy"
t_LP=r"{|lp"                           # leftparen
t_RP=r"}|rp"                           # rightparen
    
def t_SEMYDELIS(t):
    r"(semy.de.lis|billety|gutty|crusilly)"
    return t

# t_QUARTERED=r"quartered"
t_WITHIN=r"within"

def t_CARDINAL(t):
    r"(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|field|last)"
    # Field and last aren't really cardinals, but it's just as easy
    return t

def t_LINEY(t):
    r"(paly|barry|bendy(.sinister)?|gyronny|checky|lozengy|pily|chevronny)"
    return t

def t_QUARTERLY(t):
    r"quarterly"
    return t

def t_CHARGE(t):
    r"roundels?|annulets?|lozenges?|fleurs?.de.lis|cross(es)?.(formy|pattee|pommee|bottony|humetty|flory)|cross-crosslets?|mullets?|billets?|goutes?|be[zs]ants?|plates?|ogress(es)?|pellets?|gunstones?|torteaux?|hurts?|golpes?|pome(i?s)?|lions?.(passant|rampant)|pallets?|fir.twigs?|fusils?|mascles?|triangles?|canton|gyron|crescents?|escutcheons?|shakeforks?"
    return t

t_ORDINARY=r"(fesse?|pale|cross|saltire|bend(lets?)?[ ]sinister|bend(lets?)?|piles?|chevron(el)?s?|base|label|bars?(.gemelles?)?|fret|flaunches|batons?)"

t_PALL=r"pall"

# Chief is not an ordinary
t_CHIEF=r"chief"
t_ON=r"on"

t_LINETYPE=r"(plain|indented|dancetty|embattled|invected|engrailed|wavy|rayonny|dovetailed|raguly|nebuly|urdy)"

def t_FURRY(t):
    r"(vairy.in.pale|vairy|counter.vairy)"
    return t

def t_ALTERED(t):
    r"(fretty|ermined|masoned)"
    return t

t_FUR=r"(vair.in.pale|vair|counter.vair|ermines?|erminois|pean)"

t_PARTYPER=r"(party[ ]per|per)"
t_FIMBRIATED=r"fimbriated|voided"
t_INVERTED=r"inverted"
t_COUNTERCHARGED=r"countercha[rn]ged"
t_DIRECTION=r"dexter|sinister"

def t_A(t):
    r"an?"
    return t


def t_NUM(t):
    r"[0-9]+"
    t.value=int(t.value)
    return t


def t_NUMWORD(t):
    r"(one|two|three|four(teen)?|five|six(teen)?|seven(teen)?|eight(een)?|nine(teen)?|ten|eleven|twelve|thirteen|fifteen|twenty|I|II|III|IV)"
    t.value={"one":1, "two":2, "three":3, "four":4, "five":5, "six":6,
             "seven":7, "eight":8, "nine":9, "ten":10, "eleven":11,
             "twelve":12, "thirteen":13, "fourteen":14, "fifteen":15,
             "sixteen":16, "seventeen":17, "eighteen":18, "nineteen":19,
             "twenty":20,"I":1,"II":2,"III":3,"IV":4}[t.value]
    return t

def t_WORD(t):
    r"points"
    # Word that's required but doesn't mean much.
    return t

def t_error(t):
    sys.stderr.write("illegal character: %s\n"%t.value[0])
    t.skip(1)


lookupdict={
    "vair": treatment.Vair,
    "counter.vairy?": treatment.CounterVair,
    "fesse?": blazon.Fesse,
    "pale" : blazon.Pale,
    "pallets?" : blazon.Pallet,
    "cross": blazon.Cross,
    "saltire": blazon.Saltire,
    "bend" : blazon.Bend,
    "bendlets?" : blazon.Bendlet,
    "bendlets?.sinister" : blazon.BendletSinister,
    "bars?" : blazon.Bar,
    "bars?.gemelles?" : blazon.BarGemelle,
    "piles?": blazon.Pile,
    "chevrons?": blazon.Chevron,
    "chevronels?": blazon.Chevronel,
    "bend sinister": blazon.BendSinister,
    "baton": blazon.Baton,
    "chief": blazon.Chief,
    "base": blazon.Base,
    "pall": blazon.Pall,
    "labels?": blazon.Label,
    "lables?": blazon.Label,
    "fret": blazon.Fret,
    "flaunches": blazon.Flaunches,
    "lions?.passant": (lambda *a: blazon.Symbol("lionpassant")), 
    "lions?.rampant": (lambda *a: blazon.Symbol("lionrampant")), 
    "roundels?": blazon.Roundel,
    "roundles?": blazon.Roundel,
    "be[sz]ant[ys]?" : (lambda *a: blazon.Roundel(tincture="or")),
    "plate[ys]?" : (lambda *a: blazon.Roundel(tincture="argent")),
    "ogress(es)?" : (lambda *a: blazon.Roundel(tincture="sable")),
    "pellet[sy]?" : (lambda *a: blazon.Roundel(tincture="sable")),
    "gunstones?" : (lambda *a: blazon.Roundel(tincture="sable")),
    "torteaux?" : (lambda *a: blazon.Roundel(tincture="gules")),
    "tortoilly" : (lambda *a: blazon.Roundel(tincture="gules")),
    "hurt[ys]?" : (lambda *a: blazon.Roundel(tincture="azure")),
    "golpes?" : (lambda *a: blazon.Roundel(tincture="purpure")),
    "pome(i?s)?" : (lambda *a: blazon.Roundel(tincture="vert")),
    "billets?": blazon.Billet,
    "annulets?": blazon.Annulet,
    "lozenges?": blazon.Lozenge,
    "mascles?" : blazon.Mascle,
    "fusils?" : blazon.Fusil,
    "triangles?": blazon.Triangle,
    "canton": blazon.Canton,            # There can be no more than one canton.
    "gyron": blazon.Gyron,
    "fleurs?.de.lis": (lambda *a: blazon.ExtCharge("fleur")),
    "goutes?": (lambda *a: blazon.ExtCharge("goute")),
    "cross(es)?.formy": (lambda *a: blazon.ExtCharge("formy")),
    "cross(es)?.pattee": (lambda *a: blazon.ExtCharge("formy")),
    "cross(es)?.pommee": (lambda *a: blazon.ExtCharge("pommee")),
    "cross(es)?.bottony": (lambda *a: blazon.ExtCharge("bottony")),
    "cross(es)?.humetty": (lambda *a: blazon.ExtCharge("humetty")),
    "cross(es)?.flory": (lambda *a: blazon.ExtCharge("flory")),
    "cross-crosslets?": (lambda *a: blazon.ExtCharge("crosscrosslet")),
    "mullets?": (lambda *a: blazon.ExtCharge("mullet",extension=a)),
    "escutcheons?": (lambda *a: blazon.ExtCharge("escutcheon")),
    "shakeforks?": (lambda *a: blazon.ExtCharge("shakefork")),
    "semy.de.lis": (lambda *a: blazon.ExtCharge("fleur")),
    "gutty": (lambda *a: blazon.ExtCharge("goute")),
    "fir.twigs?": (lambda *a: blazon.ExtCharge("firtwig")),
    "crescents?": (lambda *a: blazon.ExtCharge("crescent")),
    "billety": blazon.Billet,
    "crusilly": (lambda *a: blazon.ExtCharge("humetty")),
    "bordure": blazon.Bordure,
    "orle": blazon.Orle,
    "tressure": blazon.Tressure,
    "double.tressure": blazon.DoubleTressure,
    "paly": treatment.Paly,
    "pily": treatment.Pily,
    "barrypily": treatment.BarryPily,
    "barry": treatment.Barry,
    "chevronny": treatment.Chevronny,
    "bendy": treatment.Bendy,
    "bendy.sinister": treatment.BendySinister,
    "gyronny": treatment.Gyronny,
    "ermine": blazon.Ermine,
    # This is a bit of a hack...
    "ermines": (lambda *a: treatment.Ermine("sable","argent")),
    "erminois": (lambda *a: treatment.Ermine("or","sable")),
    "pean": (lambda *a: treatment.Ermine("sable","or")),
    "ermined": treatment.Ermine,
    "masoned": treatment.Masoned,
    "fretty": treatment.Fretty,
    "vairy?.in.pale": treatment.VairInPale,
    "vairy": treatment.Vair,
    "per cross": treatment.PerCross,
    "per saltire": treatment.PerSaltire,
    # Parker mentions the following, but possibly it only applies
    # to the field, not to ordinaries.
    # Unfortunately, ATM it won't work, probably because the crummy lexer
    # can't handle both quartered in this sense, and quartered in the sense
    # of t_QUARTERLY.
    "per saltire quartered": treatment.PerSaltire,
    "per fesse?": treatment.PerFesse,
    "per pale": treatment.PerPale,
    "per bend": treatment.PerBend,
    "per bend sinister": treatment.PerBendSinister,
    "per chevron": treatment.PerChevron,
    "per pall": treatment.PerPall,
    "quarterly": treatment.PerCross,
    # "quartered": treatment.PerCross,
    # Need to make *copies* of the tinctures,
    # lest they contain references to charges (Semy) which then get doubly
    # shrunk.
    "checky": (lambda num,col1,col2,**kw:
               treatment.Paly(num,treatment.Barry(num,col1,col2),
                              treatment.Barry(num,copy.deepcopy(col2),
                                              copy.deepcopy(col1)))),
    "lozengy": (lambda num,col1,col2,**kw:
                treatment.Bendy(num,treatment.BendySinister(num,col1,col2),
                                treatment.BendySinister(num,copy.deepcopy(col2),
                                                        copy.deepcopy(col1)))),
    "countercha[rn]ged": treatment.Countercharged,
    "in pale": arrangement.InPale,
    "in fesse?": arrangement.InFesse,
    "in bend": arrangement.InBend,
    "in bend.sinister": arrangement.InBendSinister,
    "in chief": arrangement.InChief,
    "in base": arrangement.InBase,
    "in dexterchief": (lambda *a: arrangement.InChief(side="dexter")),
    "in sinisterchief": (lambda *a: arrangement.InChief(side="sinister")),
    "in dexterbase": (lambda *a: arrangement.InBase(side="dexter")),
    "in sinisterbase": (lambda *a: arrangement.InBase(side="sinister")),
    "in orle": arrangement.InOrle
    }

def lookup(key):
    # sys.stderr.write("Looking up: (%s)\n"%key)
    try:
        return lookupdict[key.lower()]
    except KeyError:
        key=key.lower()
        for k in lookupdict.keys():
            # Need the match to be anchored at the end too.
            # sys.stderr.write("Matching with: (%s)\n"%k)
            m=re.match(k+"$",key)
            if m:
                # sys.stderr.write("Returning: %s\n"%Globals.lookup[m.re.pattern[:-1]])
                # have to chop off the $ we added.
                # sys.stderr.write("Found it: %s\n"%m.re.pattern)
                return lookupdict[m.re.pattern[:-1]]
        return key


lex.lex()

if __name__ == "__main__":
    line=sys.stdin.readline()
    while line:
        lex.input(line)
        while 1:
            tok=lex.token()
            if not tok: break
            print tok
        line=sys.stdin.readline()
