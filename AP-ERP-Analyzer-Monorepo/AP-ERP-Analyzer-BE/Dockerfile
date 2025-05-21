# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto en el que se ejecuta la aplicación
EXPOSE 5002

# Comando para ejecutar la aplicación
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "5002"]
