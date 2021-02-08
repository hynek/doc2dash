D=test_data/docsets

doc2dash:
	go build -o doc2dash ./cmd/doc2dash

run:
	go run -race ./cmd/doc2dash -d $(D) test_data/intersphinx/structlog -f
	# go run -race ./cmd/doc2dash -d $(D) test_data/intersphinx/sqlalchemy -f
	# go run -race ./cmd/doc2dash -d $(D) test_data/intersphinx/attrs -f

.PHONY: doc2dash run
