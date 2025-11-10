from sqlalchemy import Column, Integer, Boolean, DECIMAL, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from database import engine

Base = declarative_base()

class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    favorite = Column(Boolean, default=False)
    last_known_price = Column(DECIMAL(10, 2))
    added_at = Column(TIMESTAMP, server_default=func.now())

Base.metadata.create_all(bind=engine)
