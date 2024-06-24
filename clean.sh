#!/bin/bash

rm -rf export/*.pdf &> /dev/null
rm -rf export/*.html &> /dev/null
rm -rf export/*.odt &> /dev/null
rm -rf export/*.minisig &> /dev/null
rm -rf export/*.asc &> /dev/null
rm -rf export/sha256sum.txt &> /dev/null
rm -rf export/b2sum.txt &> /dev/null
rm -rf export/* &> /dev/null
rm -rf *.md.asc &> /dev/null
rm -rf *.txt.asc &> /dev/null

true
