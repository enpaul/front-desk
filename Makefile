# Keyosk makefile for building and deployment prep

VERSION  = $(shell cat pyproject.toml | grep "^version =" | cut -d "\"" -f 2)
PROJECT  = keyosk

.PHONY: help docs
# Put it first so that "make" without argument is like "make help"
# Shamelessly lifted from here:
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## List Makefile targets
	$(info Makefile documentation)
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

tox:
	poetry run tox

clean-tox:
	rm --recursive --force ./.mypy_cache
	rm --recursive --force ./.tox
	rm --force .coverage

clean-py:
	rm --recursive --force ./dist
	rm --recursive --force ./build
	rm --recursive --force ./*.egg-info
	rm --recursive --force ./**/__pycache__

clean-docs:
	rm --recursive --force ./docs/_build
	rm --force ./docs/$(PROJECT)*.rst
	rm --force ./docs/modules.rst

clean: clean-tox clean-py clean-docs; ## Clean up all temp build/cache files and directories

wheel: ## Build Python binary wheel package for distribution
	poetry build --format wheel

source: ## Build Python source package for distribution
	poetry build --format sdist

test: clean-tox ## Run the project testsuite
	poetry run tox

publish: clean tox wheel source ## Build and upload to pypi (requires $PYPI_API_KEY be set)
	@poetry publish --username __token__ --password $(PYPI_API_KEY)

docs: clean-docs ## Generate documentation with Sphinx
	poetry run tox -e docs
