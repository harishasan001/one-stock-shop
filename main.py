#main.py

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from callbacks import update_ticker_options, update_graph, update_news_section_heading_and_toggle

external_stylesheets = [dbc.themes.BOOTSTRAP, "/styles.css"]


external_stylesheets = [dbc.themes.BOOTSTRAP, "/styles.css"]

def main():
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Label("Stock Ticker:", className="input-label"),
            dcc.Dropdown(
                id='ticker_input',
                placeholder='Enter the stock ticker...',
                value='',
                searchable=True,
                search_value='',
                multi=False,
            ),
        ]),
        dbc.Col([
            html.Label("Time Frame:", className="input-label"),
            dcc.Dropdown(
                id='timeframe_dropdown',
                options=[
                    {'label': 'Daily', 'value': 'TIME_SERIES_DAILY_ADJUSTED'},
                    {'label': 'Weekly', 'value': 'TIME_SERIES_WEEKLY_ADJUSTED'},
                    {'label': 'Monthly', 'value': 'TIME_SERIES_MONTHLY_ADJUSTED'}
                ],
                value='TIME_SERIES_DAILY_ADJUSTED',
                clearable=False,
                style={'width': '200px'}
            ),
        ]),
        dbc.Col([
            html.Label("Display Options:", className="input-label"),
            dcc.Checklist(
                id='display_options',
                options=[
                    {'label': '  Closing Price', 'value': 'closing_price'},
                    {'label': '  Trading Volume', 'value': 'trading_volume'},
                    {'label': '  Moving Average', 'value': 'moving_average'}
                ],
                value=['closing_price', 'trading_volume'],
                inline=True,
                className="display-options",
            ),
        ]),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col([
            html.Div(
                dbc.Spinner(dcc.Graph(id='stock_plot'), color="primary", type="grow"),
                className="dashboard-spinner",
                id="stock_plot_container",
                style={"display": "none"},
            ),
        ], width=12),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col([
            html.Div(id='news_section_heading', children=[
                html.H4("Enter the stock ticker in the input box, select the time frame, and get the stock charts, relevant news, and the sentiment from that news", className="news-title", style={'color': 'gray'}),
            ]),
            dbc.Button("Show News", id="news_button", className="mb-2", color="primary", outline=True),
            html.Div(
                dbc.Spinner(html.Div(id='news_articles', children=[]), color="primary", type="grow", fullscreen=True),
                className="dashboard-spinner",
                id="news_container",  
                style={"display": "none"}, 
            ),
        ], width=12),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col([
            html.Div(id='overall_sentiment', children=[html.H4(id='overall_sentiment_text', children="Overall Sentiment: N/A", className="overall-sentiment-text")]),
        ], width=12),
    ]),
    dcc.Interval(
        id='interval-component',
        interval=500,
        n_intervals=0
    )
], fluid=True)


    app.callback(
        Output('ticker_input', 'options'),
        Input('ticker_input', 'search_value'),
    )(update_ticker_options)

    app.callback(
        Output('stock_plot', 'figure'),
        Output('news_articles', 'children'),
        Output('overall_sentiment', 'children'),
        Output('stock_plot_container', 'style'),
        Output('news_button', 'style'),
        [Input('ticker_input', 'value'),
        Input('timeframe_dropdown', 'value'),
        Input('display_options', 'value')]
    )(update_graph)

    app.callback(
        [Output('news_section_heading', 'children'),
        Output("news_container", "style"),
        Output("news_button", "children")],
        [Input('ticker_input', 'value'),
        Input('news_button', 'n_clicks')]
    )(update_news_section_heading_and_toggle)

    app.run_server(debug=True)

if __name__ == '__main__':
    main()

