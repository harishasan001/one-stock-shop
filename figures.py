# figures.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def create_figure(closing_prices, dates, opening_prices, high_prices, low_prices, volumes, symbol, plot_options, window=10):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)

    if "closing_price" in plot_options:
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=closing_prices,
                mode="lines",
                name="Closing Prices",
                hovertemplate=
                    "<b>%{x}</b><br>" +
                    "Closing Price: %{y:.2f}<br>" +
                    "Opening Price: %{customdata[0]:.2f}<br>" +
                    "High Price: %{customdata[1]:.2f}<br>" +
                    "Low Price: %{customdata[2]:.2f}<br>" +
                    "Volume: %{customdata[3]:,}",
                customdata=list(zip(opening_prices, high_prices, low_prices, volumes)),
                line=dict(color="royalblue", width=2),
            ),
            row=1, col=1
        )

    if "moving_average" in plot_options:
        moving_average = np.convolve(closing_prices, np.ones(window), 'valid') / window
        fig.add_trace(
            go.Scatter(
                x=dates[window-1:],
                y=moving_average,
                mode="lines",
                name=f"{window}-day Moving Average",
                line=dict(color="orange", width=2),
            ),
            row=1, col=1
        )

    if "trading_volume" in plot_options:
        fig.add_trace(
            go.Bar(
                x=dates,
                y=volumes,
                name="Trading Volume",
                marker={
                    "color": ["red" if closing_prices[i] < closing_prices[i - 1] else "green" for i in range(1, len(closing_prices))]
                },
            ),
            row=2, col=1
        )

    fig.update_layout(
        title=f"Daily Closing Prices and Trading Volume for {symbol}",
        xaxis_title="Date",
        xaxis_tickangle=-45,
        hovermode="x",
        legend=dict(x=0, y=1),
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            ),
            rangeslider=dict(visible=True),
            type="date",
        )
    )

    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig

