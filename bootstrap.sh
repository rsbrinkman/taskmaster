#!/usr/bin/env bash
rm -rf ./venv && python virtualenv.py ./venv
./venv/bin/pip install -r requirements.txt
source ./venv/bin/activate
