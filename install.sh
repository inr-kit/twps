pip uninstall tsp;

pip install -e . --user

python setup.py clean
rm dist/*

python setup.py sdist


