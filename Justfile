set dotenv-load := true

test:
    python test.py

build:
    rm -rf dist/*
    python -m build

upload:
    python -m twine upload  dist/*

lint:
    pyright .

coverage:
    pyright --ignoreexternal --verifytypes revolt

docs:
    cd docs && make html
