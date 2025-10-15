#!/usr/bin/env bash

cd src
python manage.py test --settings=armoreddjango.settings
pytest --ds=armoreddjango.settings --durations=0 -p no:warnings