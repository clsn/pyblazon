all: xmlgrammar.py grammar.txt lexitems.txt

xmlgrammar.py: plyyacc.py plylex.py makexmlgrammar.py
	python ./makexmlgrammar.py > xmlgrammar.py

grammar.txt: plyyacc.py
	python -c 'import plyyacc; plyyacc.show_grammar()' > grammar.txt

lexitems.txt: plylex.py
	python -c 'import plyyacc; import plylex; plylex.show_grammar()' > lexitems.txt

