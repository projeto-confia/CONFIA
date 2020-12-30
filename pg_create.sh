#!/bin/bash

docker exec -it postgres createdb -U admin confia

gunzip < db_script.sql.gz | docker exec -i postgres psql -U admin -d confia
