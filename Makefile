tag ?= 3.13.2-alpine3.21

.PHONY: all
all: clean build deploy  ## Run all setup steps (default)

.PHONY: dev
dev: clean build-dev deploy  ## Run all setup steps (default)

# Help target to display available commands
.PHONY: help
help:
	@echo "Usage: make [TARGET] [EXTRA_ARGUMENTS]"
	@echo ""
	@echo "Targets:"
	@echo "  build                  Build new image"
	@echo "  test                   Build new image"
	@echo "  deploy                 Start container via Docker Compose"
	@echo "  clean                Delete container via Docker Compose, remove images"
	@echo "Examples:"
	@echo "  make deploy"
	@echo "  make clean"

# Target for building new image
.PHONY: build
build:
	docker compose build --build-arg BASE_TAG=$(tag)

.PHONY: build-dev
build:
	docker compose build --build-arg DEV_TAG=$(tag)

# Target for running locally
.PHONY: deploy
deploy:
	docker compose up --detach --force-recreate
	docker compose logs -f

.PHONY: clean
clean:
	docker compose down 
