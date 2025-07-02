install:
	uv sync

dev:
	uv run python manage.py runserver

req:
	uv pip compile pyproject.toml -o requirements.txt

#_______________________________________________________________________________Lint

lint:
	uv run ruff check .

fix:
	uv run ruff check --fix

#_______________________________________________________________________________
create-db:
	uv run python create_db.py

collectstatic:
	uv run python manage.py collectstatic --noinput

migrate:
	uv run python manage.py migrate
	uv run python manage.py shell < create_superuser.py

dev-migrate:
	uv run manage.py makemigrations
	uv run manage.py migrate

build:
	./build-prod.sh

render-start:
	uv run gunicorn w_parser.wsgi

#_______________________________________________________________________________Test
test:
	uv run pytest

test-cov:
	uv run pytest --cov=w_parser

cover-html:
	uv run pytest --cov=w_parser --cov-report html
