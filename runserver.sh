#!/bin/bash
#
# DRIVER SCRIPT FOR RUNNING getDomainAge in Unix environment
# Author: Lakhya Jyoti Nath (ljnath) @ June 2019 - July 2021
#
# Prerequisite: Python 3.5/3.6 with symlink python3 pointing to correct python3.x binary
#

VIRTUAL_ENV=.venv

if [ -d "$VIRTUAL_ENV" ]; then
    source $VIRTUAL_ENV/bin/activate && python ./app.py --config config.json
else
    python3 -m venv --python=python3 $VIRTUAL_ENV
    source $VIRTUAL_ENV/bin/activate && pip install -r requirements.txt && clear && python ./app.py --config config.json
fi