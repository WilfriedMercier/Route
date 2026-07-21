# Route

Route is a python webb application built with Dash whose goal is to store, show, and share hike trails. The objective of Route is to be lightweight and easily deployable on private clouds.

## Installation

### Building from source

<details open>

<summary> 0. Pre-setup </summary>

Whether you are installing with the easy install command or doing it step by step, you need first to update the `.env` file and modify the following lines with your username and password

```bash
export DB_USER    = username
export PGPASSWORD = password
```

These environment variables will be used every time the application connects to the database.

If the user does not already exist in PostgreSQL, you will have to create it first and grant it the privilege to create databases. You can do so by first connecting to psql with

```console
sudo -i -u postgres psql
```

and then run the following commands, replacing `username` and `password` with your values,

```pgsql
CREATE USER username WITH PASSWORD 'password';
ALTER USER "username" CREATEDB;
```

</details>

<details open>

<summary> 1. Easy install </summary>

You can install the application by running the following command

```console
make install
```

To run the application, use

```console
conda activate Route
python app.py
```

</details>

<details>

<summary> 2. (Alternative) Step-by-step installation </summary>

Alternatively, it is possible to run the installation manually. The first step is to create the database which can be done with

```console
make db-setup
```

**Warning**: `make db-setup` will remove any database with the same name for which the user has the `CREATEDB` privilege. This will erase any data in the database. Do a backup before running this command if you are unsure.

If necessary, one can just delete the database without creating a new one with the command

```console
make db-clean
```

After that, the `.env` file from the `/build` directory is copied to the root directory so that the environment variables required to connect to the database are the same as those used for its creation. 

To setup the environment, one can use the command

```console
make env-build
```

If necessary, it is possible to remove the environment first with

```console
conda deactivate
make env-clean
```

**Note**: the dash-leaflet version available on conda-forge or through the official pip integration of conda is not compatible with the rest of the libraries. Therefore, the current version of dash-leaflet is installed through pip. This may break and, thus, change in the future.

Once the database and the environment are built, the application can be launched with

```console
conda activate Route
python app.py
```

</details>

## Adding users to the database

In the current version of the application, there is no way for a new user to sign-in so this step must be handled on-server by running the following code

```console
python insert_user_into_db.py -u username
```

replacing `username` by the username to add to the users table and typing the associated password in the terminal.