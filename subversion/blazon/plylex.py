#!/usr/bin/python
# -*- coding: latin-1 -*-

import ply.lex as lex
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
        "PALL","WITHIN","BORDURE","BEZANTY","LP","RP","IN","DIRECTION",
        "URL","MULLET","NAME","ANNULO","GROUPS")

t_ignore=" \n\t"


t_BORDURE=r"\b(bordure|orle|tressure|double\W+tressure)\b"

t_COLOR=r"\b((d')?or|argent|sable|azure|gules|purpure|vert|tenné|tenne|tawny|sanguine|murrey|bleu[ ]celeste|rose|copper|de[ ]larmes|de[ ]poix|de[ ]sang|d'huile|d'eau|proper)\b"

t_AND=r"\b(and|&|between)\b"

t_BEZANTY=r"\b(be[sz]anty|platey|pellety|hurty|tortoilly)\b"

t_GROUPS=r"\bgroups\b"
t_OF=r"\bof\b"
t_EACH=r"\beach\b"
t_CHARGED=r"\bcharged\b"
t_WITH=r"\bwith\b"
t_THE=r"\bthe\b"
t_IN=r"\bin\b"
t_SEMY=r"\bsemy\b"
t_LP=r"\b({|lp)\b"                           # leftparen
t_RP=r"\b(}|rp)\b"                           # rightparen

t_ANNULO=r"\bannulo\b"

t_SEMYDELIS=r"\b(semy\W+de\W+l[iy]s|billett?y|go?utty|crusilly|mulletty)\b"

# t_QUARTERED=r"quartered"
t_WITHIN=r"\bwithin\b"

t_CARDINAL=r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|field|last)\b"
    # Field and last aren't really cardinals, but it's just as easy

t_LINEY=r"\b(paly|barry|bendy(\W+sinister)?|g[iy]ronny|checky|lozengy|pily|chevronny(\W+inverted)?)\b"

t_QUARTERLY=r"\bquarterly\b"

t_CHARGE=r"\b(roundels?|annulets?|lozenges?|fleurs?.de.l[iy]s|cross(es)?.(formy|pattee|pommee|bottony|humetty|flory)|cross(es)?\W+crosslets?|billets?|goutes?|be[zs]ants?|plates?|ogress(es)?|pellets?|gunstones?|torteaux?|hurts?|golpes?|pome(i?s)?|lions?\W+(passant|rampant)|pallets?|fir\W+twigs?|fusils?|mascles?|triangles?|canton|gyron|(in|de)?crescents?|escutcheons?|shakeforks?|escallops?|fountains?|areas?)\b"
t_MULLET=r"\bmullets?\b"

t_INVERTED=r"\b(inverted|bendwise(\W+sinister)?|reversed|contourny|fesswise|palewise|endorsed|cotised)\b"

t_ORDINARY=r"\b(fesse?|pale|cross|saltire|bend(lets?)?[ ]sinister|bend(lets?)?|piles?|chevron(el)?s?|base|label|bars?(\W+gemelles?)?|fret|flaunches|batons?|gore)\b"

t_PALL=r"\bpall\b"

# Chief is not an ordinary
t_CHIEF=r"\bchief\b"
t_ON=r"\bon\b"

t_LINETYPE=r"\b(plain|indented|dancetty|embattled|invected|engrailed|wavy|rayonny|dovetailed|raguly|nebuly|urdy|champaine)\b"

t_FURRY=r"\b(vairy\W+in\W+pale|vairy|counter\W+vairy)\b"

t_ALTERED=r"\b(fretty|ermined|masoned|estencelly)\b"

t_FUR=r"\b(vair.in.pale|vair|counter\W+vair|ermines?|erminois|pean|counter\W+ermine)\b"

t_PARTYPER=r"\b(party\W+per|per)\b"
t_FIMBRIATED=r"\b(fimbriated|voided)\b"
t_COUNTERCHARGED=r"\bcountercha[rn]ged\b"
t_DIRECTION=r"\b(dexter|sinister)\b"

def t_NUM(t):
    r"[0-9]+"
    t.value=int(t.value)
    return t


def t_NUMWORD(t):
    r"\b(one|two|three|four(teen)?|five|six(teen)?|seven(teen)?|eight(een)?|nine(teen)?|ten|eleven|twelve|thirteen|fifteen|twenty|I|II|III|IV|as[ ]many)\b"
    t.value={"one":1, "two":2, "three":3, "four":4, "five":5, "six":6,
             "seven":7, "eight":8, "nine":9, "ten":10, "eleven":11,
             "twelve":12, "thirteen":13, "fourteen":14, "fifteen":15,
             "sixteen":16, "seventeen":17, "eighteen":18, "nineteen":19,
             "twenty":20,"I":1,"II":2,"III":3,"IV":4,"as many":-1}[t.value]
    return t

t_A=r"\ban?\b"

t_WORD=r"\bpoints\b"
    # Word that's required but doesn't mean much.

def t_URL(t):
    r"<[^>]*>"
    t.value=t.value[1:-1].strip()
    return t

