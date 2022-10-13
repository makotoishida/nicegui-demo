from datetime import datetime, timedelta

import justpy as jp
import pandas_datareader as web
import plotly.graph_objects as go
from nicegui import ui
from nicegui.elements.element import Element
from plotly.subplots import make_subplots


async def disable_input(selector, value):
    s = "true" if value else "false"
    await ui.run_javascript(f"document.querySelector('{selector}').disabled={s};")


async def get_data():
    await disable_input("button.btn-get-data", True)

    df = web.DataReader(
        name="BTC-USD",
        data_source="yahoo",
        start=datetime.now() - timedelta(days=90),
        end=datetime.now(),
    )

    show_table(df)
    show_chart(df)

    await disable_input("button.btn-get-data", False)


def show_table(df):
    df = df.copy().sort_index(ascending=False).reset_index()
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    data = df.to_dict(orient="records")
    table.options.rowData = data
    table.update()


def show_chart(df):
    chart_container.clear()
    with chart_container:
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            shared_yaxes=False,
            vertical_spacing=0.06,
            subplot_titles=("BTC 90 days", "", ""),
            row_width=[0.3, 0.1, 0.6],
        )
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                showlegend=False,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Bar(x=df.index, y=df["Volume"], showlegend=False), row=3, col=1
        )
        fig.update(layout={"width": 700, "height": 500})
        # fig.update(layout_xaxis_rangeslider_visible=False)

        view = jp.PlotlyChart(
            chart=fig,
            classes="border m-1 p-0",
            style="width:100%",
        )
        Element(view)


#####################################################################
ui.markdown("# BTC価格取得テスト")
ui.label("Yahoo Financeから直近90日の価格データを取得します。")
button = ui.button("Get Data", on_click=get_data).classes("btn-get-data")

table = ui.table(
    {
        "columnDefs": [
            {"headerName": "Date", "field": "Date"},
            {"headerName": "High", "field": "High"},
            {"headerName": "Low", "field": "Low"},
            {"headerName": "Open", "field": "Open"},
            {"headerName": "Close", "field": "Close"},
            {"headerName": "Volume", "field": "Volume"},
            # {"headerName": "Adj Close", "field": "Adj Close"},
        ],
        "rowData": [],
    }
).classes("max-h-40")

chart_container = ui.row().classes("w-full")

ui.run()
