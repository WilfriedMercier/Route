# Route

Route is a python webb application built with Dash whose goal is to store, show, and share hike trails. The objective of Route is to be lightweight and easily deployable on private clouds.

## Installation

### Building from source

<details open>

<summary> 0. Pre-setup </summary>

To install the application, go to the `build` directory.

Whether you are installing with the easy install command or doing it step by step, you need first to create a `build/.env` file with the following content

```bash
export DB_ROOT_USER = postgres
export DB_NAME      = route_db
export DB_USER      = user
export PGPASSWORD   = password
export DB_HOST      = localhost
export DB_PORT      = 5432
```

`DB_ROOT_USER` must be a valid username that has privileges to create databases and grant permissions to other users. `DB_USER` and `PGPASSWORD` will be used to connect to the database and interact with it.

</details>

<details open>

<summary> 1. Easy install </summary>

You can install the application by running the following command

```bash
make install
```

</details>

<details>

<summary> 2. (Alternative) Step-by-step installation </summary>

Alternatively, it is possible to run the installation manually. The first step is to create the database which can be done with

```bash
make db-setup
```

**Warning**: `make db-setup` will remove any database with the same name for which the user has the `CREATEDB` privilege. This will erase any data in the database. Do a backup before running this command if you are unsure.

If necessary, one can just delete the database without creating a new one with the command

```bash
make db-clean
```

After that, the `.env` file from the `/build` directory is copied to the root directory so that the environment variables required to connect to the database are the same as those used for its creation. 

To setup the environment, one can use the command

```bash
make env-build
```

If necessary, it is possible to remove the environment first with

```bash
conda deactivate
make env-clean
```

**Note**: the dash-leaflet version available on conda-forge or through the official pip integration of conda is not compatible with the rest of the libraries. Therefore, the current version of dash-leaflet is installed through pip. This may break and, thus, change in the future.

Once the database and the environment are built, the application can be launched with

```bash
conda activate Route
python app.py
```

</details>

<details open>

<summary>Running the application in development mode</summary>

To run the application in development mode, simply use the following commands

```bash
conda activate Route
python app.py
```

</details>


## Adding users to the database

In the current version of the application, there is no way for a new user to sign-in so this step must be handled on-server by running the following code

```bash
python insert_user_into_db.py -u username
```

replacing `username` by the username to add to the users table and typing the associated password in the terminal.