from typing import cast
import pandas as pd
import streamlit as st
import plotly.express as px
from pymongo import MongoClient
from st_pages import show_pages_from_config, hide_pages
from streamlit_extras.switch_page_button import switch_page

show_pages_from_config()
hide_pages(["Login"])

if "user" in st.session_state:
    user = st.session_state["user"]
    http_client = st.session_state["http_client"]
else:
    switch_page("login")


@st.cache_resource
def get_mongo_client() -> MongoClient:
    return MongoClient(st.secrets["mongodb"]["uri"])


mongo_client = get_mongo_client()


@st.cache_data
def load_global_data() -> pd.DataFrame:
    col = mongo_client.etapatool.alunos
    data = col.find({}, {"notas": True, "_id": False})

    data = pd.DataFrame([i["notas"] for i in data])
    data = (
        pd.DataFrame(
            [
                [
                    pd.Series(value).dropna().sort_values(ignore_index=True)
                    for value in zip(*data[column])
                ]
                for column in data
            ],
            index=data.columns,
        )
        .transpose()
        .reindex(range(1, 4))
    )

    return data


global_data = load_global_data()

global_mean = cast(float, pd.concat([*global_data.to_numpy().flatten()]).mean())

st.title("Análise Geral")
st.metric("Média do ano:", round(global_mean, 2))

st.title("Matérias")
col_column, col_index = st.columns(2)
with col_column:
    column = st.selectbox("Código", global_data.columns)
    column = cast(str, column)
with col_index:
    index = st.selectbox(
        "Conjunto",
        [i for i in global_data.index if not all(global_data[column][i].isna())],
    )
    index = cast(int, index)

st.metric("Média:", round(global_data[column][index].mean(), 2))
st.plotly_chart(
    px.bar(
        global_data[column][index],
        y=0,
        range_y=[0, 10],
        labels={
            "0": "Nota",
            "index": "Alunos",
        },
    ),
    use_container_width=True,
)
