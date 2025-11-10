from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_USER = "root"
DB_PASSWORD = ""  # leave empty unless you have a password
DB_NAME = "ursaviourDb"

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()
