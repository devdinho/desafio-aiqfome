#!/usr/bin/env bash

cd src
python manage.py test --settings=aiqfome.settings
pytest --durations=0 -p no:warnings