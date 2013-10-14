TESTS=tests

init:
	python setup.py develop
	pip install -r dev-requirements.txt
	mkdir -p test_data/sphinx
	mkdir -p test_data/pydoctor
	echo "\n\nNow fill test_data's data type directories with...well test data!"

test:
	py.test $(TESTS)

cov:
	py.test --cov=doc2dash --cov-report=term-missing $(TESTS)

upload:
	python setup.py sdist upload --sign
	python setup.py bdist_wheel upload --sign


.PHONY: init test cov upload
