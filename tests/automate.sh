#!/bin/bash
cd "$(dirname "$0")"
count=16
pyenv=$(which python3)

for i in $(seq $count); do
    $pyenv bv.py
done
mv profile.txt bv.aria.parallel.txt

for i in $(seq $count); do
    $pyenv dj.py
done
mv profile.txt dj.aria.parallel.txt

for i in $(seq $count); do
    $pyenv ghz.py
done
mv profile.txt ghz.aria.parallel.txt

for i in $(seq $count); do
    $pyenv grover_simpl.py
done
mv profile.txt grover.aria.parallel.txt

for i in $(seq $count); do
    $pyenv simon.py
done
mv profile.txt simon.aria.parallel.txt
