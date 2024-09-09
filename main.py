from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from model import Item, Base
from database import engine, SessionLocal
from datetime import datetime

app = FastAPI()

# Define the Pydantic models for request and response
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_available: Optional[bool] = True
    stock_quantity: Optional[int] = 0

class ItemResponse(ItemCreate):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create an item endpoint
@app.post("/items/", response_model=List[ItemResponse],status_code=status.HTTP_201_CREATED)
def create_items(items: List[ItemCreate], db: Session = Depends(get_db)):
    db_items = [Item(
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available,
        stock_quantity=item.stock_quantity
    ) for item in items]
    
    db.add_all(db_items)
    db.commit()
    
    # Refreshing items if needed
    for db_item in db_items:
        db.refresh(db_item)
    
    return db_items

# Retrieve all items endpoint
@app.get("/items/", response_model=List[ItemResponse])
def read_all_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items

# Retrieve an item endpoint
@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Update an item endpoint
@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.name = item.name
    db_item.description = item.description
    db_item.price = item.price
    db_item.is_available = item.is_available
    db_item.stock_quantity = item.stock_quantity
    db.commit()
    db.refresh(db_item)
    return db_item

# Delete an item endpoint
@app.delete("/items/{item_id}", response_model=ItemResponse)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    return db_item
