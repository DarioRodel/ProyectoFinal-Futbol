# Usa una imagen oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto al contenedor
COPY .. .

# Expone el puerto 8000 para Django
EXPOSE 8000

# Comando para iniciar el servidor de desarrollo
CMD ["gunicorn","python", "manage.py", "runserver", "localhost:8000"]
