from numpy import isnan
import plotly.express as px
import streamlit as st
import pandas as pd
from st_pages import show_pages_from_config, hide_pages
from streamlit_extras.switch_page_button import switch_page

show_pages_from_config()
hide_pages(["Login"])

if "user" in st.session_state:
    user = st.session_state["user"]
    http_client = st.session_state["http_client"]
else:
    switch_page("login")

user_data: pd.DataFrame = st.session_state["user"]["notas"]

mean = user_data.to_numpy().flatten()
mean = mean[~isnan(mean)].mean()

means = user_data.mean()

st.title("Análise Pessoal")
st.metric("Média:", round(mean, 2))
st.title("Notas")
st.dataframe(
    user_data.rename(
        columns={1: "Conjunto 1", 2: "Conjunto 2", 3: "Conjunto 3", 4: "Conjunto 4"}
    )
)

st.title("Conjuntos")
st.dataframe(
    means.rename("Média").rename(
        {
            1: "Conjunto 1",
            2: "Conjunto 2",
            3: "Conjunto 3",
            4: "Conjunto 4",
        }
    )
)
st.plotly_chart(
    px.line(
        means.rename(
            {
                1: "Conjunto 1",
                2: "Conjunto 2",
                3: "Conjunto 3",
                4: "Conjunto 4",
            }
        ),
        y=0,
        range_y=[0, 10],
        markers=True,
        labels={"0": "Média", "index": "Conjunto"},
    ),
    use_container_width=True,
)


st.title("Matérias")
st.plotly_chart(
    px.bar(
        user_data.mean(axis=1).sort_values(),
        y=0,
        range_y=[0, 10],
        labels={
            "value": "Média",
        },
    ),
    use_container_width=True,
)

column = st.selectbox("Código", user_data.index)

st.plotly_chart(
    px.line(
        user_data.transpose()[column]
        .rename(
            {
                0: "Conjunto 1",
                1: "Conjunto 2",
                2: "Conjunto 3",
                3: "Conjunto 4",
            },
        )
        .dropna(),
        y=column,
        range_y=[0, 10],
        markers=True,
        labels={
            "value": "Nota",
            "index": "Conjunto",
        },
    ),
    use_container_width=True,
)
