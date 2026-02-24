CC:=latexmk
OPTIONS:=-pdf -xelatex
TARGET:=main

pdf:
	$(CC) $(OPTIONS) $(TARGET)

%:
	rm -f temp.tex
	cp main.tex temp.tex
	sed -i "s/\\\\input{main-body}//" 	temp.tex
	echo "\include{00A-header}" 		>> temp.tex
	echo "\begin{document}" 			>> temp.tex
	echo "\include{00B-acronyms}" 		>> temp.tex
	echo "\include{" $@ "}" 	>> temp.tex
	echo "\end{document}" 				>> temp.tex
	$(CC) $(OPTIONS) temp.tex

format:
	tex-fmt *.tex --config tex-fmt.toml

texcount:
	texcount 01-introduction.tex\
		02-elongated-bacteria.tex\
		03-cellular-raza.tex\
		05-bacterial-rods.tex\
		06-further-applications.tex\
		07-discussion.tex\
		08-conclusion.tex\
		20-supplement.tex

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
	rm -f *.dtx
	rm -f *.glo
	rm -f *.hd
	rm -f *.idx
	rm -f *.ins
	rm -f *.tdo
	rm -f *.xdv
	rm -f *.aux
	rm -f temp.tex
	rm -f archive.zip

clean: clean_partial
	rm -f *.pdf

fresh: clean all

book:
	$(CC) $(OPTIONS) $(TARGET)-book

zip: fresh book
	$(MAKE) clean_partial
	zip archive.zip -r *
