.PHONY: init test install clean

init:
	python3.6 -m venv .venv
	source .venv/bin/activate; \
	pip3 install -e '.[dev]'; \

test:
	if [ ! -d ".venv/" ]; then init; fi
	source .venv/bin/activate; \
	pytest; \

install:
	python3.6 -m venv .venv
	source .venv/bin/activate; \
	python3.6 setup.py install; \

clean:
	rm -rf .venv/
	rm -rf IdentityExchange.egg-info/
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/