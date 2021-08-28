# Library Back

This provides the backend for [the Library Project](library.illuminatus.be).

You can upload the barcode of a book, and it will add it to the database.

## Features

- Production-ready configuration for Static Files, Database Settings, Gunicorn, etc.
- Enhancements to Django's static file serving functionality via WhiteNoise.
- Latest Python 3.6 runtime environment.

## How to Use

To use this project, follow these steps:

1. Create your working environment.
2. Install Django (`$ pipenv install django`)
3. Create a new project using this template


## Deployment to Heroku

    $ git init
    $ git add -A
    $ git commit -m "Initial commit"

    $ heroku create
    $ git push heroku master

    $ heroku run python manage.py migrate

See also, a [ready-made application](https://github.com/heroku/python-getting-started), ready to deploy.

# Running

1. Enter your virtual environment (`pipenv shell`)
2. Execute migrations (`python manage.py migrate`)
3. Start Django (`python manage.py runserver`)

You can go to the admin page (`/admin`), or go to the specific endpoints (`books` and `genres`)

## Further Reading

- [Gunicorn](https://warehouse.python.org/project/gunicorn/)
- [WhiteNoise](https://warehouse.python.org/project/whitenoise/)
- [dj-database-url](https://warehouse.python.org/project/dj-database-url/)
