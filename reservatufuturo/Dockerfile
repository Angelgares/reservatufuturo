# Usa una imagen base de Python
FROM python:3.12-slim

# Configura el directorio de trabajo
WORKDIR /app

# Copia el archivo de requerimientos
COPY requirements.txt /app/

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos del proyecto al contenedor
COPY . /app/

# Expón el puerto 8000
EXPOSE 8000

# Comando de inicio del contenedor
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "reservatufuturo.wsgi:application"]
