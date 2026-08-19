FROM python:3.12-slim
LABEL org.opencontainers.image.source="https://github.com/vaibhavkhuranaaa/healthcare-sepsis-prediction" \
      org.opencontainers.image.description="Synthetic sepsis-risk research demo. Not for clinical use." \
      org.opencontainers.image.licenses="MIT"
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv==0.11.29 \
    && uv sync --frozen --no-dev --no-install-project
COPY src ./src
EXPOSE 8000
CMD ["/app/.venv/bin/gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "src.app:app"]
