all: xmlgrammar.py grammar.txt lexitems.txt

xmlgrammar.py: plyyacc.py plylex.py makexmlgrammar.py
	python ./makexmlgrammar.py > xmlgrammar.py

grammar.txt: plyyacc.py
	python -c 'import plyyacc; plyyacc.show_grammar()' > grammar.txt

lexitems.txt: plylex.py
	python -c 'import plyyacc; import plylex; plylex.show_grammar()' > lexitems.txt

# Sometimes (not often) I wish I knew my way around Makefiles better.
# This isn't yet a proper, complete distribution.
FILES=plylex.py plyyacc.py blazon.py treatment.py arrangement.py makexmlgrammar.py gen.py pathstuff.py data SVGdraw.py
pyblazon.tar.gz: $(FILES)
	tar czfv pyblazon.tar.gz $(FILES)

.PHONY: clean veryclean

clean:
	rm -f *.pyc parser.out parsetab.py

veryclean: clean
	rm -f grammar.txt xmlgrammar.py lexitems.txt
