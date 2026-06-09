import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 1. Добавляем путь к папке backend, чтобы Python видел модуль 'app'
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 2. Импортируем наши настройки и Base (в котором зарегистрированы все модели)
from app.core.config import settings
from app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 3. Переопределяем URL базы данных на тот, что в нашем .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. Указываем метаданные для автогенерации миграций
target_metadata = Base.metadata


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
