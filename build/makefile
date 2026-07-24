ifneq (,$(wildcard .env))
	include .env
	export
endif

.PHONY: db-setup db-clean env-build env-clean install

install: db-setup env-clean env-build

env-build:
	@echo "Building conda and pip environments."
	conda create --file environment.yaml
	conda run -n Route pip install dash-leaflet

env-clean:
	@echo "Cleaning environment."
	-conda env remove -n Route

db-setup: db-clean
	@echo "Creating PostgreSQL database $$DB_NAME with user $$DB_USER."
	sudo createdb -h $${DB_HOST} -p $${DB_PORT} -U $${DB_ROOT_USER} $${DB_NAME}
	sudo psql -h $${DB_HOST} -p $${DB_PORT} -U $${DB_ROOT_USER} -d $${DB_NAME} -f schema.sql

	@echo "Copying .env file into root directory."
	more .env +2 > ../.env

db-clean:
	@echo "Removing .env file from root directory."
	-rm ../.env

	@echo "Removing PostgreSQL databse $$DB_NAME if it already exists."
	-sudo dropdb -h $${DB_HOST} -p $${DB_PORT} -U $${DB_ROOT_USER} --if-exists $${DB_NAME}