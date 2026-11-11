# 💩 Proyecto KK

Aplicación web para **registrar, analizar y comparar tus visitas al baño**. Cronometras
cada "cagada", la calificas, la ubicas en el mapa y, si quieres, la compartes con la
comunidad. Con el tiempo, la app te muestra tus hábitos: a qué hora vas más, dónde,
cuánto tardas y cómo te comparas con otros usuarios.

Hecha con **Django** y **PostgreSQL**, con plantillas, CSS y JavaScript propios (sin
frameworks de frontend) y pensada **primero para el móvil**.

---

## Índice

- [Funcionalidades](#funcionalidades)
- [Cómo funciona](#cómo-funciona)
- [Tecnologías](#tecnologías)
- [Instalación y ejecución en local](#instalación-y-ejecución-en-local)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Privacidad](#privacidad)
- [Estado del proyecto](#estado-del-proyecto)
- [Créditos](#créditos)

---

## Funcionalidades

### ⏱️ Registro de cagadas
- **Cronómetro** para medir la duración: iniciar, terminar y reiniciar (con confirmación).
  El tiempo no se pierde al recargar la página, si el formulario vuelve con un error o al
  salir a crear una ubicación nueva.
- Datos de cada registro: **ubicación**, **calificación** (0–5, con decimales),
  **categoría** (10 tipos), **color**, **observaciones** y si es **pública o privada**.
- **Historial**, detalle, edición y eliminación de tus registros.
- Validaciones en el servidor: sin horas futuras, duración máxima de 2 horas y registro
  como mucho 1 hora después de terminar.

### 📍 Ubicaciones
- Tus "lugares de confianza" con nombre, tipo (casa, trabajo…) y coordenadas.
- Las coordenadas se pueden **capturar automáticamente** con la geolocalización del
  navegador (pidiendo permiso) o escribir a mano.
- Se pueden crear sin salir del registro de una cagada.

### 🗺️ Mapa
- Un **pin por ubicación**, con un **color según cuántas cagadas** llevas en ella
  (0 · 1–2 · 3–5 · 6–10 · 11 o más) y 👑 en tu lugar favorito.
- Al tocar un pin: número de cagadas, % del total, duración media, calificación media y
  última visita.
- Los lugares muy cercanos (por ejemplo, dos baños de la misma casa) se **agrupan** y se
  abren en abanico al tocarlos.
- Panel **"Tu geografía"**: lugar favorito, **centro de gravedad** 🎯 (el punto medio de
  tus cagadas), **radio de acción**, mayor distancia entre tus lugares y reparto por tipo
  de lugar.

### 🌍 Feed social
- Las cagadas marcadas como públicas aparecen en un **feed** con filtros y paginación.
- **Reacciones** (5 tipos) sin recargar la página.

### 📊 Analítica
- **Indicadores** generales: total, tiempo total, duración y calificación promedio.
- **Temporal**: por día de la semana y por hora del día.
- **Por categoría** y **por ubicación**.
- Gráficos hechos solo con CSS, adaptados a pantallas táctiles.

### 🥊 Comparación entre usuarios
- Duelo cara a cara con otro usuario, **solo con cagadas públicas** de ambos.
- **Marcador**: un punto por cada métrica ganada (más constante, más paciente, récord más
  largo, mejor calidad, más explorador y **más trotamundos**).
- Puntos fuertes y hábitos de cada uno (día favorito, hora pico, categoría y
  **"fiel a su trono"**), y tablas por categorías, días y horas.

### 👤 Cuentas
- Registro, inicio de sesión **con el correo**, perfil con foto, cambio y recuperación de
  contraseña y eliminación de la cuenta.
- **Avisos** en ventanas modales tras cada acción (registrar, editar, eliminar…).

---

## Cómo funciona

1. **Te registras** e inicias sesión con tu correo.
2. Desde el inicio pulsas **"Registrar cagada"**: inicias el cronómetro y lo terminas al
   acabar. Completas los detalles (ubicación, calificación, categoría…) y decides si es
   visible para otros.
3. Tus registros alimentan el **historial**, la **analítica** y el **mapa**, que son
   privados y cuentan todas tus cagadas.
4. Las cagadas **públicas** aparecen en el **feed** y son las únicas que se usan en la
   **comparación** con otros usuarios, también las tuyas.

Cada usuario solo puede ver y modificar **sus propios** registros y ubicaciones.

---

## Tecnologías

| Parte | Tecnología |
|---|---|
| Backend | Python 3.12+ · Django 6.1 |
| Base de datos | PostgreSQL (con `psycopg` 3) |
| Imágenes (fotos de perfil) | Pillow |
| Configuración | `python-dotenv` (variables en un archivo `.env`) |
| Frontend | Plantillas de Django, CSS propio y JavaScript sin frameworks |
| Mapa | [Leaflet](https://leafletjs.com/) 1.9 + [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster) 1.5 (desde CDN) con mosaicos de [OpenStreetMap](https://www.openstreetmap.org/) |

---

## Instalación y ejecución en local

### Requisitos previos

- **Python 3.12 o superior** (Django 6.1 no funciona con versiones anteriores).
  Comprobado con Python 3.14.
- **PostgreSQL** instalado y en marcha.
- **Git**.
- Conexión a internet para el mapa (Leaflet y los mosaicos se cargan desde fuera).

### 1. Clonar el repositorio

```bash
git clone https://github.com/SantiX1227/ProyectoKK.git
cd ProyectoKK
```

### 2. Crear y activar un entorno virtual

**Windows (PowerShell):**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

> Si PowerShell no deja ejecutar el script de activación, puedes permitirlo solo para la
> ventana actual con `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, o usar
> directamente `venv\Scripts\python.exe` en lugar de `python`.

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear la base de datos en PostgreSQL

Con `psql` (o con pgAdmin), crea una base de datos y un usuario para el proyecto. Por
ejemplo:

```sql
CREATE USER proyectokk WITH PASSWORD 'una-contraseña-segura';
CREATE DATABASE proyectokk OWNER proyectokk;
```

### 5. Crear el archivo `.env`

En la raíz del proyecto (junto a `manage.py`), crea un archivo llamado `.env` con este
contenido, cambiando los valores por los tuyos:

```env
SECRET_KEY=pon-aqui-una-clave-larga-y-aleatoria
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=proyectokk
DB_USER=proyectokk
DB_PASSWORD=una-contraseña-segura
DB_HOST=localhost
DB_PORT=5432
```

| Variable | Para qué sirve |
|---|---|
| `SECRET_KEY` | Clave secreta de Django. **Obligatoria**: sin ella la app no arranca. |
| `DEBUG` | `True` solo en desarrollo. Si falta o tiene otro valor, vale `False`. |
| `ALLOWED_HOSTS` | Dominios desde los que se puede abrir la app, separados por comas. |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Conexión a PostgreSQL. |

Para generar una `SECRET_KEY` nueva:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

> ⚠️ El archivo `.env` contiene contraseñas: **nunca lo subas a GitHub** (ya está en el
> `.gitignore`).

### 6. Crear las tablas

```bash
python manage.py migrate
```

### 7. Crear un administrador (opcional)

```bash
python manage.py createsuperuser
```

El panel de administración está en `/admin/`. Como la app inicia sesión con el
**correo**, en el campo de usuario del admin se escribe el **email** del superusuario.

### 8. Arrancar el servidor

```bash
python manage.py runserver
```

Abre **http://localhost:8000** en el navegador, crea una cuenta y empieza a registrar.

### Notas útiles

- **Recuperar contraseña:** en desarrollo, los correos no se envían de verdad, sino que
  se **muestran en la terminal** donde corre `runserver`. Ahí encontrarás el enlace para
  restablecer la contraseña.
- **Geolocalización:** el navegador solo la permite en `localhost` o con **HTTPS**. Si
  abres la app desde el móvil usando la IP de tu ordenador (`http://192.168.x.x:8000`),
  tendrás que escribir las coordenadas a mano.
- **Fotos de perfil:** se guardan en la carpeta `media/`. Con `DEBUG=True`, Django las
  sirve automáticamente.
- **Probarlo desde el móvil en la misma red:** añade la IP de tu ordenador a
  `ALLOWED_HOSTS` y arranca con `python manage.py runserver 0.0.0.0:8000`.

---

## Estructura del proyecto

```
config/                 Configuración de Django (settings.py, urls.py)
apps/
  usuarios/             Modelo de usuario, registro, inicio de sesión por correo y perfil
  cagadas/              Registro con cronómetro, historial, detalle, edición y eliminación
  ubicaciones/          Lugares (CRUD), mapa y cálculos geográficos (geografia.py)
  feed/                 Feed público y reacciones
  analytics/            Analítica personal y comparación entre usuarios
  core/                 Página de inicio y filtros de plantilla (|duracion, |distancia)
templates/              Plantillas HTML (una carpeta por app; base.html e includes/)
static/
  css/                  Sistema de diseño (base.css) y estilos por sección
  js/                   Cronómetro, reacciones, geolocalización, mapa y avisos
manage.py
requirements.txt
```

---

## Privacidad

- Cada usuario solo ve y edita **sus propios** registros y ubicaciones.
- El **feed** y la **comparación** usan solo las cagadas marcadas como **públicas**.
- Las **coordenadas** solo aparecen en tu analítica y en tu mapa, que son privados. En el
  feed solo se ve el nombre del lugar, y en la comparación solo conteos, porcentajes y
  distancias, nunca dónde están los lugares del otro usuario.
- Todos los cálculos geográficos se hacen en el servidor, sin enviar coordenadas a
  servicios externos. El mapa sí descarga los mosaicos de OpenStreetMap, que ve la zona
  del mapa que se está mirando.

---

## Estado del proyecto

En desarrollo. Ya funcionan el registro, las ubicaciones, el historial, el feed, la
analítica, el mapa y la comparación, con el diseño final adaptado al móvil.

Próximos pasos:

- [ ] Tests automáticos.
- [ ] Revisión funcional y de seguridad antes de publicar (servir las librerías del mapa
      desde el propio proyecto, HTTPS, configuración de producción).
- [ ] Racha diaria (en la analítica, la comparación y la página de inicio).
- [ ] Orden y filtros en el historial.
- [ ] Comparación con valores de referencia de una persona promedio.
- [ ] Mensajes automáticos con conclusiones en la analítica.

---

## Créditos

- Mapas © colaboradores de [OpenStreetMap](https://www.openstreetmap.org/copyright).
- Mapa interactivo con [Leaflet](https://leafletjs.com/) y
  [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster).
- Tipografía [Plus Jakarta Sans](https://fonts.google.com/specimen/Plus+Jakarta+Sans)
  (Google Fonts).

Desarrollado por [@SantiX1227](https://github.com/SantiX1227).
