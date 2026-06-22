# Используем легкий и стабильный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код приложения
COPY . .

# Делаем скрипт запуска исполняемым
RUN chmod +x start.sh

# Команда по умолчанию при запуске контейнера
CMD ["bash", "start.sh"]