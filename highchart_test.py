from datetime import datetime, timedelta

import pandas_datareader as web
from nicegui import ui

DAYS = 600


async def disable_input(selector, value):
    s = "true" if value else "false"
    await ui.run_javascript(f"document.querySelector('{selector}').disabled={s};")


async def get_data():
    await disable_input("button.btn-get-data", True)

    df = web.DataReader(
        name="BTC-USD",
        data_source="yahoo",
        start=datetime.now() - timedelta(days=DAYS),
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


def convert_date2(date_string):
    date = datetime.strptime(date_string, '%Y-%m-%d')
    epoch = datetime(1970, 1, 1)
    return (date - epoch).total_seconds() * 1000


def show_chart(df):
    grouping_units = [['week', [1]], ['month', [1, 2, 3, 4, 6]]]

    df["Date"] = df.index.astype(str)
    x = list(df["Date"].map(convert_date2))

    ohlc_data = list(zip(x, df['Open'], df['High'], df['Low'], df['Close']))
    volume_data = list(zip(x, df['Volume']))

    sma1_data = list(zip(x[50:], df["Close"].rolling(window=50).mean().dropna()))
    sma2_data = list(zip(x[100:], df["Close"].rolling(window=100).mean().dropna()))

    chart_dict = {
        'title': {"text": "BTC Price Chart"},

        "rangeSelector": {
            "buttons": [
                {"type": "month", "count": 1, "text": "1M"},
                {"type": "month", "count": 2, "text": "2M"},
                {"type": "month", "count": 3, "text": "3M"},
                {"type": "month", "count": 6, "text": "6M"},
                {"type": "year", "count": 1, "text": "1Y"},
                {"type": "all", "count": 1, "text": "All"},
            ],
            "selected": 4,
            "inputEnabled": False,
        },

        'yAxis': [
            {'labels': {'align': 'right', 'x': -3}, 'title': {'text': 'Price'}, 'height': '65%',
                'lineWidth': 2, 'resize': {'enabled': True}},
            {'labels': {'align': 'right', 'x': -3}, 'title': {'text': 'Volume'}, 'top': '70%',
                'height': '30%', 'offset': 0, 'lineWidth': 2},
        ],
        'tooltip': {'split': True},
        'plotOptions': {
            'series': {
                'dataGrouping': {'units': grouping_units},  # General options for all series
                'tooltip': {'valueDecimals': 2},
            },
        },
        'series': [
            {
                'name': 'Price',
                'type': 'candlestick',
                'data': ohlc_data
            },
            {
                'name': 'Volume',
                'type': 'column',
                'tooltip': {'valueDecimals': 0},
                'yAxis': 1,
                'data': volume_data
            },
            {
                'name': 'SMA1',
                'type': 'line',
                'data': sma1_data
            },
            {
                'name': 'SMA2',
                'type': 'line',
                'data': sma2_data
            }
        ]
    }

    chart_container.clear()
    with chart_container:
        chart = ui.chart(chart_dict).classes('w-full').style('height: 500px')
        chart.view.stock = True  # type: ignore


#####################################################################
ui.markdown("# BTC価格取得テスト")
ui.label(f"Yahoo Financeから直近{DAYS}日の価格データを取得します。")
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
