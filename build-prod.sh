#!/usr/bin/env bash
set -e  # останавливаем скрипт при ошибке

# Установка uv, если ещё не установлен
if ! command -v uv &> /dev/null; then
  echo "🛠 Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Установка зависимостей
echo "📦 Installing dependencies..."
uv sync

# Создание базы данных (если нужно)
echo "🧱 Creating database (if not exists)..."
uv run python create_db.py

# Сборка статики
echo "🎨 Collecting static files..."
uv run python manage.py collectstatic --noinput

# Применение миграций и создание суперпользователя
echo "🔧 Applying migrations and creating superuser..."
uv run python manage.py migrate
uv run python manage.py shell < create_superuser.py

echo "✅ Build complete."
