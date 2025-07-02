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

collectstatic:
	uv run python manage.py collectstatic --noinput

migrate:
	uv run python manage.py migrate
	uv run python manage.py shell < create_superuser.py

dev-migrate:
	uv run manage.py makemigrations
	uv run manage.py migrate

build:
	./build.sh

render-start:
	uv run gunicorn task_manager.wsgi

#_______________________________________________________________________________Test
test:
	uv run pytest

test-cov:
	uv run pytest --cov=task_manager

cover-html:
	uv run pytest --cov=task_manager --cov-report html
