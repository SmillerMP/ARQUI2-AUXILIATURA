# Etapa 1: Builder con dependencias
FROM python:3.13.2-slim AS builder

WORKDIR /install

COPY requirements.txt .

# Instalar dependencias directamente en /usr/local 
RUN pip install --no-cache-dir --prefix=/usr/local -r requirements.txt

# Etapa 2: Imagen final
FROM python:3.13.2-slim

WORKDIR /app

# Copiar dependencias ya listas desde el builder
COPY --from=builder /usr/local /usr/local

# Copiar aplicación
COPY . /app

# Ejecutar la aplicación
CMD ["python", "main.py"]
