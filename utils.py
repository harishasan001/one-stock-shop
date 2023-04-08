from dash import html

def display_error_message(message: str) -> html.Div:
    return html.Div(className="error-message", children=[html.H4(message)])
