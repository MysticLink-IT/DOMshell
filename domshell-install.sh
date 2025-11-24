#!/bin/bash

sudo apt-get update
sudo apt-get install python3 python3-django

django-admin startproject MLAdminServer
cd MLAdminServer
mkdir static
cp ../Resources/static/* ./static/
cp ../Resources/urls.py.main ./MLAdminServer/urls.py
python manage.py startapp DOMshell
cp ../Resources/settings.py ./MLAdminServer/
mkdir DOMshell/templates
cp ../Resources/templates/* DOMshell/templates/
cp ../Resources/*.py DOMshell/
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
