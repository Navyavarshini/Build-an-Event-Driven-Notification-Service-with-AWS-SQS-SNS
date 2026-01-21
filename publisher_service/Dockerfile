# ---------- Stage 1: Build dependencies ----------
FROM python:3.9-slim-buster AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# ---------- Stage 2: Runtime image ----------
FROM python:3.9-slim-buster

WORKDIR /app

# ✅ COPY BOTH site-packages AND binaries
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
