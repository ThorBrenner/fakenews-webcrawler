# Imagem oficial do Playwright para Python: já inclui o Chromium e todas as
# dependências de sistema necessárias (usadas pelo spider "lupa").
FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Garante que o navegador do Playwright esteja instalado para a versão do pip.
RUN playwright install chromium

COPY . .

CMD ["python", "scheduler.py"]
