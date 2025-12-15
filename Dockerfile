# Usamos una imagen ligera de Python
FROM python:3.10-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema necesarias (opcional para SQLite a veces)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiamos requirements e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto 5000
EXPOSE 5000

# Comando para iniciar la app con Gunicorn
# "app:app" significa: busca el archivo app.py y dentro el objeto app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]