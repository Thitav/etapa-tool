import httpx
import pymongo
import streamlit as st

from auth import auth_form
from load import load_global_data, load_user_data
from plot import barplot, distplot, lineplot, rankmetric

URL_API = "https://www.colegioetapa.com.br/ar-colegio-app-backend/v1"


@st.cache_resource
def get_http_client() -> httpx.Client:
    return httpx.Client(http2=True, base_url=URL_API)


@st.cache_resource
def get_mongo_client() -> pymongo.MongoClient:
    return pymongo.MongoClient(st.secrets["mongodb"]["uri"])


http_client = get_http_client()
mongo_client = get_mongo_client()
st.session_state.http_client = http_client
st.session_state.mongo_client = mongo_client


def app() -> None:
    user_data = load_user_data(st.session_state.user)
    global_data = load_global_data()

    toggle_filter = st.toggle("Filtrar PR, PG, SI e VF")
    if toggle_filter:
        user_data.filter(["PR", "PG", "SI", "VF"])
        global_data.filter(["PR", "PG", "SI", "VF"])

    tab_means, tab_row, tab_column, tab_element = st.tabs(
        ["Médias", "Conjuntos", "Matérias", "Provas"]
    )
    with tab_means:
        global_means = (
            global_data.get_users_attr("filtered_mean")
            .sort_values(ignore_index=True)
            .dropna()
            .drop_duplicates()
        )

        rankmetric(user_data.filtered_mean, global_data.filtered_mean, global_means)
        distplot(global_means, 10, "Alunos", "Média")
    with tab_row:
        lineplot(
            global_data.filtered_row_mean.rename(lambda n: f"Conjunto {n+1}"),
            xtitle="Conjunto",
            ytitle="Média",
            pct_change=True,
        )
    with tab_column:
        barplot(user_data.column_mean.sort_values(), xtitle="Código", ytitle="Média")

        sel_column = st.selectbox("Código", user_data.data.columns, key=1)
        lineplot(
            user_data.data[sel_column].rename(lambda n: f"Conjunto {n+1}"),
            xtitle="Conjunto",
            ytitle="Nota",
            pct_change=True,
        )
    with tab_element:
        col_column, col_row = st.columns(2)
        with col_column:
            sel_column = st.selectbox("Código", user_data.data.columns, key=2)
        with col_row:
            sel_row = (
                st.selectbox(
                    "Conjunto",
                    [
                        i + 1
                        for i in user_data.data.index
                        if not all(global_data.get_users_data(sel_column, i).isnull())
                    ],
                )
                - 1
            )

        element_global = (
            global_data.get_users_data(sel_column, sel_row)
            .dropna()
            .sort_values(ignore_index=True)
        )

        rankmetric(
            user_data.data[sel_column][sel_row],
            element_global.mean(),
            element_global.drop_duplicates(),
        )
        distplot(element_global, xtitle="Alunos", ytitle="Nota")


if "user" not in st.session_state:
    auth_form()
else:
    app()
