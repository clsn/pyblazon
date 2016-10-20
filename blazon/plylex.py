#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        "URL","MULLET","NAME","ANNULO","GROUPS", "OVERALL", "ENDORSED",
        "TOKEN","TEXT",)

t_ignore=" \n\t"

word_RE_text={}
word_REs={
    'BORDURE':r"(bordure|orle|tressure|double\W+tressure)",
    'COLOR':r"((d')?or|argent|sable|azure|gules|purpure|vert|tenné|tenne|tawny|sanguine|murrey|bleu[ ]celeste|rose|copper|de[ ]larmes|de[ ]poix|de[ ]sang|d'huile|d'eau|proper|fieldless)",
    'AND':r"(and|&|between)",
    'BEZANTY':r"(be[sz]anty|platey|pellety|hurty|tortoilly)",
    'GROUPS':r"groups",
    'OF':r"of",
    'EACH':r"each",
    'CHARGED':r"charged",
    'WITH':r"with",
    'THE':r"the",
    'IN':r"in",
    'SEMY':r"semy",
    'LP':r"({|lp)",                 # leftparen
    'RP':r"(}|rp)",                 # rightparen
    'ANNULO':r"annulo",
    'SEMYDELIS':r"(billett?y|go?utty|crusilly|mulletty)",
    'WITHIN':r"within",
    'CARDINAL':r"(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|field|last)",
    'LINEY':r"(paly|barry|bendy(\W+sinister)?|g[iy]ronny|checky|lozengy|pily|chevronny(\W+inverted)?)",
    'QUARTERLY':r"quarterly",
    'CHARGE':r"(roundels?|annulets?|lozenges?|fleurs?.de.l[iy]s|cross(es)?.(formy|pattee|pommee|bottony|humetty|flory)|cross(es)?\W+crosslets?|billets?|goutes?|be[zs]ants?|plates?|ogress(es)?|pellets?|gunstones?|torteaux?|hurts?|golpes?|pome(i?s)?|lions?\W+(passant|rampant)|pallets?|fir\W+twigs?|fusils?|mascles?|triangles?|canton|gyron|(in|de)?crescents?|escutcheons?|shakeforks?|escallops?|fountains?|squares?|areas?)",
    'MULLET':r"mullets?",
    'INVERTED':r"(inverted|bendwise(\W+sinister)?|reversed|contourny|fesswise|palewise|enhanced|reduced|enlarged)",
    'ENDORSED':r"(endorsed|cotised)",
    'ORDINARY':r"(fesse?|(canadian\W+)?pale|cross|saltire|bend(lets?)?[ ]sinister|bend(lets?)?|piles?|chevron(el)?s?|base|label|bars?(\W+gemelles?)?|fret|flaunches|batons?|gore)",
    'PALL':r"pall",
    'CHIEF':r"chief",
    'ON':r"on",
    'LINETYPE':r"(plain|indented|dancetty|embattled|invected|engrailed|wavy|rayonny|dovetailed|raguly|nebuly|urdy|champaine|potenty)",
    'FURRY':r"(vairy(\W+in\W+pale|\W+en\+pointe|W+in\W+point)?|counter\W+vairy)",
    'ALTERED':r"(fretty|ermined|masoned|estencelly)",
    'FUR':r"(vair(\W+in\W+pale|\W+en\W+pointe|\W+in\W+point)?|counter\W+vair|ermines?|erminois|pean|counter\W+ermine)",
    'PARTYPER':r"(party\W+per|per)",
    'FIMBRIATED':r"(fimbriated|voided)",
    'COUNTERCHARGED':r"countercha[rn]ged",
    'DIRECTION':r"(dexter|sinister)",
    'NUMWORD':r"(one|two|three|four(teen)?|five|six(teen)?|seven(teen)?|eight(een)?|nine(teen)?|ten|eleven|twelve|thirteen|fifteen|twenty|I|II|III|IV|as[ ]many)",
    'A':r'an?',
    'WORD':r'points',
    'OVERALL':r'overall',
    }

