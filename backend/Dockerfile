FROM python:3.11-slim
WORKDIR /app
COPY app/ ./app/
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings sqlalchemy alembic psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv httpx
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
