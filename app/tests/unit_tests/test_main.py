import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, delete
from models.models import UserTable
from main import app

client = TestClient(app)


@pytest.fixture(name="session")
def session_fixture():
    db_url = "postgresql://postgres:password@DB:5432/postgres"
    engine = create_engine(db_url, echo=False)
    with Session(engine) as session:
        yield session


def response_for_put_method():
    return {"nickname": "logan",
            "email": "white@gmail.com",
            "countryCode": "US",
            "dateOfBirth": "18-04-1997",
            "firstName": "Joe",
            "lastName": "Warren",
            "gender": "male",
            "id": 6}


def mutually_exclusive():
    """
    Response for a situation when 2 or more query params are given
    :return:
    a proper JSON
    """
    return {
        "INFO": "Given more than one argument!Choose between ids, nickname or email"
    }


def wrong_type():
    """
    Response for a situation when a query param is wrong type
    :return:
    a proper JSON
    """
    return {"WARNING": "Invalid data type!"}


def user_not_found():
    """
    Response for a situation when a user is not found in the database
    :return:
    """
    return {"message": "User not found in the database!"}


def create_fake_user():
    user = UserTable(nickname="white",
                     email="white@gmail.com",
                     countryCode="US",
                     dateOfBirth="18-04-1997",
                     firstName="Joe",
                     lastName="Warren",
                     gender="male",
                     id=6)
    return user


def create_2_fake_users_for_get_all():
    user1 = UserTable(nickname="white",
                      email="white@gmail.com",
                      countryCode="US",
                      dateOfBirth="18-04-1997",
                      firstName="Joe",
                      lastName="Warren",
                      gender="male",
                      id=6)
    user2 = UserTable(nickname="mamacita",
                      email="bigmommy@gmail.com",
                      countryCode="US",
                      dateOfBirth="18-03-1989",
                      firstName="Lara",
                      lastName="Hammilton",
                      gender="female",
                      id=7)
    return user1, user2


def response_fake_user():
    return {"nickname": "white",
            "email": "white@gmail.com",
            "countryCode": "US",
            "dateOfBirth": "18-04-1997",
            "firstName": "Joe",
            "lastName": "Warren",
            "gender": "male",
            "id": 6}


def response_get_all():
    return [
        {
            "countryCode": "US",
            "firstName": "Joe",
            "email": "white@gmail.com",
            "gender": "male",
            "nickname": "white",
            "dateOfBirth": "18-04-1997",
            "lastName": "Warren",
            "id": 6
        },
        {
            "countryCode": "US",
            "firstName": "Lara",
            "email": "bigmommy@gmail.com",
            "gender": "female",
            "nickname": "mamacita",
            "dateOfBirth": "18-03-1989",
            "lastName": "Hammilton",
            "id": 7
        }
    ]


def response_email():
    return [
        {
            "countryCode": "US",
            "firstName": "Lara",
            "email": "bigmommy@gmail.com",
            "gender": "female",
            "nickname": "mamacita",
            "dateOfBirth": "18-03-1989",
            "lastName": "Hammilton",
            "id": 7
        }
    ]


def response_nickname():
    return [
        {
            "countryCode": "US",
            "firstName": "Joe",
            "email": "white@gmail.com",
            "gender": "male",
            "nickname": "white",
            "dateOfBirth": "18-04-1997",
            "lastName": "Warren",
            "id": 6
        }
    ]


def test_create_user(session: Session):
    response = client.post("/v2/users", json={
        "nickname": "string",
        "email": "string",
        "countryCode": "string",
        "dateOfBirth": "string",
        "firstName": "string",
        "lastName": "string",
        "gender": "string"
    })
    data = response.json()
    assert response.status_code == 200
    assert data['nickname'] == 'string'
    assert data['email'] == 'string'
    assert data['countryCode'] == 'string'
    assert data['dateOfBirth'] == 'string'
    assert data['firstName'] == 'string'
    assert data['lastName'] == 'string'
    assert data['gender'] == 'string'
    assert data['id'] is not None

    session.execute(delete(UserTable))
    session.commit()


