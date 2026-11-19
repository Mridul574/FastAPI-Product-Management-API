from fastapi import FastAPI , HTTPException , Depends ,Query
from pydantic import BaseModel , field_validator , Field , ConfigDict
from database import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Product as dbProduct
from typing import Literal

app = FastAPI()

class Product(BaseModel):
    id:int
    name:str
    price:float
    quantity:int

class CreateProduct(BaseModel):
    name:str = Field(min_length=1 , max_length=100)
    price:float = Field(gt=0)
    quantity:int = Field(ge=0)

class ProductResponse(BaseModel):
    id:int
    name:str
    price:float
    quantity:int 

    model_config= ConfigDict(from_attributes=True)

class UpdateProduct(BaseModel):
    name :str | None = Field(default=None ,min_length=0 , max_length=100)
    price :float | None = Field(default=None , gt=0)
    quantity:int | None = Field(default=None , ge=0)

    @field_validator("name" ,"price","quantity", mode="before")
    @classmethod
    def value_not_null(cls , value):
        if value is None :
            raise ValueError("value can't be None")
        return value

@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=201
    )
def create_product(
    product:CreateProduct,
    db:Session = Depends(get_db)
):
    new_product= dbProduct(
        name=product.name,
        price=product.price,
        quantity=product.quantity
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get("/products", response_model=list[ProductResponse])
def get_products(
    min_price: float | None = None,
    max_price: float | None = None,
    name: str | None = None,

    sort_by: Literal["price", "name", "quantity"] = "price",
    order: Literal["asc", "desc"] = "asc",

    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),

    db: Session = Depends(get_db)
):

    # STEP 1: Start with all products
    query = select(dbProduct)

    # STEP 2: FILTERING

    if min_price is not None:
        query = query.where(dbProduct.price >= min_price)

    if max_price is not None:
        query = query.where(dbProduct.price <= max_price)

    if name is not None:
        query = query.where(dbProduct.name.ilike(f"%{name}%"))

    # STEP 3: SORTING

    sort_columns = {
        "price": dbProduct.price,
        "name": dbProduct.name,
        "quantity": dbProduct.quantity
    }

    sort_column = sort_columns[sort_by]

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # STEP 4: PAGINATION

    limit = min(limit, 50)

    query = query.offset(offset).limit(limit)

    # STEP 5: EXECUTE QUERY

    result = db.execute(query)
    products = result.scalars().all()

    return products

@app.get("/products/{product_id}",
         response_model=ProductResponse)
def get_product(
    product_id:int,
    db:Session=Depends(get_db)):
    product= db.get(dbProduct ,product_id)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )
    else:
        return product

@app.put(
    "/products/{product_id}",
    response_model=ProductResponse
    )
def put_product(
    product_id:int,
    product:CreateProduct,
    db:Session=Depends(get_db)
    ):
    existing_product=db.get(dbProduct ,product_id)
    if existing_product is None :
        raise HTTPException(
            status_code=404,
            detail="not found"
        )
    
    existing_product.name= product.name
    existing_product.price=product.price
    existing_product.quantity=product.quantity
    db.commit()
    db.refresh(existing_product)
    return existing_product

@app.patch(
    "/products/{product_id}",
    response_model=ProductResponse
    )
def patch_product(
    product_id:int,
    product:UpdateProduct,
    db:Session=Depends(get_db)
):
    existing_product=db.get(dbProduct ,product_id)
    if existing_product is None:
        raise HTTPException(
            status_code=404,
            detail="not found"
        )
    
    update_data = product.model_dump(exclude_unset=True)

    for key , value in update_data.items():
        setattr(existing_product , key , value)

    db.commit()
    db.refresh(existing_product)
    return existing_product

@app.delete(
    "/products/{product_id}"
)
def delete_product(
    product_id:int,
    db:Session=Depends(get_db)
):
    existing_product = db.get(dbProduct , product_id)
    if existing_product is None:
        raise HTTPException(
            status_code=404,
            detail="not found"
        )
    db.delete(existing_product)
    db.commit()
    return {"message":"deleted successfully"}
    
