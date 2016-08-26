#!/bin/sh

INSTALL_PATH=/srv
DJANGO_PROJECT=home_automation

# make directories
mkdir -p ${INSTALL_PATH}/${DJANGO_PROJECT}/

# copy program files
cp -r django_templates ${INSTALL_PATH}/${DJANGO_PROJECT}/
cp -r heat_control ${INSTALL_PATH}/${DJANGO_PROJECT}/

# copy configuration files
mkdir -p ${INSTALL_PATH}/${DJANGO_PROJECT}/home_automation/
cp home_automation/urls.py ${INSTALL_PATH}/${DJANGO_PROJECT}/home_automation/urls.py
cp home_automation/wsgi.py ${INSTALL_PATH}/${DJANGO_PROJECT}/home_automation/wsgi.py
cp manage.py ${INSTALL_PATH}/${DJANGO_PROJECT}/

# install static files
python manage.py collectstatic --noinput

# change owner and add read permission
chown -R www-data:www-data ${INSTALL_PATH}/${DJANGO_PROJECT}/
chown -R www-data:www-data ${INSTALL_PATH}/static/

# Set templates to be world readable in each application
chmod +r ${INSTALL_PATH}/${DJANGO_PROJECT}/django_templates/*/*.html