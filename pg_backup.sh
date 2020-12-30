#!/bin/bash

docker exec -t postgres pg_dump -d confia -c -U admin | gzip > ./pg_backup/dump_$(date +"%Y-%m-%d_%H_%M_%S").sql.gz