def t_NAME(t):
    r'\([a-z ]+\)s?'
    if t.value[-1]=='s':
        t.value=t.value[:-1]
    t.value=t.value[1:-1].strip()
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
    "gore": blazon.Gore,
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
    "fountains?" : (lambda *a: blazon.Roundel(tincture=treatment.Barry(color1="argent", color2="azure", linetype="wavy"))),
    "billets?": blazon.Billet,
    "annulets?": blazon.Annulet,
    "lozenges?": blazon.Lozenge,
    "mascles?" : blazon.Mascle,
    "areas?"  : blazon.BigRect,        # Just to fool around with.
    "fusils?" : blazon.Fusil,
    "triangles?": blazon.Triangle,
    "canton": blazon.Canton,            # There can be no more than one canton.
    "gyron": blazon.Gyron,
    "fleurs?\\W+de\\W+l[iy]s": (lambda *a: blazon.ExtCharge("fleur")),
    "goutes?": (lambda *a: blazon.ExtCharge("goute")),
    "cross(es)?.formy": (lambda *a: blazon.ExtCharge("formy")),
    "cross(es)?.pattee": (lambda *a: blazon.ExtCharge("formy")),
    "cross(es)?.pommee": (lambda *a: blazon.ExtCharge("pommee")),
    "cross(es)?.bottony": (lambda *a: blazon.ExtCharge("bottony")),
    "cross(es)?.humetty": (lambda *a: blazon.ExtCharge("humetty")),
    "cross(es)?.flory": (lambda *a: blazon.ExtCharge("flory")),
    "cross(es)?\W+crosslets?": (lambda *a: blazon.ExtCharge("crosscrosslet")),
    "mullets?": (lambda *a: blazon.ExtCharge("mullet",extension=a)),
    "escutcheons?": (lambda *a: blazon.ExtCharge("escutcheon")),
    "shakeforks?": (lambda *a: blazon.ExtCharge("shakefork")),
    r"semy\W+de\W+l[iy]s": (lambda *a: blazon.ExtCharge("fleur")),
    "go?utty": (lambda *a: blazon.ExtCharge("goute")),
    "fir\\W+twigs?": (lambda *a: blazon.ExtCharge("firtwig")),
    "crescents?": (lambda *a: blazon.ExtCharge("crescent")),
    "increscents?": (lambda *a: blazon.ExtCharge("crescent",
                                                 postprocessing=(lambda x: x.rotate(-90)))),
    "decrescents?": (lambda *a: blazon.ExtCharge("crescent",
                                                 postprocessing=(lambda x: x.rotate(90)))),
    "escallops?": (lambda *a: blazon.ExtCharge("escallop")),
    "billett?y": blazon.Billet,
    "crusilly": (lambda *a: blazon.ExtCharge("humetty")),
    "mulletty": (lambda *a: blazon.ExtCharge("mullet")),
    "bordure": blazon.Bordure,
    "orle": blazon.Orle,
    "tressure": blazon.Tressure,
    "double\\W+tressure": blazon.DoubleTressure,
    "paly": treatment.Paly,
    "pily": treatment.Pily,
    "barrypily": treatment.BarryPily,
    "bendypily": treatment.BendyPily,
    "barry": treatment.Barry,
    "chevronny": treatment.Chevronny,
    "chevronny\\W+inverted": (lambda *a,**k: treatment.Chevronny(inverted=True,*a,**k)),
    "bendy": treatment.Bendy,
    "bendy\\W+sinister": treatment.BendySinister,
    "gyronny": treatment.Gyronny,
    "gironny": treatment.Gyronny,
    "ermine": blazon.Ermine,
    "ermines": (lambda *a: treatment.Ermine("sable","argent")),
    "counter\\W+ermine": (lambda *a: treatment.Ermine("sable","argent")),
    "erminois": (lambda *a: treatment.Ermine("or","sable")),
    "pean": (lambda *a: treatment.Ermine("sable","or")),
    "ermined": treatment.Ermine,
    "masoned": treatment.Masoned,
    "estencelly": treatment.Estencelly,
    "fretty": treatment.Fretty,
    "vairy?\\W+in\\W+pale": treatment.VairInPale,
    "vairy": treatment.Vair,
    "per cross": treatment.PerCross,
    "per saltire": treatment.PerSaltire,
    # Parker mentions the following, but possibly it only applies
    # to the field, not to ordinaries.
    # Unfortunately, ATM it won't work, probably because the crummy lexer
    # can't handle both quartered in this sense, and quartered in the sense
    # of t_QUARTERLY.
    "per\\W+saltire\\W+quartered": treatment.PerSaltire,
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
    "in annulo": arrangement.InAnnulo,
    "in cross": arrangement.InCross,
    "in saltire": arrangement.InSaltire,
    "in chevron": arrangement.InChevron,
    "in pall": arrangement.InPall,
    "in pile": arrangement.InPall,      # So-so... too high.
    "in dexterchief": (lambda *a,**k: arrangement.InChief(side="dexter")),
    "in sinisterchief": (lambda *a,**k: arrangement.InChief(side="sinister")),
    "in dexterbase": (lambda *a,**k: arrangement.InBase(side="dexter")),
    "in sinisterbase": (lambda *a,**k: arrangement.InBase(side="sinister")),
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
                return lookupdict[k]
        return key

def show_grammar(all=dir()):
    all=filter((lambda x: x[0:2] == 't_'), all)
    all.sort()
    print all
    for f in all:
        obj=getattr(sys.modules[__name__],f)
        if type(obj)==str:
            print f, ":\t", obj
        else:
            print f, ":\t", obj.__doc__


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
