#main.py

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import plotly.graph_objects as go

from utils import display_error_message
from stock_data import get_stock_data, extract_data, list_of_tickers
from news_data import get_stock_news, get_overall_sentiment, sentiment_color, NEWS_API_KEY
from figures import create_figure

import numpy as np

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
                dbc.Spinner(dcc.Graph(id='stock_plot'), color="primary", type="grow", fullscreen=True),
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


    @app.callback(
        Output('ticker_input', 'options'),
        Input('ticker_input', 'search_value'),
    )
    def update_ticker_options(search_value):
        if not search_value:
            return []

        matching_tickers = [ticker for ticker in list_of_tickers if search_value.upper() in ticker.upper()]
        return (
            [{'label': ticker, 'value': ticker} for ticker in matching_tickers]
            if matching_tickers
            else [{'label': 'No results found', 'value': '', 'disabled': True}]
        )

    @app.callback(
        Output('stock_plot', 'figure'),
        Output('news_articles', 'children'),
        Output('overall_sentiment', 'children'),
        Output('stock_plot_container', 'style'),
        Output('news_button', 'style'),
        [Input('ticker_input', 'value'),
        Input('timeframe_dropdown', 'value'),
        Input('display_options', 'value')]
    )
    def update_graph(ticker, timeframe, display_options):
        if ticker not in list_of_tickers or ticker == "":
            return go.Figure(layout=dict(xaxis=dict(visible=False), yaxis=dict(visible=False))), display_error_message(
                "Error fetching stock data. Please try again or enter a different stock ticker"), None, {"display": "none"}, {"display": "none"}

        ticker = ticker.upper()

        try:
            data = get_stock_data(ticker, timeframe)
            closing_prices, dates, opening_prices, high_prices, low_prices, volumes = extract_data(data)
        except Exception as e:
            return go.Figure(layout=dict(xaxis=dict(visible=False), yaxis=dict(visible=False))), display_error_message("Error fetching stock data. Please try again or enter a different stock ticker"), "N/A", {"display": "none"}, {"display": "none"}

        fig = create_figure(closing_prices, dates, opening_prices, high_prices, low_prices, volumes, ticker, display_options)
        
        if timeframe == "TIME_SERIES_DAILY_ADJUSTED":
            fig.update_layout(title=f"Daily Closing Prices and Trading Volume for {ticker}")
        elif timeframe == "TIME_SERIES_WEEKLY_ADJUSTED":
            fig.update_layout(title=f"Weekly Closing Prices and Trading Volume for {ticker}")
        elif timeframe == "TIME_SERIES_MONTHLY_ADJUSTED":
            fig.update_layout(title=f"Monthly Closing Prices and Trading Volume for {ticker}")

        try:
            stock_news = get_stock_news(ticker, NEWS_API_KEY)
        except Exception as e:
            return fig, display_error_message("Error fetching news articles. Please try again or enter a different stock ticker"), "N/A", {"display": "block"}, {"display": "block"}

        if len(stock_news) == 0:
            return fig, html.Div([
                html.H4("No news articles found for this stock.", className="news-title"),
            ]), html.H4("Overall Sentiment: N/A"), {"display": "block"}, {"display": "block"}


        news_div = html.Div([
    html.H4(id='news_section_heading', className="news-title"),
    dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        html.Div( # Add this Div
                            dbc.CardImg(src=article["image"], top=True, className="news-image"),
                            className="news-image-container" # Add the new class here
                        ),
                        dbc.CardBody(
                            [
                                dcc.Link(article["title"], href=article["url"], target="_blank", className="news-title card-title"),
                                html.P(f"Sentiment: {article['sentiment']} ({article['sentiment_score']:.2f})", className="news-sentiment", style={'color': sentiment_color(article['sentiment_score'])})
                            ],
                        ),
                    ],
                    className="news-article-card mb-4"
                ),
                lg=3, md=4, sm=12
            )
            for article in stock_news
        ],
        className="news-article-row"
    ),
])


        overall_sentiment = get_overall_sentiment(stock_news)
        overall_sentiment_text = f"Overall Sentiment: {overall_sentiment['sentiment']}"
        overall_sentiment_color = overall_sentiment['color']

        overall_sentiment_component = html.H4(overall_sentiment_text, style={"color": overall_sentiment_color}, className="overall-sentiment-text")

        return fig, news_div, overall_sentiment_component, {"display": "block"}, {"display": "block"}

    @app.callback(
    [Output("news_container", "style"),
    Output("news_button", "children")],  # Add this line to modify the button text
    Input("news_button", "n_clicks")
    )
    def toggle_news_section(n_clicks):
        if n_clicks is None or n_clicks % 2 == 0:
            return {"display": "none"}, "Show News" 
        else:
            return {"display": "block"}, "Hide News"
        
    @app.callback(
    Output('news_section_heading', 'children'),
    Input('ticker_input', 'value'),
)
    def update_news_section_heading(ticker):
        if not ticker:
            return html.H4("Enter the stock ticker in the input box, select the time frame, and get the stock charts, relevant news, and the sentiment from that news", className="news-title", style={'color': 'gray'})
        else:
            return html.H4(f"Latest, most relevant headlines about {ticker}", className="news-title")
        
    app.run_server(debug=True)

if __name__ == '__main__':
    main()

