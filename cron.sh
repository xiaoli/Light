#!/bin/bash
cd /srv/www/Ultron
source ./venv/bin/activate
cd ultron
python manage.py updatestocks --settings=ultron.settings.prod
python manage.py updatehistory --settings=ultron.settings.prod
#股票和指数分开之后，股票在baostock上默认就有pe，而指数在理性人上也默认就有pe，不再需要单独update pe了
#python manage.py updatehistorype --settings=ultron.settings.prod
#python manage.py avgpe --settings=ultron.settings.prod

# updatehistory 是从数据库最后一天数据，更新到今天--往后更新
# importhistory 是从1990开始，更新到数据库最早的一天--往前更新

dt=$(date '+%d/%m/%Y %H:%M:%S');
echo "$dt" >> /srv/www/test.log