# Tienda de Electrónica - Django

Sistema de tienda en línea construido con Django 5.2.8 con las siguientes características:

## Características

- **Control de Acceso**: Autenticación de usuarios con roles (admin, vendedor, gerente, cliente).
- **Catálogo de Productos**: Browseable product listing con filtros por categoría y búsqueda.
- **Carrito de Compras**: Agregar/eliminar productos, actualizar cantidades, procesar compras.
- **Ventas/Transacciones**: Registro de ventas con reducción automática de stock.
- **Reportes**: Reportes de ventas por fecha, categoría y producto.
- **Generación de PDF**: Descargar reportes en PDF usando ReportLab.
- **Interfaz Web**: Bootstrap 5 con diseño responsivo.

## Tecnologías

- Python 3.13
- Django 5.2.8
- SQLite (desarrollo) / PostgreSQL (producción)
- ReportLab (generación de PDF)
- Bootstrap 5

## Instalación Local

1. Clonar el repositorio:
```bash
git clone <tu-repo>
cd proyecto2.1
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Aplicar migraciones:
```bash
python manage.py migrate
```

5. Crear superusuario:
```bash
python manage.py createsuperuser
```

6. Ejecutar servidor de desarrollo:
```bash
python manage.py runserver
```

7. Acceder a:
- Inicio: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

## Despliegue en Render

1. Configura las variables de entorno en Render:
   - `SECRET_KEY` — clave segura
   - `DATABASE_URL` — URL de PostgreSQL
   - `ALLOWED_HOSTS` — dominio de tu app
   - `CSRF_TRUSTED_ORIGINS` — dominio con protocolo (ej: `https://mi-app.onrender.com`)

2. Build command:
```bash
bash build.sh
```

3. Start command:
```bash
gunicorn proyecto_dos.wsgi:application --bind 0.0.0.0:$PORT --log-file -
```

## Usuarios de Prueba

Si ejecutas el script de inicialización:
```bash
python manage.py init_tienda
# o
python scripts\populate_db.py
```

Usuarios creados:
- `admin` / `admin123` — Administrador
- `vendedor` / `vendedor123` — Vendedor
- `gerente` / `gerente123` — Gerente de Reportes

## Estructura del Proyecto

```
proyecto2.1/
├── proyecto_dos/       # Configuración de Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── tienda/             # Aplicación principal
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── templates/      # Templates HTML
│   ├── static/         # Archivos estáticos (CSS, JS, SVG)
│   └── management/commands/  # Comandos personalizados
├── manage.py
├── requirements.txt
├── build.sh            # Script de build para Render
└── README.md
```

## Contribuciones

Para contribuir, crea un fork del proyecto, realiza los cambios en una rama nueva y envía un pull request.

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.
