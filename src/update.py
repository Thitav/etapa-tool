import os
import json
import httpx
import pandas as pd
from pymongo.mongo_client import MongoClient

URL_API = "https://www.colegioetapa.com.br/ar-colegio-app-backend/v1"
URL_LOGIN = "/login/aluno"
URL_DATA = "/provas/notas?matricula={}&local=vl"

http_client = httpx.Client(http2=True, base_url=URL_API)
mongo_client = MongoClient(os.getenv("MONGODB"))

col = mongo_client.etapatool.alunos

res = http_client.post(
    URL_LOGIN, data={"matricula": os.getenv("USERNAME"), "senha": os.getenv("PASSWORD")}
)
res = json.loads(res.content.decode("utf-8"))["body"]
http_client.headers["Auth-Token"] = f"{res['token']}:{res['matricula']}"

users = col.find({})
for user in users:
    print(f"[+] Updating data for user {user['matricula']}...")

    user_data = http_client.get(URL_DATA.format(user["matricula"]))
    user_data = json.loads(user_data.content.decode("utf-8"))["prvNotas"]

    user_data = pd.DataFrame(user_data)
    user_data = user_data.drop(
        [
            "materia",
            "class1",
            "class2",
            "class3",
            "class4",
            "link1",
            "link2",
            "link3",
            "link4",
        ],
        axis=1,
    )
    user_data = user_data.set_index("celula")
    user_data = user_data.replace({"---": None, "F*": None, "F**": None})
    user_data = user_data.astype(float).transpose().to_dict()
    for i in user_data:
        user_data[i] = list(user_data[i].values())

    col.update_one({"_id": user["_id"]}, {"$set": {"notas": user_data}})
    print(f"[+] Updated data for user {user['matricula']}")
