# Etapa de construcción
FROM node:18-alpine as build

# Establecer directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar el resto del código fuente
COPY . .

# Construir la aplicación para producción
RUN npm run build

# Etapa de producción
FROM nginx:alpine

# Copiar la configuración personalizada de nginx
COPY --from=build /app/build /usr/share/nginx/html

# Crear archivo de configuración de nginx para manejar rutas de React
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Exponer puerto 80
EXPOSE 80

# Iniciar nginx
CMD ["nginx", "-g", "daemon off;"]
