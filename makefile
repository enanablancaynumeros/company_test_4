#!make

SHELL := /bin/bash

##############
# Docker commands for build, run, cleanups
##############

build:
	cd docker && \
	find . -type d -name __pycache__ -exec rm -r {} \+ && \
	docker-compose build

up: build
	cd docker && \
	docker-compose up -d --remove-orphans --scale api=2

db_up:
	cd docker && docker-compose up --remove-orphans -d postgres

docker_cleanup:
	docker image prune --force && \
	docker volume prune --force

docker_down:
	cd docker && \
	docker-compose down -v --remove-orphans

##############
# Testing commands
##############

tests: format static_analysis build
	cd docker && \
	BEHAVE_DEBUG_ON_ERROR=$(or $(BEHAVE_DEBUG_ON_ERROR),True) docker-compose run tests

##############
# Data migration commands and helpers
##############

alembic_new_migration_file: db_up
	cd api/inventory_api && \
	$(shell cat docker/.env docker/.localenv | xargs) POSTGRES_HOST=localhost flask create_database_and_upgrade && \
	$(shell cat docker/.env docker/.localenv | xargs) POSTGRES_HOST=localhost flask alembic_autogenerate_revision

##############
# static code analysis
##############

format:
	black --skip-string-normalization .

pep8_checks:
	flake8

safety_check:
	safety check

static_analysis: pep8_checks format_check safety_check

format_check:
	black --skip-string-normalization --check .