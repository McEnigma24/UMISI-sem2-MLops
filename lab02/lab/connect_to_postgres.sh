#!/bin/bash

export PGPASSWORD=postgres

psql --host=localhost --username=postgres
# psql --host localhost --username postgres --file data/services_table.sql

