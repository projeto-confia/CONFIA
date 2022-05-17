#!/bin/bash -l

cd ${AUTOMATA_PATH}
nohup ./.venv/bin/python -m src > logs/nohup.out &
