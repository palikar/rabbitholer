NAME = rabbitholer
VERSION = $(shell grep "__version__\s*=\s*" rabbitholer/version.py | sed "s/__version__\s*=\s*'\(.*\)'/\1/g")

SNAPSHOT_NAME ?= $(NAME)-$(VERSION)-$(shell git rev-parse HEAD | cut -b 1-8).tar.gz

PYTHON ?= $(shell \
	     (python -c 'import sys; sys.exit(sys.version < "2.6")' && \
	      which python) \
	     || (which python3) \
	     || (python2 -c 'import sys; sys.exit(sys.version < "2.6")' && \
	         which python2))

ifeq ($(PYTHON),)
  $(error No suitable python found.)
endif

SETUPOPTS ?= '--record=install_log.txt'
PYOPTIMIZE ?= 1
FILTER ?= .


CWD = $(shell pwd)


TEST_PATHS =  $(shell find ./rabbitholer -mindepth 1 -maxdepth 1 ! -name '__pycache__')

TEST_FILES = $(shell find tests -mindepth 1 -maxdepth 1  -type f -not -name '__*')


all : clean test compile build

.PHONY: all


help:
	@echo 'make:              Test and compile rabbitholer.'
	@echo 'make install:      Install $(NAME)'
	@echo 'make compile:      Byte-compile all of the python files'
	@echo 'make build:        Builds the $(NAME) and generates egg file'
	@echo 'make clean:        Remove the compiled files (*.pyc, *.pyo)'
	@echo 'make test:         Test everything'
	@echo 'make snapshot:     Create a tar.gz of the current git revision'
	@echo 'make dist_test:    Release a new sdist to Test PyPI'

test: test_pylint test_flake8 test_pytest
	@echo "All test ran..."

test_pytest:
	@echo "Running pytest..."
	python -m pytest $(TEST_FILES)

test_pylint:
	@echo "Running pylint..."
	pylint $(TEST_PATHS)

test_flake8:
	@echo "Running flake8..."
	flake8 $(TEST_PATHS)

snapshot:
	git archive --prefix='$(NAME)-$(VERSION)/' --format=tar HEAD | gzip > $(SNAPSHOT_NAME)

todo:
	@grep --color -Ion '\(TODO\|XXX\).*' -r ./rabbitholer

compile: clean
	PYTHONOPTIMIZE=$(PYOPTIMIZE) $(PYTHON) -m compileall -q ./rabbitholer

clean:
	@echo 'Cleaning all generated files'
	find ./rabbitholer -regex .\*\.py[co]\$$ -delete
	find ./rabbitholer -depth -name __pycache__ -type d -exec rm -r -- {} \;
	rm -rf ./build
	rm -rf ./rabbitholer.egg-info
	rm -rf ./dist
	rm -rf ./install_log.txt
	rm -rf ./htmlcov

build: compile
	@echo 'Building the project'
	$(PYTHON) setup.py build

dist_test:
	$(PYTHON) setup.py sdist bdist_wheel;
	$(PYTHON) -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

dist:
	$(PYTHON) setup.py sdist bdist_wheel;
	$(PYTHON) -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

install: build
	@echo 'Installing on the system'	
	$(PYTHON) setup.py install $(SETUPOPTS)
		--optimize=$(PYOPTIMIZE)

coverage_html:
	py.test --cov=rabbitholer --cov-report=html $(TEST_FILES)

coverage:
	py.test --cov=rabbitholer $(TEST_FILES)
