# Базовый образ Python
FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    sqlite3 \
    libsqlite3-dev \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование requirements.txt для установки зависимостей
COPY requirements.txt /app/
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Копирование остального кода
COPY . /app/

# Активация виртуального окружения
ENV PATH="/opt/venv/bin:$PATH"

# Запуск приложения
CMD ["python", "main.py"]