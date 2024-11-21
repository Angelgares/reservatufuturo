# ReservaTuFuturo

## NEW! Boring Tasks Script
Script to automate boring tasks like rebuilding the database or running the server. It's a bash script that runs the commands for you.
```bash
./boring_tasks.sh
```

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

## Test Users
### User1
- **user:** user1
- **email:** user1@example.com
- **password:** pass_user_1
### User2
- **user:** user2
- **email:** user2@example.com
- **password:** pass_user_1
### Academy1 (group academy)
- **user:** academy1
- **email:** academy1@example.com
- **password:** pass_user_1