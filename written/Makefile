CC:=latexmk
OPTIONS:=-pdf -xelatex
TARGET:=main

pdf:
	$(CC) $(OPTIONS) $(TARGET)

all: pdf book

clean_partial:
	rm -f *.aux
	rm -f *.bbl
	rm -f *.bbl-SAVE-ERROR
	rm -f *.bcf
	rm -f *.bcf-SAVE-ERROR
	rm -f *.blg
	rm -f *.fdb_latexmk
	rm -f *.fls
	rm -f *.lof
	rm -f *.log
	rm -f *.lol
	rm -f *.lot
	rm -f *.out
	rm -f *.run.xml
	rm -f *.toc

clean: clean_partial
	rm -f *.pdf

fresh: clean all

book:
	$(CC) $(OPTIONS) $(TARGET)-book

zip: fresh book
	$(MAKE) clean_partial
	zip archive.zip -r *
