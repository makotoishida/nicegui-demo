from datetime import datetime, timedelta

import pandas_datareader as web
from matplotlib import pyplot as plt
from nicegui import ui


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
        with ui.plot(figsize=(6.5, 5.8)):
            plt.plot(df["Close"])
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.xticks(rotation=18)


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

chart_container = ui.row()

ui.run()
