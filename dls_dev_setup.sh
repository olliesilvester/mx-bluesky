#module load python/3.10

if [ -d "./.venv" ]
then
rm -rf .venv
fi
mkdir .venv

python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

tox -p