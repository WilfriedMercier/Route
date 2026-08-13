#!/usr/bin/env bash

file="migration_v0.6.sql"

psql "$@" -f "$file"

exit 0