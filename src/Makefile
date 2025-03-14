
# Constants
VENV_DIR ?= .venv
REQUIREMENTS_FILE = requirements.txt
TEST_DIR = tests

# Define paths and variables
PYTHON ?= python3
PIP ?= $(VENV_DIR)/bin/pip
SETTINGS_FILE ?= ../config/settings.toml

# Default target to run the program
all: setup run  ## Run setup, tests, and execute the program (default)

# Display available commands

.PHONY: help
help:  # Display this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: setup
setup: create-venv install-deps  ## Create virtual environment and install dependencies

.PHONY: create-venv
create-venv:  ## Create virtual environment if it doesn't exist
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "Virtual environment created."; \
	fi

.PHONY: install-deps
install-deps:  ## Install dependencies from requirements.txt
	@echo "Installing dependencies..."
	$(PIP) install --no-cache-dir -r $(REQUIREMENTS_FILE)

.PHONY: run
run:  ## Run the Python program with configurable settings file
	@echo "Running the program"
	@SETTINGS_FILE_FOR_DYNACONF='["$(SETTINGS_FILE)"]' $(VENV_DIR)/bin/python main.py

.PHONY: test
test:  ## Run unit tests in $(TEST_DIR)
	@echo "Running unit tests..."
	@PYTHONPATH=. $(VENV_DIR)/bin/pytest

.PHONY: deactivate
deactivate:  ## Deactivate the virtual environment
	@deactivate || echo "No active virtual environment to deactivate."

.PHONY: clean
clean:  ## Remove __pycache__, .venv, and test cache files
	@echo "Cleaning up __pycache__ and .venv"
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@rm -rf .pytest_cache
	@rm -rf .venv