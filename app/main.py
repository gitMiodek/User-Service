import uvicorn
import json
from redis import Redis
from sqlmodel import SQLModel, Session, select
from fastapi import FastAPI, status, Query, Response, Request, BackgroundTasks
from fastapi_redis_cache import FastApiRedisCache
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from models.models import UserTable, UserRead, UserCreate, UserNotification
from db.database import engine
from publisher import publisher

app = FastAPI()

LOCAL_REDIS_URL = "redis://redis:6379"
redis_host = 'redis'


class My404Exception(Exception):
    pass


@app.exception_handler(My404Exception)
async def custom_404(*args, **kwargs):
    return JSONResponse(
        status_code=404, content={"message": "User not found in the database!"}
    )


# Override of data validation error to create nice 400 Error (invalid data type)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(*args, **kwargs):
    return JSONResponse(status_code=400, content={"WARNING": "Invalid data type!"})


class MutuallyExclusiveException(Exception):
    pass


@app.exception_handler(MutuallyExclusiveException)
async def mutually_exclusive_except(*args, **kwargs):
    return JSONResponse(
        status_code=400,
        content={
            "INFO": "Given more than one argument!"
                    "Choose between ids, nickname or email"
        },
    )


responses_id = {
    200: {"description": "Successful operation"},
    400: {"description": "Invalid Parameter Received"},
    404: {"description": "User Not Found"},
    405: {"description": "Method Not Allowed"},
    500: {"description": "Internal Server Error"},
    503: {"description": "Service Unavailable"},
}
responses_no_id = {
    200: {"description": "Successful operation"},
    400: {"description": "Invalid Parameter Received"},
    405: {"description": "Method Not Allowed"},
    500: {"description": "Internal Server Error"},
    503: {"description": "Service Unavailable"},
}


def create_table():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def start_up():
    create_table()
    FastApiRedisCache().init(
        host_url=LOCAL_REDIS_URL,
        prefix="Users-Cache",
        response_header="X-Users-Cache",
        ignore_arg_types=[Request, Response, Session]
    )


def filter_helper_ids(index_list: list[int], session: Session):
    res_list = []
    for idx in index_list:
        res = session.get(UserTable, idx)
        if res:
            res_list.append(session.get(UserTable, idx))
    return res_list


def filter_helper_emai(email: str, session: Session):
    res = session.exec(select(UserTable).where(UserTable.email == email)).all()
    idx = session.exec(select(UserTable.id).where(UserTable.email == email)).all()
    return res, idx


def filter_helper_nickname(nickname: str, session: Session):
    res = session.exec(select(UserTable).where(UserTable.nickname == nickname)).all()
    idx = session.exec(select(UserTable.id).where(UserTable.nickname == nickname)).all()
    return res, idx


def filter_helper_get_all_users(session: Session):
    qr = select(UserTable)
    res = session.exec(qr).all()
    idx = session.exec(select(UserTable.id)).all()
    return res, idx


def create_key_user_id(id, value):
    try:
        FastApiRedisCache().add_to_cache(f"Users-Cache:main.get_user_id(id={id})"
                                         , value, expire=180)
    except AttributeError as e:
        print(e)


def create_key_filter(id, value):
    try:
        FastApiRedisCache().add_to_cache(f'Users-Cache:main.get_all_users(id={id})', value, expire=180)
    except AttributeError as e:
        print(e)


def del_cache(idx):
    r = Redis(redis_host)
    keys = r.keys(f'*{idx}*')
    r.delete(*keys)


def take_user_from_cache_id(id):
    r = Redis(redis_host)
    user = r.get(f"Users-Cache:main.get_user_id(id={id})")
    if user:
        user = json.loads(user)
        return user


def take_users_from_cache_filter(id):
    r = Redis(redis_host)
    user = r.get(f'Users-Cache:main.get_all_users(id={id})')
    if user:
        user = json.loads(user)
        return user


@app.post("/v2/users", response_model=UserRead, responses=responses_no_id, status_code=status.HTTP_200_OK)
async def create_users(user: UserCreate, background_task: BackgroundTasks):
    with Session(engine) as session:
        db_user = UserTable.from_orm(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    user_event = UserNotification(operation='Create user', user=user.dict())
    background_task.add_task(publisher, user_event)

    try:
        del_cache(db_user.id)
    except Exception as e:
        print(e)
    return db_user


@app.get("/v2/users", responses=responses_id, status_code=status.HTTP_200_OK)
async def get_all_users(response: Response, ids: list[int] = Query(default=None),
                        nickname: str = Query(default=None),
                        email: str = Query(default=None)):
    with Session(engine) as session:

        legit_params = [param for param in [nickname, ids, email] if param is not None]

        if len(legit_params) == 0:
            result, idx = filter_helper_get_all_users(session)

        elif len(legit_params) > 1:
            raise MutuallyExclusiveException()
        if ids:
            result = filter_helper_ids(ids, session)
            idx = ids
        elif nickname:
            result, idx = filter_helper_nickname(nickname, session)
        elif email:
            result, idx = filter_helper_emai(email, session)
    if take_users_from_cache_filter(idx):
        decoded_result = take_users_from_cache_filter(idx)
    else:
        decoded_result = jsonable_encoder(result)
        create_key_filter(idx, decoded_result)
    if not decoded_result:
        raise My404Exception
    else:
        return decoded_result


@app.get("/v2/users/{id}", response_model=UserRead, responses=responses_id, status_code=status.HTTP_200_OK)
async def get_user_id(id: int, response: Response):
    with Session(engine) as session:
        if take_user_from_cache_id(id):
            encoded_user = take_user_from_cache_id(id)
        else:
            user_id = session.get(UserTable, id)
            encoded_user = jsonable_encoder(user_id)
            create_key_user_id(id, encoded_user)
    if not encoded_user:
        raise My404Exception

    return encoded_user


@app.delete("/v2/users/{id}", responses=responses_id, status_code=status.HTTP_200_OK)
async def delete_user(id: int, background_task: BackgroundTasks):
    with Session(engine) as session:
        user = session.get(UserTable, id)
        if not user:
            raise My404Exception
        session.delete(user)
        session.commit()
        user_event = UserNotification(operation='Delete usere', user=user.dict())
        background_task.add_task(publisher, user_event)
    try:
        del_cache(id)
    except Exception:
        pass


@app.put("/v2/users/{id}", response_model=UserRead, responses=responses_id, status_code=status.HTTP_200_OK)
async def update_user(id: int, user: UserCreate, background_task: BackgroundTasks):
    with Session(engine) as session:
        user_id = session.get(UserTable, id)
        if not user_id:
            raise My404Exception
        db_user = user.dict()
        for k, v in db_user.items():
            setattr(user_id, k, v)
        session.add(user_id)
        session.commit()
        session.refresh(user_id)
    user_event = UserNotification(operation='Update user', user=user.dict())
    background_task.add_task(publisher, user_event)
    try:
        del_cache(id)
    except Exception:
        pass

    return user_id


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
