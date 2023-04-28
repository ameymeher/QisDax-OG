#!/bin/bash
cd "$(dirname "$0")"
count=16
pyenv='/home/kjbadrik/anaconda3/envs/qisdax/bin/python3'

for i in $(seq $count); do
    $pyenv bv.py
done
mv profile.txt bv.data.txt

for i in $(seq $count); do
    $pyenv dj.py
done
mv profile.txt dj.data.txt

for i in $(seq $count); do
    $pyenv ghz.py
done
mv profile.txt ghz.data.txt

for i in $(seq $count); do
    $pyenv grover_simpl.py
done
mv profile.txt grover.data.txt

for i in $(seq $count); do
    $pyenv simon.py
done
mv profile.txt simon.data.txt
