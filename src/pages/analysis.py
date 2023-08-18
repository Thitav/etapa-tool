from typing import cast
import pandas as pd
from numpy import nan
import streamlit as st
import plotly.express as px
from pymongo import MongoClient
from st_pages import show_pages_from_config, hide_pages
from streamlit_extras.switch_page_button import switch_page

show_pages_from_config()
hide_pages(["Login"])

if "user" not in st.session_state:
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

    data = pd.DataFrame(
        [
            [pd.Series(value) for value in zip(*list(data[column].apply(lambda x: [nan]*4 if isinstance(x, float) else x)))] 
            for column in data
        ],
         index=data.columns,
     ).transpose()

    return data


user_data = st.session_state["user"]["data"]
user_dataframe: pd.DataFrame = user_data["dataframe"]
user_mean = user_data["mean"]

global_data = load_global_data()
global_mean = cast(float, pd.concat([*global_data.to_numpy().flatten()]).mean())

st.title("Análise Geral")

col_global_mean, col_user_mean = st.columns(2)
with col_global_mean:
    st.metric("Média do ano", round(global_mean, 2))
with col_user_mean:
    mean_delta = ((user_mean / global_mean) - 1) * 100
    st.metric("Sua média", round(user_data["mean"], 2), f"{round(mean_delta, 2)}%")

st.header("Matérias")
col_column, col_index = st.columns(2)
with col_column:
    column = st.selectbox("Código", global_data.columns)
    column = cast(str, column)
with col_index:
    index = st.selectbox(
        "Conjunto",
        [i + 1 for i in global_data.index if not all(global_data[column][i].isna())],
    )
    index = cast(int, index) - 1


element_mean = global_data[column][index].mean()
element_delta = ((user_dataframe[column][index] / element_mean) - 1) * 100

col_global_mean, col_user_mean = st.columns(2)
with col_global_mean:
    st.metric("Média", round(element_mean, 2))
with col_user_mean:
    st.metric("Sua nota", user_dataframe[column][index], f"{round(element_delta, 2)}%")

st.plotly_chart(
    px.bar(
        global_data[column][index].dropna().sort_values(ignore_index=True),
        y=0,
        range_y=[0, 10],
        labels={
            "0": "Nota",
            "index": "Alunos",
        },
    ),
    use_container_width=True,
)
st.caption(f"Desvio padrão: {round(global_data[column][index].std(), 2)}")
