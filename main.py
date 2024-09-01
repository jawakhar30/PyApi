from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model import Item,Base
from database import engine,SessionLocal
app = FastAPI()





# Define the Pydantic model for request and response
class ItemCreate(BaseModel):
    name: str
    description: str

# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Create an item endpoint
@app.post("/items/", response_model=ItemCreate)
def create_item(item: ItemCreate):
    db = SessionLocal()
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

# Retrieve all items endpoint
@app.get("/items/", response_model=List[ItemCreate])
def read_all_items(skip: int = 0, limit: int = 10):
    db = SessionLocal()
    items = db.query(Item).offset(skip).limit(limit).all()
    db.close()
    return items

# Retrieve an item endpoint
@app.get("/items/{item_id}", response_model=ItemCreate)
def read_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    db.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Update an item endpoint
@app.put("/items/{item_id}", response_model=ItemCreate)
def update_item(item_id: int, item: ItemCreate):
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.name = item.name
    db_item.description = item.description
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

# Delete an item endpoint
@app.delete("/items/{item_id}", response_model=ItemCreate)
def delete_item(item_id: int):
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    db.close()
    return db_item
