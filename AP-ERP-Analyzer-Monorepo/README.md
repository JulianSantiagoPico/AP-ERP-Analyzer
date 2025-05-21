# AP-ERP-Analyzer Monorepo

Este monorepo está configurado para facilitar el despliegue del proyecto AP-ERP-Analyzer (backend y frontend) en Render.

## Estructura del Monorepo

```
AP-ERP-Analyzer-Monorepo/
├── AP-ERP-Analyzer-BE/
│   └── Dockerfile
├── AP-ERP-Analyzer-FE/
│   └── Dockerfile
├── docker-compose.yml
├── render.yaml
└── README.md
```

## Cómo funciona

Esta estructura de monorepo está diseñada para trabajar con los repositorios originales sin modificarlos:

- Los Dockerfiles están configurados para acceder a los archivos de los repositorios originales
- El contexto de construcción de Docker se establece en el directorio raíz del proyecto
- El archivo render.yaml está configurado para desplegar ambos servicios en Render

## Despliegue Local

Para probar el despliegue localmente:

1. Navega al directorio del monorepo:
   ```bash
   cd AP-ERP-Analyzer-Monorepo
   ```

2. Ejecuta Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Accede a la aplicación:
   - Frontend: http://localhost:80
   - Backend API: http://localhost:5002

## Despliegue en Render

### Preparación

1. Crea un nuevo repositorio Git en GitHub/GitLab
2. Inicializa Git en el directorio raíz del proyecto (si aún no está inicializado)
   ```bash
   git init
   ```

3. Añade todos los archivos al repositorio:
   ```bash
   git add .
   git commit -m "Initial commit with monorepo structure"
   ```

4. Conecta con el repositorio remoto:
   ```bash
   git remote add origin <URL-DEL-REPOSITORIO>
   git push -u origin main
   ```

### Despliegue

1. Inicia sesión en [Render](https://dashboard.render.com/)
2. Haz clic en "New" y selecciona "Blueprint"
3. Conecta tu repositorio de GitHub/GitLab
4. Render detectará automáticamente el archivo `render.yaml` y configurará los servicios
5. Revisa la configuración y haz clic en "Apply"

## Actualización del Código

Cuando necesites actualizar el código:

1. Actualiza los repositorios originales (backend y frontend)
2. Haz commit y push de los cambios al repositorio del monorepo

## Consideraciones Importantes

- Los Dockerfiles están configurados para acceder a los archivos de los repositorios originales desde el contexto raíz
- El archivo `render.yaml` está configurado para que el frontend pueda comunicarse con el backend automáticamente
- Si cambias la estructura de directorios, asegúrate de actualizar las rutas en los Dockerfiles y en el archivo `render.yaml`
