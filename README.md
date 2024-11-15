# ReservaTuFuturo

## Dependencies
```bash
cd reservatufuro
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running
```bash
cd reservatufuturo
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata seed.json
python manage.py runserver
```

