from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Test database URL
TEST_DATABASE_URL = "postgresql+psycopg2://postgres:abc123@localhost:5432/test_db"

# Create a new engine and session for the test database
test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base = declarative_base()

