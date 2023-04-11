from dash import dcc, html
import dash_bootstrap_components as dbc
import dash

import plotly.graph_objects as go

from utils import display_error_message
from stock_data import get_stock_data, extract_data, list_of_tickers
from news_data import get_stock_news, get_overall_sentiment, sentiment_color, NEWS_API_KEY
from figures import create_figure

def update_ticker_options(search_value):
    """
    Update the ticker dropdown options based on user input.

    :param search_value: User's search input
    :return: List of matching tickers
    """
    if not search_value:
        return []

    matching_tickers = [ticker for ticker in list_of_tickers if search_value.upper() in ticker.upper()]
    return (
        [{'label': ticker, 'value': ticker} for ticker in matching_tickers]
        if matching_tickers
        else [{'label': 'No results found', 'value': '', 'disabled': True}]
        )

def update_graph(ticker, timeframe, display_options):
    """
    Update the graph, news articles, and overall sentiment based on user inputs.

    :param ticker: Selected stock ticker
    :param timeframe: Selected timeframe (daily, weekly, or monthly)
    :param display_options: Selected display options (closing price, trading volume, moving average)
    :return: Updated figure, news articles, overall sentiment, and display styles
    """
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
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            html.Div( 
                                dbc.CardImg(src=article["image"], top=True, className="news-image"),
                                className="news-image-container"
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

def update_news_section_heading_and_toggle(ticker, n_clicks):
    """
    Update the news section heading and toggle news display based on user inputs.

    :param ticker: Selected stock ticker
    :param n_clicks: Number of times the news button has been clicked
    :return: Updated news section heading, news container style, and news button text
    """
    ctx = dash.callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_input == 'ticker_input':
        if not ticker:
            return html.H4(
                "Enter the stock ticker in the input box, select the time frame, and get the stock charts, relevant news, and the sentiment from that news",
                className="news-title", style={'color': 'gray'}), dash.no_update, "Show News"
        else:
            return [], dash.no_update, f"{ticker} News Insights"

    elif triggered_input == 'news_button':
        if n_clicks is None or n_clicks % 2 == 0:
            return [], {"display": "none"}, f"{ticker} News Insights" 
        else:
            return [], {"display": "block"}, "Hide News" 
