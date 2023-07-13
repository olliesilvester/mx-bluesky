module load python/3.10

if [ -d "./.venv" ]
then
rm -rf .venv
fi
mkdir .venv

python -m venv .venv
source .venv/bin/activate

pip install -e .[dev]

# Ensure we use a local version of dodal
if [ ! -d "../dodal" ]; then
  git clone git@github.com:DiamondLightSource/dodal.git ../dodal
fi

pip uninstall -y dodal
pip install -e ../dodal[dev]

tox -p