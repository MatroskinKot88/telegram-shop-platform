#!/bin/bash
# Запускаем FastAPI в фоновом режиме
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Запускаем Telegram бота в основном потоке
python -m app.bot