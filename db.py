from sqlalchemy_utils import database_exists, create_database, drop_database
from api import DB_URL, db

if database_exists(DB_URL):
    print('Deleting database.')
    drop_database(DB_URL)
if not database_exists(DB_URL):
    print('Creating database.')
    create_database(DB_URL)

print('Creating tables.')
db.create_all()
print('Shiny!')