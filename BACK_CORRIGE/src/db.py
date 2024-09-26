from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:880708@localhost/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def execute_query(query: str, params: dict = None):
    with SessionLocal() as session:
        result = session.execute(text(query), params or {})
        session.commit()
        return result.fetchall()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
