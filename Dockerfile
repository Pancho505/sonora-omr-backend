FROM python:3.9-slim

# Instalar dependencias del sistema operativo (Poppler, FFmpeg, patchelf y librerías C)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    ffmpeg \
    libsm6 \
    libxext6 \
    git \
    patchelf \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Actualizar pip
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Limpiar el flag de la librería ONNX para evitar el ImportError de executable stack
RUN find /usr/local/lib/python3.9/site-packages/onnxruntime -name "*.so" -exec patchelf --clear-execstack {} + || true

COPY . .

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]