def t_NUM(t):
    r"[0-9]+"
    t.value=int(t.value)
    return t

def t_URL(t):
    r"<[^>]*>"
    t.value=t.value[1:-1].strip()
    return t

def t_TEXT(t):
    r'"[^"]+"'
    t.value=t.value[1:-1]
    return t

def t_NAME(t):
    r'\([a-z ]+\)s?'
    if t.value[-1]=='s':
        t.value=t.value[:-1]
    t.value=t.value[1:-1].strip()
    return t

# Here's the weirdness of the new-style parser:

# PLY matches lexer tokens in the following order: first, it matches
# against all the tokens that are defined as functions, in the order
# specified in the file.  Then it goes against ones that are defined as
# variables, sorted in order of decreasing regexp length.  Now, it seems to
# me that what would be good is to match all the "special" words and
# anything else would be considered an "identifier" (to borrow a term from
# programming languages), basically a general charge that has to be looked
# up someplace.  The PLY documentation actually suggests that for such
# things it's best to have a rule that matches nearly everything, and
# inside that check the actual value of the token and adjust its type
# accordingly, if necessary.  So that's what I'm doing: that's what that
# big word_REs dictionary above is for: helps look up the token it's
# supposed to be.  Then the t_TOKEN rule below does all the lookups.
# Trouble is that some of my tokens are already multi-word (e.g. "bend
# sinister").  I can't have the TOKEN rule include spaces, or it gobbles up
# everything.  So instead I put all the multi-word tokens in individual
# functions above the TOKEN rule (so they are done first).  It's kind of
# ugly, I think; maybe there are better ways.

def t_COLOR(t):
    r"\b(bleu[ ]celeste|de[ ]poix|de[ ]larmes|de[ ]sang|d'or|[#][a-f0-9]{6})\b"
    return t

# No idea why "|[#]" at the end of the previous rule doesn't work, but it doesn't
def t_COLOR_b(t):
    r"[#][0-9a-f]{6}"
    t.type='COLOR'
    return t

def t_BORDURE(t):
    r"\b(double\W+tressure)\b"
    return t

def t_LINEY(t):
    r"\b(bendy\W+sinister)\b"
    return t

def t_CHARGE(t):
    r"\b(fleurs?\W+de\W+lis|cross(es)?\W+crosslets?|fir\W+twigs?|cross(es)?\W+(formy|pattee|pommee|bottony|humetty|flory)|lions?\W+(passant|rampant)|bars?(\W+gemelles?)?)\b|⚜"
    # Note that ⚜ must be outside the \b delims (which is why it isn't in the word_REs),
    # because it isn't a word char.
    return t

def t_INVERTED(t):
    r"\b(bendwise\W+sinister)\b"
    return t

def t_ORDINARY(t):
    r"\b(bend(lets?)?\W+sinister|canadian\W+pale)\b"
    return t

def t_FURRY(t):
    r"\b(vairy(\W+in\W+pale|\W+in\W+point|\W+en\W+pointe)?|counter\W+vairy)\b"
    return t

def t_FUR(t):
    r"\b(vair(\W+in\W+pale|\W+in\W+point|\W+en\W+pointe)?|counter\W+vair|counter\W+ermine)\b"
    return t

def t_SEMYDELIS(t):
    r"semy\W+de\W+l[iy]s"
    return t

def t_PARTYPER(t):
    r"\b(party\W+per)\b"
    return t

def t_NUMWORD(t):
    r"\bas\W+many\b"
    t.value= -1
    return t

