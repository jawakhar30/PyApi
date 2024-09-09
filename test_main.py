import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from model import Base
from test_db import test_engine,TestSessionLocal

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the override for all routes in the test
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def setup_test_db():
    # Create tables in the test database
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop tables after the test
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_item(client, setup_test_db):
    response = client.post("/items/", json=[{
        "name": "Test1",
        "description": "Test Description",
        "price": 10.99,
        "is_available": True,
        "stock_quantity": 50
    }])
    assert response.status_code == 201
    data = response.json()
    assert data[0]["name"] == "Test1"

def test_read_items(db_session, client, setup_test_db):
   # Insert an item into the test database directly using db_session
    db_session.execute(text("""
        INSERT INTO items (name, description, price, is_available, stock_quantity) 
        VALUES ('Item2', 'Description', 20.99, TRUE, 200)
    """))
    db_session.commit()

    # Make a GET request to read the inserted item
    response = client.get("/items/")
    assert response.status_code == 200
    items = response.json()
    
    # Assert the correct number of items and item details
    assert len(items) == 1
    assert items[0]["name"] == "Item2"
def test_update_item(db_session, client, setup_test_db):
    # Insert an item into the test database
    db_session.execute(text("""
        INSERT INTO items (name, description, price, is_available, stock_quantity) 
        VALUES ('Item3', 'Old Description', 30.99, TRUE, 300)
    """))
    db_session.commit()

    # Update the item using a PUT or PATCH request
    response = client.put("/items/1", json={
        "name": "Item3",
        "description": "Updated Description",
        "price": 30.99,
        "is_available": True,
        "stock_quantity": 300
    })
    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item["description"] == "Updated Description"

    # Verify the update
    read_response = client.get("/items/")
    items = read_response.json()
    assert len(items) == 1
    assert items[0]["description"] == "Updated Description"

# Test: Delete item
def test_delete_item(db_session, client, setup_test_db):
    # Insert an item into the test database
    db_session.execute(text("""
        INSERT INTO items (name, description, price, is_available, stock_quantity) 
        VALUES ('Item4', 'To be deleted', 40.99, TRUE, 400)
    """))
    db_session.commit()

    # Delete the item using a DELETE request
    response = client.delete("/items/1")
    assert response.status_code == 200

    # Verify the item was deleted
    read_response = client.get("/items/")
    items = read_response.json()
    assert len(items) == 0