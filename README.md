=====================
home_automation
=====================
home_automation currently offer only one application to manage a home heating system.
It work with a client (hc-client only available at this time).
The server is responsible for :
  * holding the configuration
  * offering a web GUI to the home heating system
  * deciding if a heater need to be activated or not given the rules and temperature records


============================
Install
============================
Launching 'sudo install.sh' will copy needed files in '/srv'
Then you need to set an application file for gunicorn in '/etc/gunicorn'.
An example file can be found in 'docs/'.


============================
Post-install
============================


============================
Requirements
============================
Software :
  * Python 2.7 or above
  * Django 1.6.1 or above
  * django rest-framework
  * highcharts.js
  * jquery-2.0.3.js
  * gunicorn
