# Despliegue de una app Streamlit con Docker en DigitalOcean

Esta guía te explica cómo desplegar tu aplicación Streamlit en una Droplet de DigitalOcean usando Docker, desde cero.

---

## 1. Pre-requisitos
- Tener una Droplet de DigitalOcean con Ubuntu.
- Acceso SSH a la Droplet.
- Tener tu código en un repositorio de GitHub.

---

## 2. Instalar Docker

```bash
sudo apt update
sudo apt install docker.io -y
sudo systemctl enable --now docker
```

---

## 3. Clonar tu proyecto desde GitHub

```bash
cd ~
git clone https://github.com/Cagudelot/autoservicio_autipista.git
cd autoservicio_autipista
```

---

## 4. Crear el archivo `.env` con tus variables secretas

Crea un archivo `.env` en la raíz del proyecto con este contenido (ajusta los valores):

```
ALEGRA_API_KEY="tu_api_key"
ALEGRA_EMAIL="tu_email"
DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres.sbuhgxgwhkcfrumuvmyf
DB_PASSWORD=7Pz8Xp0ulx8K2yi9
```

---

## 5. Crear el archivo `Dockerfile`

Crea un archivo llamado `Dockerfile` en la raíz del proyecto con este contenido:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8501

ENV PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 6. Construir la imagen Docker

```bash
docker build -t miapp-streamlit .
```

---

## 7. Ejecutar el contenedor

```bash
docker run -d -p 8501:8501 --env-file .env miapp-streamlit
```

---

## 8. Acceder a la app

Abre tu navegador y entra a:
```
http://IP_DE_TU_DROPLET:8501
```

---

## 9. (Opcional) Abrir el puerto en el firewall

Si usas UFW:
```bash
sudo ufw allow 8501
```

---

## 10. (Opcional) Servir la app por HTTPS con Nginx y dominio propio

1. Instala Nginx y Certbot:
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx -y
   ```
2. Configura Nginx como proxy reverso (ver instrucciones detalladas en la conversación si lo necesitas).
3. Solicita el certificado SSL con Certbot.

---

## Notas
- Si el puerto 80 está ocupado, usa el 8501 como en los ejemplos.
- Si cambias el archivo `.env`, reinicia el contenedor para que tome los nuevos valores.
- Para ver logs del contenedor:
  ```bash
  docker logs <id_del_contenedor>
  ```

---

**¡Listo! Tu app Streamlit está desplegada en DigitalOcean usando Docker.**
