# ---------- Base image ----------
FROM python:3.11-slim

# ---------- Set working directory ----------
WORKDIR /app

# ---------- Copy project files ----------
COPY . /app

# ---------- Upgrade pip ----------
RUN pip install --upgrade pip

# ---------- Install system dependencies ----------
RUN apt-get update && \
    apt-get install -y git build-essential libsqlite3-0 && \
    rm -rf /var/lib/apt/lists/*

# ---------- Install Python dependencies ----------
RUN pip install --no-cache-dir -r medrag/requirements.txt

# ---------- Set environment variables ----------
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ENABLECORS=false

# ---------- Expose Streamlit port ----------
EXPOSE 8501

# ---------- Run Streamlit ----------
CMD ["streamlit", "run", "medrag/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
