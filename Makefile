TESTS=tests

init:
	python setup.py develop
	pip install -r dev-requirements.txt --use-mirrors
	mkdir -p test_data/sphinx
	mkdir -p test_data/pydoctor
	echo "\n\nNow fill test_data's data type directories with...well test data!"

test:
	py.test $(TESTS)

cov:
	py.test --cov=doc2dash --cov-report=term-missing $(TESTS)

pep8:
	py.test --pep8 doc2dash tests

pypi:
	python setup.py sdist upload --sign

.PHONY: serve init test cov pep8 pypi
