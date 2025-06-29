FROM python
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/main.py .
COPY app/database.py .
COPY app/models.py .
COPY app/config.py .
COPY app/middlewares.py .
COPY app/commands.py .

ENV PYTHONPATH=/app

CMD ["python", "main.py"]
