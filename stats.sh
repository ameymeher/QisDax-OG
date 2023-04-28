git clone git@gitlab.com:fmuelle/qisdax.git

cd qisdax

conda env create -f environment.yml
conda activate qisdax
pip3 install -r requirements.txt

git checkout profile

cd tests

git checkout aria-p
./automate.sh && ./mw-automate.sh

git checkout aria-s
./automate.sh && ./mw-automate.sh

git checkout cryo-s
./mw-automate.sh

git checkout cryo-p
./mw-automate.sh

git checkout profile
python3 consolidate.py

# Move `qisdax.json` to the directory containing the notebook
# Activate any environment with the `numpy`, `scipy` and `pandas` packages
# Run the notebook