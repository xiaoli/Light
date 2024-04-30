#!/bin/bash
cd /srv/www/Ultron
source ./venv/bin/activate
cd ultron
python manage.py avgpe --settings=ultron.settings.prod

dt=$(date '+%d/%m/%Y %H:%M:%S');
echo "$dt" >> /srv/www/test_pe.log
