#!/bin/bash
cd /srv/www/Ultron
source ./venv/bin/activate
cd ultron
python manage.py updatestocks --settings=ultron.settings.prod
python manage.py updatehistory --settings=ultron.settings.prod
python manage.py updatehistorype --settings=ultron.settings.prod
python manage.py avgpe --settings=ultron.settings.prod

dt=$(date '+%d/%m/%Y %H:%M:%S');
echo "$dt" >> /srv/www/test.log