import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from plotly.subplots import make_subplots
from scipy import stats


def rankmetric(data: float, ref: float, rank: pd.Series) -> None:
    col_rank, col_data, col_ref = st.columns(3)
    with col_rank:
        pos = rank.tolist().index(data)
        pos_delta = pos / (len(rank) - 1)
        st.metric(
            "Posição no ranking",
            f"{len(rank) - pos}/{len(rank)}",
            f"Melhor que {pos_delta:.2%}",
        )
    with col_data:
        data_delta = (data / ref) - 1
        st.metric("Sua média", f"{data:.2f}", f"{data_delta:+.2%}")
    with col_ref:
        st.metric("Média do ano", f"{ref:.2f}")


def barplot(
    data: pd.Series,
    xtitle: str | None = None,
    ytitle: str | None = None,
    pct_change: bool = False,
) -> None:
    yaxis = 0
    if data.name:
        yaxis = data.name

    fig = px.bar(data, y=yaxis, range_y=[0, 10])

    if pct_change:
        change = [(data.iloc[i] / data.iloc[i - 1]) - 1 for i in range(1, len(data))]
        fig.update_traces(
            text=[""] + [f"{pct:+.2%}" if not pd.isnull(pct) else "" for pct in change],
            textposition="outside",
        )

    fig.update_traces(hovertemplate=ytitle + ": %{y:.2f}")
    fig.update_layout(xaxis_title=xtitle, yaxis_title=ytitle),

    st.plotly_chart(fig, use_container_width=True)


def lineplot(
    data: pd.Series,
    xtitle: str | None = None,
    ytitle: str | None = None,
    pct_change: bool = False,
) -> None:
    yaxis = 0
    if data.name:
        yaxis = data.name

    fig = px.line(data, y=yaxis, range_y=[0, 10])

    if pct_change:
        change = [(data.iloc[i] / data.iloc[i - 1]) - 1 for i in range(1, len(data))]
        fig.update_traces(
            text=[""] + [f"{pct:+.2%}" if not pd.isnull(pct) else "" for pct in change],
            textposition="top center",
            mode="lines+markers+text",
        )

    fig.update_traces(hovertemplate=ytitle + ": %{y:.2f}")
    fig.update_layout(xaxis_title=xtitle, yaxis_title=ytitle),

    st.plotly_chart(fig, use_container_width=True)


def distplot(
    data: pd.Series,
    bins: int | None = None,
    xtitle: str | None = None,
    ytitle: str | None = None,
) -> None:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, specs=[[{"secondary_y": True}], [{}]]
    )

    hist_xaxis = 0
    if data.name:
        hist_xaxis = data.name

    hist = px.histogram(data, x=hist_xaxis, nbins=bins, marginal="rug", text_auto=True)
    hist.update_traces(hovertemplate=xtitle + ": %{y}<br>Entre: %{x}", row=1, col=1)
    hist.update_traces(hovertemplate=ytitle + ": %{x:.2f}", row=2, col=1)
    fig.add_trace(hist.data[0], row=1, col=1)
    fig.add_trace(hist.data[1], row=2, col=1)

    kde_values = np.linspace(data.min(), data.max(), 1000)
    pdf = stats.norm.pdf(kde_values, data.mean(), data.std())
    fig.add_scatter(
        x=kde_values,
        y=pdf,
        name="Densidade",
        line={"color": "#9467bd"},
        secondary_y=True,
    )
    fig.update_layout(xaxis_title=ytitle, yaxis_title=xtitle)

    tab_barplot, tab_distplot = st.tabs(["Barras", "Distribuição"])
    with tab_barplot:
        barplot(data, xtitle, ytitle)
    with tab_distplot:
        st.plotly_chart(fig, use_container_width=True)
