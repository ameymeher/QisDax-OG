#!/bin/bash
cd "$(dirname "$0")"
pyenv=$(which python3)

$pyenv bv.py
mv maxwidth.txt bv.maxwidth.txt

$pyenv dj.py
mv maxwidth.txt dj.maxwidth.txt

$pyenv ghz.py
mv maxwidth.txt ghz.maxwidth.txt

$pyenv grover_simpl.py
mv maxwidth.txt grover.maxwidth.txt

$pyenv simon.py
mv maxwidth.txt simon.maxwidth.txt

rm profile.txt
