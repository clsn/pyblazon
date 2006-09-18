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
	"bendy":blazon.Bendy
   }


def lookup(key):
   try:
      return Globals.lookup[key.lower()]
   except KeyError:
      key=key.lower()
      for k in Globals.lookup.keys():
         m=re.match(k,key)
         if m:
           return Globals.lookup[m.re.pattern]
      return None


%%
parser Blazonry:
   token A:		"(a|an)"
   token COLOR:		"(or|argent|sable|azure|gules|purpure|vert)"
   token PARTYPER:      "(party per|per)"
   token ORDINARY:	"(fesse|pale|cross|saltire|bend|pile|chevron)"
   token CHARGE:	"(chief|roundel|lozenge)"  # can't have "per chief"
   token BENDSINISTER:	"bend sinister"
   token LINEY:		"(paly|barry|bendy)"
   token LINETYPE:	"(plain|indented|dancetty|embattled|invected|engrailed|wavy)"
   token FUR:		"(vair|counter.vair)"
   token NUM:		"\\d+"
   ignore:		"\\W+"
   token END:		"($|\.$)"

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
   {{ return blazon.__dict__["Per"+ORDINARY.capitalize()](col1,COLOR) }}
	| LINEY "of" NUM COLOR {{ col1=COLOR }} "and" COLOR
   {{ return blazon.__dict__[LINEY.capitalize()](int(NUM),col1,COLOR) }}
	| FUR {{ cols=() }} [COLOR {{ col1=COLOR }} "and" COLOR {{ cols=(col1,COLOR) }}] {{ return lookup(FUR)(*cols) }}
>>>>>>> .r8

## The following does not work. It results in:
##  * These tokens could be matched by more than one clause:
##  * LINEY
## Why?
#	| LINEY LINETYPE "of" NUM COLOR {{ col1=COLOR }} "and" COLOR
#   {{ res = blazon.__dict__[LINEY.capitalize()](int(NUM),col1,COLOR); res.lineType=LINETYPE; return res }}


   rule ordinary:	ORDINARY {{ return blazon.__dict__[ORDINARY.capitalize()]() }}
                        | CHARGE {{ return blazon.__dict__[CHARGE.capitalize()]() }}
			| BENDSINISTER {{ return blazon.BendSinister() }}




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


