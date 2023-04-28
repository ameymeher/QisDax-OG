#!/bin/bash
cd "$(dirname "$0")"
pyenv=$(which python3)

$pyenv bv.py
mv maxwidth.txt bv.aria.maxwidth.txt

$pyenv dj.py
mv maxwidth.txt dj.aria.maxwidth.txt

$pyenv ghz.py
mv maxwidth.txt ghz.aria.maxwidth.txt

$pyenv grover_simpl.py
mv maxwidth.txt grover.aria.maxwidth.txt

$pyenv simon.py
mv maxwidth.txt simon.aria.maxwidth.txt

rm profile.txt
