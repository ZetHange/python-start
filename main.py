from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from tinydb import TinyDB, Query
import json
import os

app = FastAPI()
db = TinyDB('./db.json')
usersRepository = db.table('users')
UserQuery = Query()
security = HTTPBasic()

if usersRepository.search(UserQuery.login == "string"):
    print("Создавать суперпользователя не требуется")
else:
    usersRepository.insert(
        {"id": usersRepository.count(id) + 1, "login": "string", "password": "string", "role": "ADMIN"})


class CreateUser(BaseModel):
    login: str
    password: str


@app.get("/")
def read_root(credentials: HTTPBasicCredentials = Depends(security)):
    if usersRepository.search(UserQuery.login == credentials.username and UserQuery.password == credentials.password):
        return {"statusCode": 200, "message": f"Успешно авторизован под {credentials.username}"}
    else:
        return {"statusCode": 401, "message": "Логин или пароль неверный"}


@app.get("/users")
def get_all_users():
    all_user = usersRepository.all()
    return all_user


@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    item = usersRepository.search(UserQuery.id == user_id)
    return item[0]


@app.post("/users/new")
def create_user(user: CreateUser, credentials: HTTPBasicCredentials = Depends(security)):
    if usersRepository.search(UserQuery.login == credentials.username and UserQuery.password == credentials.password):
        data = usersRepository.search(UserQuery.login == credentials.username)
        test_user = data[0]
        if test_user.get('role'):
            if usersRepository.search(UserQuery.login == user.login):
                return {"statusCode": 405, "message": "Пользователь с таким логином уже существует"}
            else:
                usersRepository.insert(
                    {"id": usersRepository.count(id) + 1, "login": user.login, "password": user.password, })
                return user
        else:
            return {"statusCode": 403, "message": "Недостаточно прав"}
    else:
        return {"statusCode": 401, "message": "Unauthorized"}


@app.get("/quests")
def get_all_quests():
    dir_quests = './quests/'
    all_dir_quests = os.listdir(dir_quests)
    quests = []
    for file in all_dir_quests:
        if os.path.isfile(os.path.join(dir_quests, file)) and file.endswith('.json'):
            quests.append(file)

    all_quests = []

    for quest in quests:
        file_quest = open(f'./quests/{quest}', 'r', encoding="utf-8")
        json_formatted = json.loads(file_quest.read())
        all_quests.append(*json_formatted['quests'])

    return all_quests


@app.get("/quests/{chapter_id}")
def get_quest_by_id(chapter_id: int):
    if os.path.isfile(f'./quests/{chapter_id}.json'):
        file_quest = open(f'./quests/{chapter_id}.json', 'r', encoding="utf-8")
        return json.loads(file_quest.read())
    else:
        return {"status": 404}
