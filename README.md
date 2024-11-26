# ReservaTuFuturo 🚀

ReservaTuFuturo es una plataforma moderna y robusta para gestionar cursos académicos, facilitar reservas y permitir pagos rápidos. Este proyecto está diseñado para ser fácil de usar y personalizar, con soporte para ejecución local y en contenedores Docker. 💡

---

## ✨ **Novedades**: Boring Tasks Script 🎉

¿Te cansan los comandos repetitivos? Hemos añadido el **Boring Tasks Script**, un script bash para automatizar tareas monótonas como reconstruir la base de datos o ejecutar el servidor.

### Cómo usarlo:
```bash
./boring_tasks.sh
```

El script se encarga de todo por ti. Siéntate, relájate y deja que haga el trabajo aburrido. 😌

---

## 🔧 **Dependencias**

Asegúrate de tener Python 3.12 instalado. Luego, sigue estos pasos para instalar las dependencias:

```bash
cd reservatufuturo
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 **Cómo ejecutar la aplicación**

### Ejecución local

Si prefieres ejecutar la aplicación en tu máquina sin Docker:

1. Navega al directorio del proyecto:
   ```bash
   cd reservatufuturo
   ```

2. Prepara la base de datos:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py loaddata seed.json
   ```

3. Levanta el servidor:
   ```bash
   python manage.py runserver
   ```

Accede a la aplicación en: [http://localhost:8000](http://localhost:8000)

---

### Ejecución con Docker 🐳

Si prefieres contenedores (¡porque vivimos en 2024!):

1. Navega al directorio raíz del proyecto:
   ```bash
   cd reservatufuturo
   ```

2. Construye y levanta los contenedores:
   ```bash
   docker-compose up --build
   ```

Accede a la aplicación en: [http://localhost:8000](http://localhost:8000)

---

## 👤 **Usuarios de prueba**

Puedes utilizar los siguientes usuarios para probar la aplicación.

### **User1**
- **Usuario:** user1
- **Email:** user1@example.com
- **Contraseña:** pass_user_1

### **User2**
- **Usuario:** user2
- **Email:** user2@example.com
- **Contraseña:** pass_user_1

### **Academy1 (Grupo Academy)**
- **Usuario:** academy1
- **Email:** academy1@example.com
- **Contraseña:** pass_user_1

---

## 💳 **Tarjeta de prueba para pagos**

Para probar el sistema de pagos (Stripe):

- **Número de tarjeta:** `4242424242424242`
- **Fecha de expiración:** cualquier fecha futura
- **CVC:** cualquier combinación de 3 dígitos

---

## 🛠️ **Estructura del proyecto**

```plaintext
PGPI_PROJECT/
│
├── reservatufuturo/     # Carpeta principal de la aplicación Django
│   ├── cart/            # Módulo de carrito de compras
│   ├── courses/         # Módulo de gestión de cursos
│   ├── home/            # Módulo para la página principal
│   ├── reservatufuturo/ # Configuración principal de Django
│   ├── db.sqlite3       # Base de datos local SQLite
│   ├── manage.py        # Herramienta de administración de Django
│   ├── staticfiles/     # Archivos estáticos
│   └── media/           # Archivos cargados por los usuarios
│
├── requirements.txt     # Dependencias de Python
├── Dockerfile           # Configuración para Docker
├── docker-compose.yml   # Configuración de Docker Compose
├── boring_tasks.sh      # Script para automatizar tareas repetitivas
└── README.md            # Este archivo 💪
```

---

## ⚡ **Automatización con `boring_tasks.sh`**

El script `boring_tasks.sh` incluye atajos para:

- **Reconstruir la base de datos:**
  ```bash
  ./boring_tasks.sh rebuild-db
  ```

- **Levantar el servidor localmente:**
  ```bash
  ./boring_tasks.sh runserver
  ```

- **Construir y ejecutar contenedores Docker:**
  ```bash
  ./boring_tasks.sh docker-up
  ```

---