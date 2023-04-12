# drf-shop
This is an Internet shop app. Provides a simple web Api. In this project also used: Celery and Redis, aiogram, Swagger, Factory boy. 
All views covered by unit tests, also pytests were added.

## `Requirements`:
1. Python 3.10
2. Poetry 1.3.1
3. PostgreSQL 14.5


## `Prerequisites`:

### If using Docker:
1. From your project directory, start up your application by running docker compose up:

`docker compose up`

2. Use this command to create superuser:

`docker compose exec app python shop/manage.py createsuperuser`
