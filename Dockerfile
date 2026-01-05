# Dockerfile para desplegar tu app Streamlit
FROM python:3.11-slim

WORKDIR /app

# Instala dependencias del sistema si las necesitas (ejemplo: build-essential, libpq-dev para psycopg2)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copia los archivos de dependencias
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia el resto del código
COPY . .

# Expone el puerto de Streamlit
EXPOSE 8503

# Variables de entorno para Streamlit (opcional)
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar la app
CMD ["streamlit", "run", "src/app.py", "--server.port=8503", "--server.address=0.0.0.0"]
