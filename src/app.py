import plotly.express as px
import streamlit as st
import pandas as pd
from st_pages import show_pages_from_config, hide_pages
from streamlit_extras.switch_page_button import switch_page

show_pages_from_config()
hide_pages(["Login"])

if "user" not in st.session_state:
    switch_page("login")

user_data = st.session_state["user"]["data"]

user_dataframe: pd.DataFrame = user_data["dataframe"].rename(
    {0: "Conjunto 1", 1: "Conjunto 2", 2: "Conjunto 3", 3: "Conjunto 4"}
)
user_dataframe.index.name = "Conjunto"
row_mean: pd.Series = (
    user_data["row_mean"]
    .rename("Média")
    .rename({0: "Conjunto 1", 1: "Conjunto 2", 2: "Conjunto 3", 3: "Conjunto 4"})
)
row_mean.index.name = "Conjunto"
column_mean: pd.Series = user_data["column_mean"].rename("Média")
user_mean: float = user_data["mean"]

st.title("Análise Pessoal")

st.metric("Média:", round(user_mean, 2))

tab_dataframe, tab_row, tab_column = st.tabs(["Notas", "Conjuntos", "Matérias"])

tab_dataframe.dataframe(user_dataframe.transpose(), use_container_width=True)

tab_row.dataframe(row_mean.to_frame().transpose(), use_container_width=True)
tab_row.plotly_chart(
    px.line(row_mean, y="Média", range_y=[0, 10], markers=True),
    use_container_width=True,
)

tab_column.dataframe(column_mean.sort_values(ascending=False), use_container_width=True)
tab_column.plotly_chart(
    px.bar(column_mean.sort_values(), y="Média", range_y=[0, 10]),
    use_container_width=True,
)

column = st.selectbox("Código", user_dataframe.columns)
st.plotly_chart(
    px.line(user_dataframe[column].dropna(), y=column, range_y=[0, 10], markers=True),
    use_container_width=True,
)
