CC:=latexmk
OPTIONS:=-pdf
TARGET:=main

all:
	$(CC) $(OPTIONS) $(TARGET)

clean_partial:
	rm -f *.aux
	rm -f *.bbl
	rm -f *.blg
	rm -f *.dvi
	rm -f *.fdb_latexmk
	rm -f *.log
	rm -f *.out
	rm -f *.fls
	rm -f *.toc

clean: clean_partial
	rm -f *.pdf

fresh: clean all

zip: fresh
	$(MAKE) clean_partial
	zip archive.zip -r *
