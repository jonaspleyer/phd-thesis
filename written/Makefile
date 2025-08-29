CC:=latexmk
OPTIONS:=-pdf
TARGET:=main

all:
	$(CC) $(OPTIONS) $(TARGET)

clean_partial:
	rm -f *.aux
	rm -f *.bbl
	rm -f *.bbl-SAVE-ERROR
	rm -f *.bcf
	rm -f *.bcf-SAVE-ERROR
	rm -f *.blg
	rm -f *-book.bcf
	rm -f *-book.lof
	rm -f *-book.lol
	rm -f *-book.lot
	rm -f *-book.run.xml
	rm -f *.fdb_latexmk
	rm -f *.fls
	rm -f *.lof
	rm -f *.log
	rm -f *.lol
	rm -f *.lot
	rm -f *.out
	rm -f *.pdf
	rm -f *.run.xml
	rm -f *.toc

clean: clean_partial
	rm -f *.pdf

fresh: clean all

book:
	$(CC) $(OPTIONS) $(TARGET)-book

zip: fresh
	$(MAKE) clean_partial
	zip archive.zip -r *
