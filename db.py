from sqlalchemy_utils import database_exists, create_database, drop_database
from api import DB_URL, db

if not database_exists(DB_URL):
    create_database(DB_URL)

db.create_all()
