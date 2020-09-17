import dash
import dash_core_components as dcc
import dash_html_components as html
import yfinance as yf
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go


def get_stock_price_fig(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(mode='lines', x=df['Date'], y=df['Close']))
    return fig


def get_dounts(df, label):
    non_main = 1 - df.values[0]
    labels = ["main", label]
    values = [non_main, df.values[0]]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.499)])
    return fig


app = dash.Dash()

app.layout = html.Div(
    [
        html.Div(
            [
                # Navigation
                html.P("Choose a ticker to start", className="start"),
                html.Div([
                    "Input stock code: ",
                    dcc.Input(id="dropdown_tickers", type="text"),
                    html.Button("Submit", id='submit'),
                ]),
                html.Div([
                    html.Button(
                        "Stock Price", className="stock-btn", id="stock"),
                    html.Button("Indicators",
                                className="indicators-btn",
                                id="indicators")
                ],
                         className="buttons")
            ],
            className="nav"),

        # content
        html.Div(
            [
                html.Div(
                    [  # header
                        html.P(id="ticker"),
                        html.Img(id="logo")
                    ],
                    className="header"),
                html.Div(id="description", className="decription_ticker"),
                html.Div([html.Div([], id="graphs-content")],
                         id="main-content")
            ],
            className="content"),
    ],
    className="container")


# callback for company info
@app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children")
], [Input("submit", "n_clicks")], [State("dropdown_tickers", "value")])
def update_data(v2, val):  # inpur parameter(s)
    if val == None:
        raise PreventUpdate
    ticker = yf.Ticker(val)
    inf = ticker.info
    df = pd.DataFrame().from_dict(inf, orient="index").T
    df[['logo_url', 'shortName', 'longBusinessSummary']]

    if val == None:
        return [""]
    else:
        return df['longBusinessSummary'].values[0], df['logo_url'].values[
            0], df['shortName'].values[0]


# callback for stocks graphs
@app.callback([Output("graphs-content", "children")],
              [Input("stock", "n_clicks"),
               Input("dropdown_tickers", "value")])
def stock_price(v1, v2):
    if v1 == None:
        raise PreventUpdate

    df = yf.download(v2)
    df.reset_index(inplace=True)

    fig = get_stock_price_fig(df)

    if v2 == None:
        return [""]
    else:
        return [dcc.Graph(figure=fig)]


# callback for indicators
@app.callback(
    [Output("main-content", "children"),
     Output("stock", "n_clicks")],
    [Input("indicators", "n_clicks"),
     Input("dropdown_tickers", "value")])
def indicators(v1, v2):
    if v1 == None:
        raise PreventUpdate

    ticker = yf.Ticker(v2)
    df_info = pd.DataFrame.from_dict(ticker.info, orient="index").T
    df_info = df_info[[
        "priceToBook", "profitMargins", "bookValue", "enterpriseToEbitda",
        "shortRatio", "beta", "payoutRatio", "trailingEps"
    ]]

    kpi_data = html.Div([
        html.Div([
            html.Div([
                html.H4("Price to Book"),
                html.P(df_info["priceToBook"]),
            ]),
            html.Div([
                html.H4("Enterprise to Ebitda"),
                html.P(df_info["enterpriseToEbitda"]),
            ]),
            html.Div([
                html.H4("Beta"),
                html.P(df_info["beta"]),
            ])
        ],
                 className="kpi"),
        html.Div([
            dcc.Graph(figure=get_dounts(df_info["profitMargins"], "Margins"))
        ]),
        html.Div(
            [dcc.Graph(figure=get_dounts(df_info["payoutRatio"], "Payout"))])
    ],
                        className="dounuts")
    return [html.Div([kpi_data],
                     id="graphs-contents")], None  #[dcc.Graph(figure=fig)]


app.run_server(debug=True)