#!/bin/bash
# (c) 2022 Anonymous Planet (Licensed under CC BY NC 4.0)

rm *.pdf &> /dev/null
rm *.html &> /dev/null
rm *.odt &> /dev/null
rm *.minisig &> /dev/null
rm *.asc &> /dev/null
rm sha256sum.txt &> /dev/null
rm b2sum.txt &> /dev/null
rm -r export/{.,}* &> /dev/null

true
