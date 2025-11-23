# -------------------------------------------------------
# LifePilot — Dockerfile
# Python + Streamlit + Google GenAI + ReportLab support
# -------------------------------------------------------

FROM python:3.10-slim

# Install system dependencies for reportlab (PDF fonts)
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Environment variable for Google AI Key
ENV GOOGLE_API_KEY=""

# Streamlit runs without Stdin prompts
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run the Streamlit app
CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
