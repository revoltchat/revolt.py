set dotenv-load := true

activate:
    source .venv/bin/activate

venv:
    python -m venv .venv
    just activate
    python -m pip install -r requirements.txt
    python -m pip install -r docs_requirements.txt

test: venv
    python test.py

build: venv
    python -m build

upload: venv
    python -m twine upload  dist/* -u $PYPI_USERNAME -p $PYPI_PASSWORD

lint:
    pyright . --venv-path .venv

coverage:
    pyright --lib --ignoreexternal --verifytypes revolt

docs:
    cd docs && make html
