ifneq (,$(wildcard .env))
	include .env
	export
endif

.PHONY: install env-build env-clean db-setup db-drop db-clean user-clean user-create user-setup user-add-permissions

# Make installation easy
install: db-setup user-setup env-clean env-build
	sudo systemctl restart postgresql

##############################################
#           Conda related commands           #
##############################################

# Build the conda environment
env-build:
	@echo "=== Building conda and pip environments ==="
	conda create --file environment.yaml
	conda run -n Route pip install dash-leaflet
	@echo "\n"

# Clean the conda environment
env-clean:
	@echo "=== Cleaning environment ==="
	- conda env remove -n Route
	@echo "\n"

###########################################
#           DB related commands           #
###########################################

db-setup: db-clean
	@echo "=== Creating PostgreSQL database $$DB_NAME ==="
	sudo createdb -h $${DB_HOST} -p $${DB_PORT} -U $${DB_ROOT_USER} $${DB_NAME}
	sudo psql -h $${DB_HOST} -p $${DB_PORT} -U $${DB_ROOT_USER} -d $${DB_NAME} -f schema.sql
	@echo "\n"

	@echo "=== Copying .env file into root directory ==="
	more .env +2 > ../.env
	@echo "\n"

# Drop the db from postgres
db-drop:
	@echo "=== Removing PostgreSQL database $$DB_NAME if it exists ==="
	- sudo dropdb -h $${DB_HOST} -p $${DB_PORT} -U $${DB_ROOT_USER} --if-exists $${DB_NAME}
	@echo "\n"

db-clean: db-drop user-clean
	@echo "=== Removing .env file from root directory ==="
	- rm ../.env
	@echo "\n"

#############################################
#           User related commands           #
#############################################

# Remove the user from the DB
user-clean:
	@echo "=== Removing user $$DB_USER" if it exists ===""
	- sudo -u $${DB_ROOT_USER} psql -c "DROP USER IF EXISTS $${DB_USER};"
	@echo "\n"

# Create a user
user-create:
	@echo "=== Creating user $$DB_USER ==="
	sudo -u $${DB_ROOT_USER} psql -c "CREATE USER $${DB_USER} WITH PASSWORD '$${PGPASSWORD}';"
	@echo "\n"

# (Re-)create a new user and set limited privileges
user-setup: user-clean user-create user-add-permissions

# Add permissions to the user
user-add-permissions:
	@echo "=== Granting Permissions ==="
	@echo "GRANT CONNECT ON DATABASE "$${DB_NAME}" TO $${DB_USER}; \
GRANT USAGE ON SCHEMA public TO $${DB_USER}; \
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO $${DB_USER}; \
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO $${DB_USER}; \
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $${DB_USER}; \
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO $${DB_USER};" \
	| sudo -u $${DB_ROOT_USER} psql -d $${DB_NAME}
	@echo "\n"