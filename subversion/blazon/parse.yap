import blazon
import sys

class Globals:
   shield=None
   fieldcol=None
   ord=None
   ordcol=None
   line=None

%%
parser Blazonry:
   token A:		"(a|an)"
   token COLOR:		"(or|argent|sable|azure|gules|purpure|vert)"
   token ORDINARY:	"(fesse|pale|cross|saltire|bend|pile|chevron)"
   token CHARGE:	"(chief|roundel|lozenge)"  # can't have "per chief"
   token BENDSINISTER:	"bend sinister"
   token LINEY:		"(paly|barry|bendy)"
   token LINETYPE:	"(plain|indented|dancetty|embattled|invected|engrailed|wavy)"
   token NUM:		"\\d+"
   ignore:		"\\W+"
   token END:		"$"

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
	| "per" ORDINARY COLOR {{ col1=COLOR }} "and" COLOR
   {{ return blazon.__dict__["Per"+ORDINARY.capitalize()](col1,COLOR) }}
	| LINEY "of" NUM COLOR {{ col1=COLOR }} "and" COLOR
   {{ return blazon.__dict__[LINEY.capitalize()](int(NUM),col1,COLOR) }}



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


