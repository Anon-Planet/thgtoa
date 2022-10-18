#!/bin/bash

rm *.pdf &> /dev/null
rm *.html &> /dev/null
rm *.odt &> /dev/null
rm *.minisig &> /dev/null
rm *.asc &> /dev/null
rm sha256sum.txt &> /dev/null
rm b2sum.txt &> /dev/null
rm -r export/{.,}* &> /dev/null

true
