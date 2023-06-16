import json
from math import nan
import httpx
import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import show_pages_from_config, hide_pages


URL_API = "https://www.colegioetapa.com.br/ar-colegio-app-backend/v1"
PATH_LOGIN = "/login/aluno"
PATH_DATA = "/provas/notas?grau={}&local={}&matricula={}&serie={}&unidade={}"

st.set_page_config(initial_sidebar_state="collapsed")
show_pages_from_config()
hide_pages(["Login", "Pessoal", "Geral"])


@st.cache_resource
def get_http_client() -> httpx.Client:
    return httpx.Client(http2=True, base_url=URL_API)


http_client = get_http_client()


@st.cache_data
def load_user_data(user):
    data = http_client.get(
        PATH_DATA.format(
            user["grau"],
            user["local"],
            user["matricula"],
            user["serie"],
            user["unidade"],
        )
    )
    data = json.loads(data.content.decode("utf-8"))["prvNotas"]

    data = pd.DataFrame(data)
    data = data.drop(
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
    data = data.rename(
        {"celula": "Código", "conj1": 1, "conj2": 2, "conj3": 3, "conj4": 4}, axis=1
    )
    data = data.replace({"---": nan, "F*": nan, "F**": nan})
    data = data.set_index("Código")
    data = data.astype(float)

    return data


with st.form("auth_form"):
    st.header("Login")

    username = st.text_input("Matrícula")
    password = st.text_input("Senha", type="password")
    submit = st.form_submit_button("Carregar")

    if submit:
        user_data = http_client.post(
            PATH_LOGIN, data={"matricula": username, "senha": password}
        )
        user_data = json.loads(user_data.content.decode("utf-8"))

        if "body" in user_data:
            http_client.headers[
                "Auth-Token"
            ] = f"{user_data['body']['token']}:{username}"
            st.session_state["http_client"] = http_client

            user = user_data["body"]
            user["notas"] = load_user_data(user)
            st.session_state["user"] = user

            switch_page("Pessoal")
        else:
            st.error("Login inválido")
