#!/bin/bash
cd "$(dirname "$0")"
count=16
pyenv=$(which python3)

for i in $(seq $count); do
    $pyenv bv.py
done
mv profile.txt bv.cryo.serial.txt

for i in $(seq $count); do
    $pyenv dj.py
done
mv profile.txt dj.cryo.serial.txt

for i in $(seq $count); do
    $pyenv ghz.py
done
mv profile.txt ghz.cryo.serial.txt

for i in $(seq $count); do
    $pyenv grover_simpl.py
done
mv profile.txt grover.cryo.serial.txt

for i in $(seq $count); do
    $pyenv simon.py
done
mv profile.txt simon.cryo.serial.txt
