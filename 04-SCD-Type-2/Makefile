include ../../../make.inc

.PHONY: test clean

test: pytest-and-write-output

clean:
	rm -f *.parquet *.csv
	find . -type d -name __pycache__ -exec rm -rf {} +
