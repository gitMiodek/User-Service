from sqlmodel import create_engine

DATABASE_URL = "postgresql://postgres:password@DB:5432/postgres"
engine = create_engine(DATABASE_URL,echo=False)
