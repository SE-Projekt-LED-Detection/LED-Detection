#!/bin/bash 
cat requirements.txt | while read requirement; do conda install python=3.8 --yes --force-reinstall -c conda-forge $requirement || pip install $requirement; done