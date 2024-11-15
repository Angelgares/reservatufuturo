#!/bin/bash
set -e
# Rutas
GLOBAL_PATH="$(pwd)"  # Usa el directorio actual como referencia
echo "✅ Ruta global definida: $GLOBAL_PATH"
DB_PATH="$GLOBAL_PATH/reservatufuturo/db.sqlite3"
echo "✅ Ruta de la base de datos: $DB_PATH"
VENV_DIR="$GLOBAL_PATH/venv"
echo "✅ Ruta del entorno virtual: $VENV_DIR"

# Comprobamos si existe el entorno virtual
if [[ -d "$VENV_DIR" ]]; then
    echo "🐍 Activando entorno virtual..."
    source "$VENV_DIR/bin/activate"

    # Verificamos si se activó correctamente
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo "❌ No se pudo activar el entorno virtual, saliendo..."
        exit 1
    else
        echo "✅ Entorno virtual activado: $VIRTUAL_ENV"
    fi
else
    echo "ℹ️ No se encontró un entorno virtual, puedes crear uno con 'python3.12 -m venv $VENV_DIR'"
    exit 1
fi

# Usar pip del entorno virtual
echo "📦 Instalando dependencias..."
"$VENV_DIR/bin/pip3" install -r requirements.txt

# Eliminar el archivo de base de datos SQLite si existe
if [[ -f "$DB_PATH" ]]; then
    echo "🗑️  Eliminando $DB_PATH..."
    rm "$DB_PATH"
else
    echo "ℹ️  No se encontró $DB_PATH, continuando..."
fi

# Eliminar archivos de migraciones en todas las apps, EXCEPTO __init__.py
echo "🗑️  Eliminando archivos de migraciones..."
find $GLOBAL_PATH/reservatufuturo -path "*/migrations/*.py" -not -name "__init__.py" -delete
find $GLOBAL_PATH/reservatufuturo -path "*/migrations/*.pyc"  -delete

# Crear migraciones desde cero usando python del entorno virtual
echo "⚙️  Creando nuevas migraciones..."
cd $GLOBAL_PATH/reservatufuturo
python manage.py makemigrations

# Aplicar las migraciones
echo "⚙️  Aplicando migraciones..."
python manage.py migrate

# Opcional: Cargar datos iniciales si existe un archivo seed.json
if [[ -f "seed.json" ]]; then
    echo "📂 Cargando datos iniciales desde seed.json..."
    python manage.py loaddata seed.json
else
    echo "ℹ️  No se encontró seed.json, saltando este paso..."
fi

echo "🚀 ¡Base de datos restablecida y lista para usar!"
