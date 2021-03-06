.PHONY: init lint test clean

init:
	python3 -m venv .venv
	source .venv/bin/activate; \
	pip3 install -e '.[dev]'; \

lint:
	source .venv/bin/activate; \
	python3 .ci/linter.py; \

test:
	source .venv/bin/activate; \
	pytest --cov=identityexchange; \

clean:
	rm -rf .venv/
	rm -rf IdentityExchange.egg-info/
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