def t_TOKEN(t):
    r"\b[a-z'-]+\b|⚜"            # Kludge for FDL!
    # Massive function that seeks out just about all the reserved words
    found='TOKEN'
    foundlen=0
    for kwd in word_REs:
        rexp=word_REs[kwd]
        mtch=rexp.match(t.value)
        # FAILS, for tokens with spaces in them.  Finding the longest one
        # doesn't work: e.g. "party per" sends back "party" as a TOKEN first.
        # So we have to do those above.
        if mtch:
            l=mtch.end()
            # print "l=",l,"kwd=",kwd
            if l>foundlen:
                foundlen=l
                found=kwd
    t.type=found
    # Special case:
    if found=="NUMWORD":
        t.value={"one":1, "two":2, "three":3, "four":4, "five":5, "six":6,
                 "seven":7, "eight":8, "nine":9, "ten":10, "eleven":11,
                 "twelve":12, "thirteen":13, "fourteen":14, "fifteen":15,
                 "sixteen":16, "seventeen":17, "eighteen":18, "nineteen":19,
                 "twenty":20,"I":1,"II":2,"III":3,"IV":4,
                 "i":1,"ii":2,"iii":3,"iv":4,"as many":-1}[t.value]
    # print "returning: ",t
    return t

def t_error(t):
    sys.stderr.write("illegal character: %s\n"%t.value[0])
    t.lexer.skip(1)


lookupdict={
    "vair": treatment.Vair,
    "vairy?\W+(en\W+pointe|in\W+point)": treatment.VairEnPointe,
    "counter.vairy?": treatment.CounterVair,
    "fesse?": blazon.Fesse,
    "canadian\\W+pale" : blazon.CanadianPale,
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
    "squares?": blazon.Square,
    "annulets?": blazon.Annulet,
    "lozenges?": blazon.Lozenge,
    "mascles?" : blazon.Mascle,
    "areas?"  : blazon.BigRect,        # Just to fool around with.
    "fusils?" : blazon.Fusil,
    "triangles?": blazon.Triangle,
    "canton": blazon.Canton,            # There can be no more than one canton.
    "gyron": blazon.Gyron,
    "fleurs?\\W+de\\W+l[iy]s": (lambda *a: blazon.ExtCharge("fleur")),
    "⚜": (lambda *a: blazon.ExtCharge("fleur")),
    "goutes?": (lambda *a: blazon.ExtCharge("goute")),
    "cross(es)?.formy": (lambda *a: blazon.ExtCharge("formy")),
    "cross(es)?.pattee": (lambda *a: blazon.ExtCharge("formy")),
    "cross(es)?.pommee": (lambda *a: blazon.ExtCharge("pommee")),
    "cross(es)?.bottony": (lambda *a: blazon.ExtCharge("bottony")),
    "cross(es)?.humetty": (lambda *a: blazon.ExtCharge("humetty")),
    "cross(es)?.flory": (lambda *a: blazon.ExtCharge("flory")),
    "cross(es)?\\W+crosslets?": (lambda *a: blazon.ExtCharge("crosscrosslet")),
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
    key=key.lower()
    for k in lookupdict:
        m=k.match(key)
        if m:
            return lookupdict[k]
    return key

def show_grammar(all=dir()):
    all=list(filter((lambda x: x[0:2] == 't_'), all))
    all.sort()
    print(all)
    for f in all:
        obj=getattr(sys.modules[__name__],f)
        if type(obj)==str:
            print(f, ":\t", obj)
        else:
            print(f, ":\t", obj.__doc__)
    # Most of the tokens are now in word_REs...
    for k in word_RE_text:
        print(k, ":\t", word_RE_text[k])


# Compile all the REs.
for kwd in word_REs:
    rexp=word_REs[kwd]
    # Save the text for the show_grammar function, otherwise it can't
    # print them out.
    word_RE_text[kwd]=rexp
    word_REs[kwd]=re.compile(r'\b'+rexp+r'\b')
# Compile the lookupdict too
newdict={}
for kwd in lookupdict:
    # has to match at the end also.
    newdict[re.compile(kwd+'$')]=lookupdict[kwd]
lookupdict=newdict

lex.lex()

if __name__ == "__main__":
    line=sys.stdin.readline()
    while line:
        lex.input(line)
        while 1:
            tok=lex.token()
            if not tok: break
            print(tok)
        line=sys.stdin.readline()
