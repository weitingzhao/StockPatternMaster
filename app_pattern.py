from dash import dcc, html, Dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import re
import src.controller.app as fn

app = Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.title = "Stock Patterns Master"
server = app.server

##### Header #####

def highlight_text(text, highlight):
    highlighted = re.sub(f"({highlight})", r'<span style="background-color: yellow">\1</span>', text, flags=re.IGNORECASE)
    return html.Span(dangerously_allow_html=True, children=highlighted)

header_div = html.Div(
    [html.Div([html.H3("📈")], className="one-third column"),
     html.Div([html.Div([html.H3("Stock Patterns", style={"margin-bottom": "0px"}),
                         html.H5("Find historical patterns and use for forecasting",
                                 style={"margin-top": "0px"})])],
              className="one-half column",
              id="title"),
     html.Div([html.A(html.Button("Author"), href="")],
              className="one-third column",
              id="learn-more-button")
     ],
    id="header", className="row flex-display", style={"margin-bottom": "25px"})

##### Explanation #####

explanation_div = html.Div([dcc.Markdown("""Select a stock symbol, lazy load""")])

##### Settings container #####
default_symbol = "AAPL"

symbol_dropdown_id = "id-symbol-dropdown"
symbol_dropdown = dcc.Dropdown(
    id=symbol_dropdown_id,
    options=[], # Start with empty options
    multi=False,
    value=default_symbol,
    className="dcc_control")

settings_div = html.Div(
    [
        html.P("Symbol (anchor)", className="control_label"),
        symbol_dropdown,
    ],
    className="pretty_container three columns",
    id="id-settings-div")

##### Stats & Graph #####

##### Matched Stocks List #####


##### Layout #####

app.layout = html.Div([
    header_div,
    explanation_div,
    html.Div([
        settings_div,
    ], className="row flex-display"),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"})


##### Callbacks #####
@app.callback(
    Output(symbol_dropdown_id, "options")
    ,[Input(symbol_dropdown_id, "search_value")])
def update_symbol_options(search_value):
    if not search_value:
        raise PreventUpdate
    # Fetch symbols based on the search value
    search_value = search_value.upper()
    available_symbols = fn.get_match_symbols(search_value)
    filtered_symbols = [symbol for symbol in available_symbols if search_value in symbol]
    result = [{"label": symbol, "value": symbol} for symbol in filtered_symbols]

    # Highlight matched characters
    highlighted_options = []
    for symbol in filtered_symbols:
        highlighted_label = symbol.replace(search_value, f"**{search_value}**")
        highlighted_options.append({"label": highlighted_label, "value": symbol})

    print(f"result4=>{highlighted_options}")
    return highlighted_options



if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
