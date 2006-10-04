#!/usr/bin/python
# -*- coding: latin-1 -*-

import lex
import re
import blazon
import sys
import tinctures

tokens=("COLOR","ORDINARY","CHARGE","LINEY","CHIEF","ON","COUNTERCHARGED",
        "LINETYPE","FUR","FURRY","NUM","NUMWORD","INVERTED","ALTERED",
        "PARTYPER","FIMBRIATED","QUARTERLY","AND","OF","A","WS")

# For some reason, things seem to work better when functions are defined,
# even if they don't do anything.  e.g. "vair" would overshadow "vairy"
# when they were just strings.

t_ignore=" \n\t"

def t_COLOR(t):
    r"(or|argent|sable|azure|gules|purpure|vert|tenné|tenne|tawny|sanguine|murrey|bleu[ ]celeste)"    
    return t

def t_AND(t):
    r"and"
    return t

t_OF=r"of"

def t_LINEY(t):
    r"(paly|barry|bendy(.sinister)?|gyronny)"
    return t

def t_QUARTERLY(t):
    r"(quarterly|quartered)"
    return t

def t_CHARGE(t):
    r"(roundel|lozenge|fleur.de.lis|cross.formy|cross.pattee|cross-crosslet|mullet)"
    return t

# Hmm.  How to handle "*in* a bordure..." ?
t_ORDINARY=r"(fesse?|pale|cross|saltire|bend[ ]sinister|bend|pile|chevron|bordure|base)"

# Chief is not an ordinary
t_CHIEF=r"chief"
t_ON=r"on"

t_LINETYPE=r"(plain|indented|dancetty|embattled|invected|engrailed|wavy|rayonny)"

def t_FURRY(t):
    r"(vairy.in.pale|vairy|counter.vairy)"
    return t

def t_ALTERED(t):
    r"(fretty|ermined)"
    return t

t_FUR=r"(vair.in.pale|vair|counter.vair|ermines?|erminois|pean)"

t_PARTYPER=r"(party[ ]per|per)"
t_FIMBRIATED=r"fimbriated"
t_INVERTED=r"inverted"
t_COUNTERCHARGED=r"countercha[rn]ged"

def t_A(t):
    r"an?"
    return t


def t_NUM(t):
    r"[0-9]+"
    t.value=int(t.value)
    return t


def t_NUMWORD(t):
    r"(one|two|three|four(teen)?|five|six(teen)?|seven(teen)?|eight(een)?|nine(teen)?|ten|eleven|twelve|thirteen|fifteen|twenty)"
    t.value={"one":1, "two":2, "three":3, "four":4, "five":5, "six":6,
             "seven":7, "eight":8, "nine":9, "ten":10, "eleven":11,
             "twelve":12, "thirteen":13, "fourteen":14, "fifteen":15,
             "sixteen":16, "seventeen":17, "eighteen":18, "nineteen":19,
             "twenty":20}[t.value]
    return t


def t_error(t):
    print "illegal character: %s"%t.value[0]
    t.skip(1)


lookupdict={
    "vair": tinctures.Vair,
    "counter.vairy?": tinctures.CounterVair,
    "fesse?": blazon.Fesse,
    "pale" : blazon.Pale,
    "cross": blazon.Cross,
    "saltire": blazon.Saltire,
    "bend" : blazon.Bend,
    "pile": blazon.Pile,
    "chevron": blazon.Chevron,
    "bend sinister": blazon.BendSinister,
    "chief": blazon.Chief,
    "base": blazon.Base,
    "roundel": blazon.Roundel,
    "lozenge": blazon.Lozenge,
    "fleur.de.lis": (lambda *a: blazon.ExtCharge("fleur")),
    "cross.formy": (lambda *a: blazon.ExtCharge("formy")),
    "cross.pattee": (lambda *a: blazon.ExtCharge("formy")),
    "cross-crosslet": (lambda *a: blazon.ExtCharge("crosscrosslet")),
    "mullet": (lambda *a: blazon.ExtCharge("mullet")),
    "bordure": blazon.Bordure,
    "paly": tinctures.Paly,
    "barry": tinctures.Barry,
    "bendy": tinctures.Bendy,
    "bendy.sinister": tinctures.BendySinister,
    "gyronny": tinctures.Gyronny,
    "ermine": blazon.Ermine,
    # This is a bit of a hack...
    "ermines": (lambda *a: tinctures.Ermine("sable","argent")),
    "erminois": (lambda *a: tinctures.Ermine("or","sable")),
    "pean": (lambda *a: tinctures.Ermine("sable","or")),
    "ermined": tinctures.Ermine,
    "fretty": tinctures.Fretty,
    "vairy?.in.pale": tinctures.VairInPale,
    "vairy": tinctures.Vair,
    "per cross": tinctures.PerCross,
    "per saltire": tinctures.PerSaltire,
    "per fesse?": tinctures.PerFesse,
    "per pale": tinctures.PerPale,
    "per bend": tinctures.PerBend,
    "per bend sinister": tinctures.PerBendSinister,
    "per chevron": tinctures.PerChevron,
    "quarterly": tinctures.PerCross,
    "quartered": tinctures.PerCross,
    "countercha[rn]ged": tinctures.Countercharged
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
