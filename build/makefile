ifneq (,$(wildcard .env))
	include .env
	export
	_ENV_FOUND := true
else
	DB_NAME    ?= route_db
	DB_USER    ?= admin
	PGPASSWORD ?= admin
	DB_HOST    ?= localhost
	DB_PORT    ?= 5432	
	_ENV_FOUND := false
endif

.PHONY: db-setup db-clean

db-setup: info db-clean
	@echo "Creating PostgreSQL database $$DB_NAME with user $$DB_USER."
	createdb -h $${DB_HOST} -p $${DB_PORT} -U $${DB_USER} $${DB_NAME}
	psql -h $${DB_HOST} -p $${DB_PORT} -U $${DB_USER} -d $${DB_NAME} -f schema.sql

db-clean:
	@echo "Removing PostgreSQL databse $$DB_NAME if it already exists."
	-dropdb -h $${DB_HOST} -p $${DB_PORT} -U $${DB_USER} --if-exists $${DB_NAME}

# Describe where the environment variables come from
info:
	@if $(_ENV_FOUND); then \
		echo "Using environment variables from .env file."; \
	else \
		echo "Using environment variables from the MakeFile and the command line."; \
	fi
