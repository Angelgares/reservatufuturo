#!/bin/bash
set -e
clear

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin color

# Capturar señal de interrupción (Ctrl+C)
trap ctrl_c INT

ctrl_c() {
    echo -e "\n${RED}👋 Saliendo...${NC}"
    exit 0
}

# Mostrar banner con colores y ASCII Art

echo -e "${GREEN}==============================================================

    ____   ______    ______           ____     ______ _    __
   / __ \ /_  __/   / ____/          / __ \   / ____/| |  / /
  / /_/ /  / /     / /_             / / / /  / __/   | | / / 
 / _, _/  / /     / __/            / /_/ /  / /___   | |/ /  
/_/ |_|  /_/     /_/              /_____/  /_____/   |___/   
                                                             
${YELLOW}ReservaTuFuturo Developer Settings${NC}
${GREEN}==============================================================${NC}"


# Rutas
GLOBAL_PATH="$(pwd)"  # Usa el directorio actual como referencia
DB_PATH="$GLOBAL_PATH/reservatufuturo/db.sqlite3"
VENV_DIR="$GLOBAL_PATH/venv"

menu() {
    echo "🔧 Menú de Opciones"
    echo "-----------------"
    echo "0) All in One (Puede tardar un poco)"
    echo "1) Restablecer BD y Migraciones"
    echo "2) Arrancar el servidor"
    echo "3) Crear superusuario de Django (admin/admin)"
    echo "4) Crear entorno virtual"
    echo "5) Salir"
    echo -n -e "${YELLOW}Elige una opción: ${NC}"
    read opcion
}

activar_entorno_virtual() {
    if [[ -d "$VENV_DIR" ]]; then
        echo -e "${GREEN}🐍 Activando entorno virtual...${NC}"
        source "$VENV_DIR/bin/activate"
        if [[ -z "$VIRTUAL_ENV" ]]; then
            echo -e "${RED}❌ No se pudo activar el entorno virtual, saliendo...${NC}"
            exit 1
        else
            echo -e "${GREEN}✅ Entorno virtual activado: $VIRTUAL_ENV${NC}"
        fi
    else
        echo -e "${RED}ℹ️ No se encontró un entorno virtual. Crea uno con 'python3.12 -m venv $VENV_DIR'.${NC}"
        exit 1
    fi
}

instalar_dependencias() {
    echo -e "${GREEN}📦 Instalando dependencias...${NC}"
    "$VENV_DIR/bin/pip3" install -r requirements.txt
}

eliminar_base_datos() {
    if [[ -f "$DB_PATH" ]]; then
        echo -e "${GREEN}🗑️  Eliminando base de datos en $DB_PATH...${NC}"
        rm "$DB_PATH"
    else
        echo -e "${RED}ℹ️  No se encontró $DB_PATH, continuando...${NC}"
    fi
}

eliminar_migraciones() {
    echo -e "${GREEN}🗑️  Eliminando archivos de migraciones...${NC}"
    find $GLOBAL_PATH/reservatufuturo -path "*/migrations/*.py" -not -name "__init__.py" -delete
    find $GLOBAL_PATH/reservatufuturo -path "*/migrations/*.pyc" -delete
}

crear_migraciones() {
    echo -e "${GREEN}⚙️  Creando nuevas migraciones...${NC}"
    cd $GLOBAL_PATH/reservatufuturo
    python manage.py makemigrations
}

aplicar_migraciones() {
    echo -e"${GREEN}⚙️  Aplicando migraciones...${NC}"
    cd $GLOBAL_PATH/reservatufuturo
    python manage.py migrate
}

cargar_datos_iniciales() {
    if [[ -f "$GLOBAL_PATH/reservatufuturo/home/fixtures/seed.json" ]]; then
        echo -e "${GREEN}📂 Cargando datos iniciales desde seed.json...${NC}"
        cd $GLOBAL_PATH/reservatufuturo
        python manage.py loaddata seed.json
    else
        echo -e "${RED}ℹ️  No se encontró seed.json, saltando este paso...${NC}"
    fi
}

restablecer_bd_y_migraciones() {
    activar_entorno_virtual
    instalar_dependencias
    eliminar_base_datos
    eliminar_migraciones
    crear_migraciones
    aplicar_migraciones
    cargar_datos_iniciales
    crear_superusuario
    echo -e "${GREEN}🚀 ¡Base de datos restablecida y lista para usar!${NC}"
}

arrancar_servidor() {
    activar_entorno_virtual
    echo -e "${GREEN}🚀 Arrancando el servidor...${NC}"
    cd $GLOBAL_PATH/reservatufuturo
    python manage.py runserver
}

# Crear superusuario de Django
crear_superusuario() {
    activar_entorno_virtual
    if [[ $(python $GLOBAL_PATH/reservatufuturo/manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='admin').exists())") == "True" ]]; then
        echo -e "${YELLOW}ℹ️ El superusuario admin ya existe, saltando este paso...${NC}"
        return
    fi
    echo -e "${GREEN}👤 Creando superusuario...${NC}"
    cd $GLOBAL_PATH/reservatufuturo
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@admin.com', 'admin')" | python manage.py shell
    echo -e "${GREEN}✅ Superusuario creado: admin/admin${NC}"
}

# Crear entorno virtual
crear_entorno_virtual() {
    if [[ -d "$VENV_DIR" ]]; then
        echo -e "${YELLOW}ℹ️ El entorno virtual ya existe, saltando este paso...${NC}"
        return
    fi
    echo -e "${GREEN}🐍 Creando entorno virtual...${NC}"
    python3.12 -m venv $VENV_DIR
    echo -e "${GREEN}✅ Entorno virtual creado en $VENV_DIR${NC}"
}

all_in_one() {
    crear_entorno_virtual
    restablecer_bd_y_migraciones
    echo -e "${GREEN}🚀 ¡Todo listo! Arrancando servidor...${NC}"
    arrancar_servidor
}

# Ciclo del menú
while true; do
    menu
    case $opcion in
        0) all_in_one ; exit 0 ;;
        1) restablecer_bd_y_migraciones ; exit 0 ;;
        2) arrancar_servidor ; exit 0 ;;
        3) crear_superusuario ; exit 0 ;;
        4) crear_entorno_virtual ; exit 0 ;;
        5) echo -e "${RED}👋 Saliendo..."; exit 0 ;;
        *) echo -e "${RED}❌ Opción inválida, intenta de nuevo.${NC}" ; clear ;;
    esac
done
