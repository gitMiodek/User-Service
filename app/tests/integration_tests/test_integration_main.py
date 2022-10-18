from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, delete
from main import app
from models.models import UserTable


client = TestClient(app)

db_url = "postgresql://postgres:password@DB:5432/postgres"
engine = create_engine(db_url, echo=False)


def test_db_connect():
    connection = engine.connect()

    response_post = client.post("/v2/users", json={
        "nickname": "Heisenberg",
        "email": "chemistryTeacher@hotmail.com",
        "countryCode": "US",
        "dateOfBirth": "17-03-1976",
        "firstName": "Walter",
        "lastName": "White",
        "gender": "male"})
    data = response_post.json()

    response_get = client.get(f"/v2/users/{data['id']}")

    assert connection
    assert response_post.status_code == 200
    assert response_get.status_code == 200
    assert response_get.json() == {
        "nickname": "Heisenberg",
        "email": "chemistryTeacher@hotmail.com",
        "countryCode": "US",
        "dateOfBirth": "17-03-1976",
        "firstName": "Walter",
        "lastName": "White",
        "gender": "male",
        "id": data['id']}
    with Session(bind=connection) as session:
        session.execute(delete(UserTable))
        session.commit()



