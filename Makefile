tag ?= 3.13.2-alpine3.21

.PHONY: all
all: clean build deploy  ## Run all setup steps (default)

.PHONY: dev
dev: clean build-dev deploy  ## Run all setup steps for dev env (default)

# Help target to display available commands
.PHONY: help
help:  # Display this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)



.PHONY: build 
build: ## Run docker compose build
	docker compose build --build-arg BASE_TAG=$(tag)

.PHONY: build-dev
build-dev:
	docker compose build --build-arg DEV_TAG=$(tag)

# Target for running locally
.PHONY: deploy
deploy: ## docker compose up + follow logs
	docker compose up --detach --force-recreate
	docker compose logs -f

.PHONY: clean
clean: ## docker compose down
	docker compose down