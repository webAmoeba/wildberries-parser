import os
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv(Path(__file__).resolve().parent / ".env")

url = urlparse(os.getenv("DATABASE_URL"))

db_name = url.path.lstrip("/")
db_user = url.username
db_password = url.password
db_host = url.hostname or "localhost"
db_port = url.port or 5432

pg_superuser = os.getenv("POSTGRES_SUPERUSER", "postgres")
pg_password = os.getenv("POSTGRES_PASSWORD", "")


def create_db():
    conn = psycopg2.connect(
        dbname="postgres",
        user=pg_superuser,
        password=pg_password,
        host=db_host,
        port=db_port,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    try:
        cur.execute(f"CREATE USER {db_user} WITH PASSWORD %s;", (db_password,))
        print(f"✅ User '{db_user}' created.")
    except psycopg2.errors.DuplicateObject:
        print(f"ℹ️  User '{db_user}' already exists.")
        conn.rollback()

    try:
        cur.execute(f"CREATE DATABASE {db_name} OWNER {db_user};")
        print(f"✅ Database '{db_name}' created.")
    except psycopg2.errors.DuplicateDatabase:
        print(f"ℹ️  Database '{db_name}' already exists.")
        conn.rollback()

    cur.close()
    conn.close()


if __name__ == "__main__":
    create_db()
