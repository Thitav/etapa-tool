import json

import httpx
import numpy as np
import pandas as pd
import pymongo
import streamlit as st

from data import GlobalData, UserData

PATH_DATA = "/provas/notas?grau={}&local={}&matricula={}&serie={}&unidade={}"


@st.cache_data
def load_user_data(user: dict) -> UserData:
    http_client: httpx.Client = st.session_state.http_client
    user_data = http_client.get(
        PATH_DATA.format(
            user["grau"],
            user["local"],
            user["matricula"],
            user["serie"],
            user["unidade"],
        )
    )
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
    user_data = user_data.rename(
        {"celula": "Código", "conj1": 0, "conj2": 1, "conj3": 2, "conj4": 3}, axis=1
    )
    user_data = user_data.replace({"---": np.nan, "F*": np.nan, "F**": np.nan})
    user_data = user_data.set_index("Código")
    user_data = user_data.astype(float).transpose()

    return UserData(user_data)


@st.cache_data(ttl=300)
def load_global_data() -> GlobalData:
    mongo_client: pymongo.MongoClient = st.session_state.mongo_client
    collection = mongo_client.etapatool.alunos
    global_data = collection.find({}, {"notas": True, "_id": False})

    return GlobalData([UserData(pd.DataFrame(user["notas"])) for user in global_data])
