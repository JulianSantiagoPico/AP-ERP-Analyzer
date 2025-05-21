# AP-ERP-Analyzer

Aplicación para análisis de datos ERP y visualización de KPIs, con un backend en FastAPI y un frontend en React.

## Estructura del Proyecto

```
AP-ERP-Analyzer/
├── AP-ERP-Analyzer-BE/       # Backend (FastAPI)
│   ├── app/                  # Código principal del backend
│   ├── Dockerfile            # Dockerfile para el backend
│   ├── requirements.txt      # Dependencias del backend
│   └── run.py                # Punto de entrada del backend
├── AP-ERP-Analyzer-FE/       # Frontend (React)
│   ├── public/               # Archivos estáticos
│   ├── src/                  # Código fuente del frontend
│   ├── Dockerfile            # Dockerfile para el frontend
│   └── package.json          # Dependencias del frontend
├── docker-compose.yml        # Configuración para Docker Compose
└── render.yaml               # Configuración para despliegue en Render
```

## Despliegue Local

Para ejecutar la aplicación localmente:

1. Clona este repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd AP-ERP-Analyzer
   ```

2. Ejecuta con Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Accede a la aplicación:
   - Frontend: http://localhost:80
   - Backend API: http://localhost:5002

## Despliegue en Render

Este proyecto está configurado para ser desplegado automáticamente en Render:

1. Conecta tu repositorio de GitHub a Render
2. Selecciona la opción "Blueprint"
3. Render detectará automáticamente el archivo `render.yaml` y configurará los servicios

## Características

- **Backend**: API RESTful con FastAPI para análisis de datos ERP
- **Frontend**: Interfaz de usuario moderna con React y Tailwind CSS
- **Análisis de Datos**: KPIs financieros, análisis de ventas, cuentas por cobrar/pagar
- **Predicciones ML**: Modelos de machine learning para predicciones de ventas
