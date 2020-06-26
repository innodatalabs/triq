.PHONY: docs docker test

all: wheel

ON_TAG := $(shell git tag --points-at HEAD)

test:
	pip install pytest
	PYTHONPATH=. pytest

wheel: test
	rm -rf build dist
	pip install wheel
	python setup.py bdist_wheel

publish: wheel
	pip install twine
	twine upload dist/triq*.whl -u __token__ -p $(PYPI_TOKEN)

maybe_publish: wheel
ifneq ($(ON_TAG),)
	pip install twine
	twine upload dist/triq*.whl -u __token__ -p $(PYPI_TOKEN)
endif

docs:
	(cd docs; make html)
