SH = bash

# Define the scripts
SCRIPTS = make.sh clean.sh

# Define the target
.PHONY: all guide clean

# Default target
all: clean guide

# Target to run script1
clean:
	$(SH) clean.sh

# Target to run script2
guide:
	$(SH) make.sh