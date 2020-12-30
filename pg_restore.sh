#!/bin/bash

gunzip < $1 | docker exec -i postgres psql -U admin -d confia

