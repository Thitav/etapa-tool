import json

import httpx
import streamlit as st

PATH_AUTH = "/login/aluno"


def auth_form() -> None:
    http_client: httpx.Client = st.session_state.http_client

    with st.form("auth_form"):
        st.header("Login")

        username = st.text_input("Matrícula")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Carregar")

        if submit:
            user_data = http_client.post(
                PATH_AUTH, data={"matricula": username, "senha": password}
            )
            user_data = json.loads(user_data.content.decode("utf-8"))

            if "body" in user_data:
                auth_token = f"{user_data['body']['token']}:{username}"
                http_client.headers["Auth-Token"] = auth_token

                st.session_state.user = user_data["body"]
                st.experimental_rerun()
            else:
                st.error("Login inválido")
