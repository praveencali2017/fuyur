import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

DB_NAME = 'fyyur_db'
# Done IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:post@localhost:5432/'+DB_NAME
SQLALCHEMY_TRACK_MODIFICATIONS = False
