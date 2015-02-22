=====================
home_automation
=====================
home_automation currently offer only one application to manage a home heating system.
It work with a client (hc-client only available at this time).
The server is responsible for :
  * holding the configuration
  * offering a web GUI to the home heating system
  * deciding if a heater need to be activated or not given the rules and temperature records


=====================
Pre-install
====================
home_automation uses a database like any django application.
It is recommanded to create it before installing the application.
  * Create a mysql database 
    "mysql -u root -p"
    then inside the mysql shell :
      "CREATE DATABASE home_automation;"
      "GRANT ALL PRIVILEGES ON home_automation.* to home_automation@localhost IDENTIFIED BY 'secret_password';"
      "commit;"
      "quit;"
  * Extract the tarball into a directory
  * Put your 'secret_password' from previous steps into the file 'home_automation/settings.py'
  * Generate and store a SECRET_KEY in 'home_automation/settings.py' (key used to make hashes)
  * Launch this command to initialize the database : 'python manage.py syncdb heat_control'
  * If not asked at the previous step you can create a superuser with this command : 'python manage.py createsuperuser'


============================
Install
============================
Launch 'sudo install.sh', this will :
  * copy needed files into '/srv/home_automation'
  * launch 'python manage.py collectstatic' which will copy static files into '/srv/static/'
    (parameter STATIC_ROOT into 'home_automation/settings.py')
  * change the owner to 'www-data/www-data' for the two directories

Then you will need to set an application file for gunicorn in '/etc/gunicorn'.
An example file can be found in 'docs/'.


============================
Post-install
============================
Reload gunicorn : 'sudo service gunicorn restart'

Add this part into '/etc/nginx/sites-enabled/default' to serve static files :
    upstream django {
      server 127.0.0.1:8000;
    }
    server {
        location / {
                try_files $uri $uri/ @proxy_to_django;
        }
        location /static {
                alias /srv/static;
        }
        location @proxy_to_django {
                proxy_pass http://django;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }

If prefered you can use Apache instead :
  * activate mod_proxy : 'sudo a2enmod proxy proxy_http'
  * activate mod_alias : 'sudo a2enmod alias'
  * Allow override for 'srv' directory, in file '/etc/apache2/apache2.conf' :
        <Directory /srv/>
            Options Indexes FollowSymLinks
            AllowOverride None
            Require all granted
        </Directory>
  * Add thoses lines in '/etc/apache2/sites-enabled/default-ssl.conf'
           <Directory "/srv/static">
                   Options Indexes FollowSymLinks MultiViews
                   AllowOverride None
                   Order allow,deny
                   allow from all
           </Directory>
           Alias /static /srv/static

           <Proxy /hc/*>
                   Order deny,allow
                   Allow from all
           </Proxy>
           ProxyPreserveHost On
           ProxyPass /hc http://127.0.0.1:8000/hc

Reload nginx or apache : 'sudo service nginx reload' or 'sudo service apache2 reload'


============================
Configuration
===========================
  * Connect to "http://localhost/hc/admin/" with the superuser login and password
  * Create a new user named 'hc-client' and give him those rights :
        - Can add heater_history
        - Can add sensor
        - Can add heater
        - Can add temperature
  * Configure and launch 'hc-client' which will detect and populate some sensors and heaters
  * Configure and/or create sensors and heaters
  * Create rules and rulesets and link sensors to it


============================
Requirements
============================
Software :
  * Python 2.7 or above
  * Django 1.6.1 or above
  * django rest-framework
  * highcharts.js (provided in the repository for convenience)
  * jquery-2.0.3.js (provided in the repository for convenience)
  * gunicorn
