prod-install:
	uv sync

install:
	uv sync
	npm i

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
	uv run manage.py makemigrations w_parser
	uv run manage.py migrate

build:
	./build.sh

render-start:
	uv run gunicorn w_parser.wsgi

#_______________________________________________________________________________Test
test:
	uv run pytest

test-cov:
	uv run pytest --cov=w_parser

cover-html:
	uv run pytest --cov=w_parser --cov-report html

#_______________________________________________________________________________CSS
css-build:
	npx postcss w_parser/static/css/dev/main.css --no-map -o w_parser/static/css/main.css

#_______________________________________________________________________________Docker
dc-up:
	docker compose -f docker-compose.yml -f compose.override.yml up -d

dc-down:
	docker compose -f docker-compose.yml -f compose.override.yml down

dc-logs:
	docker compose -f docker-compose.yml -f compose.override.yml logs -f

dc-ps:
	docker compose -f docker-compose.yml -f compose.override.yml ps

dc-shell:
	docker compose -f docker-compose.yml -f compose.override.yml exec app /bin/sh

dc-db:
	docker compose -f docker-compose.yml -f compose.override.yml exec db psql -U $$POSTGRES_USER $$POSTGRES_DB

#_______________________________________________________________________________VPS
vps-update:
	git fetch origin
	git reset --hard origin/main
	uv sync
	uv run python manage.py migrate
	make collectstatic
	sudo systemctl restart w_parser.service
