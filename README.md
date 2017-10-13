# Django Boilerplate
This is a simple Boilerplate for starting Django projects. It includes a user account app containing profile, account settings and profile editor pages. it's theme is based on Bootstrap v4 and includes JQuery and FontAwesome.

## Installation
1. Clone Repository.
2. Install "sorl-thumbnail" for avatar thumbnails and "django-widget-tweaks" for improving bootstrap integration with forms.
```
pip install git+git://github.com/mariocesar/sorl-thumbnail@v12.3
pip install django-widget-tweaks
```
3. Migrate
python manage.py makemigrations account
python manage.py migrate
Note: make sure that you are using latest version of Django. I've used Django 1.11 with Python 3.5 for this version.
4. Rename the "app" directory to your app's name and change it in `INSTALLED_APPS`.

## Documentation
In app directory create a directory named `static` to hold your JS,CSS, fonts and image files.
In app directory create a directory named `template` for your template files.
you can extend based on "base.html" to have standard navigation or "base-clean-header.html" to have an empty template.
```
{% extends "base.html" %}
```
Edit "project/templates/base.html" to change navigation or general design of main container.

--------
## Copyright
This project is published under [MIT License]. you are free to use or change it in any way you like.

## Contrubutions
Feel free to fork the project and push improvements.

## About Developer
This project is created by [Towhid](http://TheRational.ist/ "The Rationalist").
