TESTS=tests

init:
	python setup.py develop
	pip install -r requirements.txt

test:
	py.test $(TESTS)

cov:
	py.test --cov=doc2dash --cov-report=term-missing $(TESTS)


.PHONY: serve init test cov