def test_create_user_wrong_method():
    response = client.put("/v2/users")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


def test_get_user_id(session: Session):
    session.add(create_fake_user())
    session.commit()
    response = client.get("/v2/users/6")

    assert response.status_code == 200
    assert response.json() == response_fake_user()
    session.execute(delete(UserTable))
    session.commit()


def test_get_user_not_found_id():
    response = client.get("/v2/users/5")
    assert response.status_code == 404
    assert response.json() == user_not_found()


def test_get_user_wrong_id_type():
    response = client.get("/v2/users/str")
    assert response.status_code == 400
    assert response.json() == wrong_type()


def test_get_user_wrong_method():
    response = client.post("/v2/users/str")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


def test_update_user(session: Session):
    session.add(create_fake_user())
    session.commit()

    response = client.put(
        "/v2/users/6",
        json={"nickname": "logan",
              "email": "white@gmail.com",
              "countryCode": "US",
              "dateOfBirth": "18-04-1997",
              "firstName": "Joe",
              "lastName": "Warren",
              "gender": "male"}
    )
    assert response.status_code == 200
    assert response.json() == response_for_put_method()
    session.execute(delete(UserTable))
    session.commit()


def test_update_no_user_found():
    response = client.put(
        "/v2/users/8",
        json={
            "countryCode": "ENG",
            "dateOfBirth": "16-08-2000",
            "firstName": "Kuba",
            "lastName": "Olszewski",
            "nickname": "Olsza",
            "gender": "male",
            "email": "olcza420@gmail.com",
        },
    )
    assert response.status_code == 404
    assert response.json() == user_not_found()


def test_update_user_wrong_id_type():
    response = client.put(
        "/v2/users/str",
        json={
            "countryCode": "ENG",
            "dateOfBirth": "16-08-2000",
            "firstName": "Kuba",
            "lastName": "Olszewski",
            "nickname": "Olsza",
            "gender": "male",
            "email": "olcza420@gmail.com",
        },
    )
    assert response.status_code == 400
    assert response.json() == wrong_type()


def test_delete_user(session: Session):
    session.add(create_fake_user())
    session.commit()
    response = client.delete("/v2/users/6")
    assert response.status_code == 200


def test_delete_user_not_found():
    response = client.delete("/v2/users/8")
    assert response.status_code == 404
    assert response.json() == user_not_found()


def test_delete_user_wrong_id_type():
    response = client.delete("/v2/users/str")
    assert response.status_code == 400
    assert response.json() == wrong_type()


@pytest.mark.parametrize(
    "test_input,expected,status_code",
    [
        ("/v2/users", response_get_all(), 200),
        ("/v2/users?nickname=white", response_nickname(), 200),
        ("/v2/users?ids=6&ids=7", response_get_all(), 200),
        (
                "/v2/users?email=bigmommy@gmail.com",
                response_email(),
                200,
        ),
        ("/v2/users?email=pis@gmail.com&ids=1", mutually_exclusive(), 400),
        ("/v2/users?email=pis@gmail.com&nickname=kaczor", mutually_exclusive(), 400),
        ("/v2/users?nickname=kaczor&ids=1", mutually_exclusive(), 400),
        (
                "/v2/users?email=pis@gmail.com&ids=1&nickname=kaczor",
                mutually_exclusive(),
                400,
        ),
        ("/v2/users?ids=str", wrong_type(), 400),
        ("/v2/users?email=yoho@gmail.com", user_not_found(), 404),
        ("/v2/users?ids=10", user_not_found(), 404),
        ("/v2/users?nickname=andrewtate", user_not_found(), 404)
    ]
)
def test_get_all_users(test_input, expected, status_code, session: Session):
    user_1, user_2 = create_2_fake_users_for_get_all()
    session.add(user_1)
    session.add(user_2)
    session.commit()
    response = client.get(test_input)
    assert response.status_code == status_code
    assert response.json() == expected
    session.execute(delete(UserTable))
    session.commit()
