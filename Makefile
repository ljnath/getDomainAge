# Makefile for getDomainAge
# author - ljnath https://ljnath.com}

# target to run all pytest
test:
	pytest -v

test-cov:
	pytest -v --cov=getDomainAge --cov-report=xml

# target to perform lint check using pytest-flake8
lint:
	pytest --flake8 -v

# target to perform forceful lint check using pytest-flake8 by cleaning pytest cache
lint-force:
	pytest --cache-clear --flake8 -v
