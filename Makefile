VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
FLASK = $(VENV)/bin/flask

.PHONY: all setup run clean

all: setup

setup: $(VENV)/bin/activate

$(VENV)/bin/activate: setup.py
	python3 -m venv $(VENV)
	$(PIP) install -e .

run:
	$(PYTHON) app.py

clean:
	rm -rf $(VENV)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
