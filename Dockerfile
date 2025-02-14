# ������� ����� Python
FROM python:3.9-slim

# ��������� ��������� ������������
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    sqlite3 \
    libsqlite3-dev \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# �������� ������� ����������
WORKDIR /app

# ����������� requirements.txt ��� ��������� ������������
COPY requirements.txt /app/
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# ����������� ���������� ����
COPY . /app/

# ��������� ������������ ���������
ENV PATH="/opt/venv/bin:$PATH"

# ������ ����������
CMD ["python", "main.py"]