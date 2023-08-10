#!/bin/bash

rm upload/*.minisig &> /dev/null
rm upload/*.asc &> /dev/null
rm upload/*.odt &> /dev/null
rm upload/*.pdf &> /dev/null
rm upload/*.txt &> /dev/null
rm upload/sha256sum.txt &> /dev/null
rm upload/b2sum.txt &> /dev/null
rm -r upload/{.,}* &> /dev/null

true
