# Route

A small web app used to store, display, and share hiking trails

## Installation

### Building from source

#### 0. Pre-setup

Whether you are installing with the easy install command or doing it step by step, you need first to update the `.env` file and modify the following lines with your username and password

```
export DB_USER     = username
export PGPASSWORD  = password
```

These environment variables will be used every time the application connects to the database.

If the user does not already exist you will have to create it first and grant it the privilege to create databases. You can do so by first connecting to psql with the command

```
sudo -i -u postgres psql
```

and then run the following commands, replacing `username` and `password` with your values

```
CREATE USER username WITH PASSWORD 'password';
ALTER USER "username" CREATEDB;
```

#### 1. Easy install

You can install the application by running the following command

```
make install
```

To run the application, do not forget to activate the environment with

```
conda activate Route
```

#### 2. (Alternative) Step-by-step installation

Alternatively, it is possible to run the installation manually. The first step is to create the database which can be done with

```
make db-setup
```

**Warning**: `make db-setup` will remove any database with the same name for which the user has the `CREATEDB` privilege. Do a backup of your database before running this command.

If necessary, one can just delete the database without creating a new one with the command

```
make db-clean
```

XXX TBD bellow

To install the application, run

```
conda create --file environment.yaml
```

At the moment, there is a bug with the dsah-leaflet version available on conda-forge. Instead, it must be installed with

```
pip install dash-leaflet
```