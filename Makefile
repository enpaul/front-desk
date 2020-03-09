# Keyosk makefile for building and deployment prep

VERSION           ?= $(shell cat pyproject.toml | grep "^version =" | cut -d "\"" -f 2)
DOC_FORMAT        ?= html
DOC_OPTIONS       ?=
DOC_SOURCEDIR      = ./docs
DOC_BUILDDIR       = ./docs/_build
DOC_PROJECT        = keyosk
DOCKER_CONTAINER   = keyosk

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
	rm -rf ./.mypy_cache
	rm -rf ./.tox
	rm -f .coverage
	find ./tests -type d -name __pycache__ -prune -exec rm -rf {} \;

clean-py:
	rm -rf ./dist
	rm -rf ./build
	rm -rf ./*.egg-info
	find ./keyosk -type d -name __pycache__ -prune -exec rm -rf {} \;

clean-docs:
	rm -rf $(DOC_BUILDDIR)
	rm -f $(DOC_SOURCEDIR)/$(DOC_PROJECT)*.rst
	rm -f $(DOC_SOURCEDIR)/modules.rst

clean: clean-tox clean-py clean-docs; ## Clean up all temp build/cache files and directories

wheel: ## Build Python binary wheel package for distribution
	poetry build --format wheel

source: ## Build Python source package for distribution
	poetry build --format sdist

build: clean-py tox; ## Test and build python distributions
	poetry build

docs: clean-docs ## Generate sphinx documentation, provide `DOC_FORMAT` to override default format of "html"
	poetry run tox -e docs
