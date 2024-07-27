#! /bin/bash -m

# Author.: Anonymous Planet
# License.: CC BY-NC 4.0

# Setup shell
# https://github.com/QubesOS/qubes-issues/issues/8343
# if the default shell ($SHELL) is zsh, else use bash

ifneq ($(shell echo $$SHELL | grep -q 'zsh' && echo zsh), zsh)
    SHELL := /bin/bash # using standard shell
else
    SHELL := /bin/zsh # else use zsh (Whonix)
endif

ifneq ($(shell which safe-rm), /usr/bin/safe-rm)
	RM := /usr/bin/rm # using standard rm
else
    RM := /usr/share/safe-rm/bin/rm # else use safe rm
endif

# Paths

BUILD_DIR				:= ./export
PANDOC=/usr/bin/pandoc
PANDOC_OPTIONS=--smart --standalone

SOURCE_DOCS := $(wildcard *.md)

EXPORTED_DOCS=\
 $(SOURCE_DOCS:.md=.html) \
 $(SOURCE_DOCS:.md=.pdf) \
 $(SOURCE_DOCS:.md=.docx) \
 $(SOURCE_DOCS:.md=.rtf) \
 $(SOURCE_DOCS:.md=.odt) \
 $(SOURCE_DOCS:.md=.epub)

PANDOC=/usr/bin/pandoc

PANDOC_OPTIONS=--standalone --metadata title="The Hitchhiker's Guide to Online Anonymity" -t context

PANDOC_HTML_OPTIONS=--to html5
PANDOC_PDF_OPTIONS=
PANDOC_DOCX_OPTIONS=
PANDOC_RTF_OPTIONS=
PANDOC_ODT_OPTIONS=
PANDOC_EPUB_OPTIONS=--to epub3

# TODO: Makefile flags

.PHONY: clean sigs docs

# target: cleanup

clean:
	-$(RM) -drf $(BUILD_DIR)/*
	-$(RM) -rf *sum*
	-$(RM) -rf *.md.asc
	-$(RM) -rf *.txt.asc
	-$(RM) -rf *.md.minisig
	-$(RM) -rf *.txt.minisig
	-$(RM) -f $(EXPORTED_DOCS)

# target: signatures

sigs:
	mkdir -p export
	./make.sh

# target: documentation

docs:
	%.html : %.md
	$(PANDOC) $(PANDOC_OPTIONS) $(PANDOC_HTML_OPTIONS) -o $@ $<

	%.pdf : %.md
	$(PANDOC) $(PANDOC_OPTIONS) $(PANDOC_PDF_OPTIONS) -o $@ $<

	%.docx : %.md
	$(PANDOC) $(PANDOC_OPTIONS) $(PANDOC_DOCX_OPTIONS) -o $@ $<

	%.rtf : %.md
	$(PANDOC) $(PANDOC_OPTIONS) $(PANDOC_RTF_OPTIONS) -o $@ $<

	%.odt : %.md
	$(PANDOC) $(PANDOC_OPTIONS) $(PANDOC_ODT_OPTIONS) -o $@ $<

	%.epub : %.md
	$(PANDOC) $(PANDOC_OPTIONS) $(PANDOC_EPUB_OPTIONS) -o $@ $<
