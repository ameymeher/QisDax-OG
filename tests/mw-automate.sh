#!/bin/bash
cd "$(dirname "$0")"
pyenv=`which python`

$pyenv bv.py
mv maxwidth.txt bv.cryo.maxwidth.txt

$pyenv dj.py
mv maxwidth.txt dj.cryo.maxwidth.txt

$pyenv ghz.py
mv maxwidth.txt ghz.cryo.maxwidth.txt

$pyenv grover_simpl.py
mv maxwidth.txt grover.cryo.maxwidth.txt

$pyenv simon.py
mv maxwidth.txt simon.cryo.maxwidth.txt

rm profile.txt
