from sqlalchemy import Column , String , Integer ,Numeric
from database import Base

class Product(Base):
    __tablename__="products"
    id= Column(Integer ,primary_key=True)
    name=Column(String(100),nullable=False)
    price=Column(Numeric(10,2), nullable=False)
    quantity=Column(Integer, nullable=False)
    brand = Column(String, nullable=True)
    