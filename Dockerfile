FROM python:3.9-slim

# Instalar dependencias del sistema operativo (Poppler, FFmpeg, execstack y librerías C)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    ffmpeg \
    libsm6 \
    libxext6 \
    git \
    execstack \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Actualizar pip
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# LIMPIAR EL FLAG EXECSTACK EN LAS LIBRERÍAS DE ONNXRUNTIME QUE GENERA EL ERROR 500
RUN find /usr/local/lib/python3.9/site-packages/onnxruntime -name "*.so" -exec execstack -c {} + || true

COPY . .

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]