#!/bin/sh

INSTALL_PATH=/srv
DJANGO_PROJECT=home_automation

# make directories
mkdir -p $INSTALL_PATH/$DJANGO_PROJECT/

# copy files
cp -r django_templates $INSTALL_PATH/$DJANGO_PROJECT/
cp -r heat_control $INSTALL_PATH/$DJANGO_PROJECT/
cp -r home_automation $INSTALL_PATH/$DJANGO_PROJECT/
cp manage.py $INSTALL_PATH/$DJANGO_PROJECT/

# install static files
python manage.py collectstatic --noinput

# change owner
chown -R www-data:www-data $INSTALL_PATH/$DJANGO_PROJECT/
chown -R www-data:www-data $INSTALL_PATH/static/

# disable DEBUG mode
sed -i -e 's/^DEBUG\ =\ True$/DEBUG\ =\ False/' $INSTALL_PATH/$DJANGO_PROJECT/home_automation/settings.py
