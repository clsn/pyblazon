import blazon
import sys
import re

class Globals:
   shield=None
   fieldcol=None
   ord=None
   ordcol=None
   line=None

   lookup={
	"vair": blazon.Vair,
	"counter.vair": blazon.CounterVair,
	"fesse?": blazon.Fesse,
	"pale" : blazon.Pale,
	"cross": blazon.Cross,
	"saltire": blazon.Saltire,
	"bend" : blazon.Bend,
	"pile": blazon.Pile,
	"chevron": blazon.Chevron,
	"bend sinister": blazon.BendSinister,
	"paly": blazon.Paly,
	"barry": blazon.Barry,
	"bendy":blazon.Bendy,
	"ermine": blazon.Ermine,
        # This is a bit of a hack...
	"ermines": (lambda *a: blazon.Ermine("sable","argent")),
	"erminois": (lambda *a: blazon.Ermine("or","sable")),
	"pean": (lambda *a: blazon.Ermine("sable","or")),
	"ermined": blazon.Ermine,
	"vairy?.in.pale": blazon.VairInPale,
	"vairy": blazon.Vair,
	"per cross": blazon.PerCross,
	"per saltire": blazon.PerSaltire,
	"per fesse?": blazon.PerFesse,
	"per pale": blazon.PerPale,
	"per bend": blazon.PerBend,
	"per bend sinister": blazon.PerBendSinister
   }


def lookup(key):
   # sys.stderr.write("Looking up: %s\n"%key)
   try:
      return Globals.lookup[key.lower()]
   except KeyError:
      key=key.lower()
      for k in Globals.lookup.keys():
         # Need the match to be anchored at the end too.
         m=re.match(k+"$",key)
         if m:
           # sys.stderr.write("Returning: %s\n"%Globals.lookup[m.re.pattern[:-1]])
           # have to chop off the $ we added.
           return Globals.lookup[m.re.pattern[:-1]]
      return None


%%
parser Blazonry:
   token A:		"(a|an)"
   token COLOR:		"(or|argent|sable|azure|gules|purpure|vert)"
   token ORDINARY:	"(fesse?|pale|cross|saltire|bend sinister|bend|pile|chevron)"
   token CHARGE:	"(chief|roundel|lozenge)"  # can't have "per chief"
   token LINEY:		"(paly|barry|bendy)"
   token LINETYPE:	"(plain|indented|dancetty|embattled|invected|engrailed|wavy)"
   token FUR:		"(vair.in.pale|vair|counter.vair|ermines?|erminois|pean)"
   token FURRY:		"(vairy.in.pale|vairy|ermined)"
   token NUM:		"\\d+"
   token PARTYPER:	"(party per|per)"
   ignore:		"\\W+"
   token END:		"\.?$"

   rule blazon:		treatment  
		{{ shield=blazon.Field(); shield.tincture=treatment }}
			[[A]
			grouporcharge {{ shield.charges.extend(grouporcharge) }}
			( ["and"] [A] charge 
				{{ shield.charges.append(charge) }})*]
			END {{ return shield }}




   rule group:		NUM charge {{ return blazon.ChargeGroup(int(NUM),charge); }}


   rule grouporcharge:	group {{ return group.elts }}
			| charge {{ return [charge] }}


   rule treatment:	COLOR  {{ return blazon.Tincture(COLOR) }}
	| PARTYPER ORDINARY COLOR {{ col1=COLOR }} "and" COLOR
   {{ return lookup("per "+ORDINARY)(col1,COLOR) }}
	| LINEY "of" NUM COLOR {{ col1=COLOR }} "and" COLOR
   {{ return blazon.__dict__[LINEY.capitalize()](int(NUM),col1,COLOR) }}
	| FUR {{ return lookup(FUR)() }}
        | FURRY {{ cols=() }} COLOR {{ col1=COLOR }} "and" COLOR {{ cols=(col1,COLOR) }} {{ return lookup(FURRY)(*cols) }}



   rule ordinary:	ORDINARY {{ return lookup(ORDINARY)() }}
                        | CHARGE {{ return lookup(CHARGE)() }}




   rule charge:		ordinary {{ res=ordinary }}
			["inverted" {{ res.invert() }}]
                        [LINETYPE {{ res.lineType=LINETYPE }}] 
			treatment {{ res.tincture=treatment; return res }}
			|
	"on" [A] charge {{ res=charge }} 
		[A] charge {{ res.charges.append(charge) ; return res }}

%%
if __name__=="__main__":
    shield=parse('blazon'," ".join(sys.argv[1:]))
    print shield


