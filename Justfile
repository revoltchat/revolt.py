set dotenv-load := true

test:
    python test.py

build:
    rm -rf dist/*
    python -m build

upload:
    python -m twine upload  dist/* -u $PYPI_USERNAME -p $PYPI_PASSWORD

lint:
    pyright . --venv-path .venv

coverage:
    pyright --lib --ignoreexternal --verifytypes revolt

docs:
    cd docs && make html
