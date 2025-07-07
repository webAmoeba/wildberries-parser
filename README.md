## Deployed:
[🌎 w-parser.webamoeba.ru](https://w-parser.webamoeba.ru/)

## Requirements:
To run this project, you need to have the following software installed:
- Python >=3.13.2
- Uv
- PostgreSQL
- Node.js 22.17.0 (for build css)

## Preparation:
Create .env file with code kind of:
```bash
webserver=127.0.0.1,localhost

DEBUG=True

SECRET_KEY=secret_key
DATABASE_URL=postgresql://admin:password@localhost:5432/db_name

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=password
```

Create a PostgreSQL user (or reuse an existing one) and a database using the parameters from DATABASE_URL.

## Installation:
To set up the project, navigate to the project directory and run the following commands:
```bash
make install
```
```bash
make migrate
```

## Local run:
```bash
make dev
```