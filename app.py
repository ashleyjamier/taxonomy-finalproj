
import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import requests
from urllib.parse import urlencode, parse_qs

BACKEND_URL = "http://127.0.0.1:8000"

# Custom Pink Theme
PINK_STYLE = {
    "backgroundColor": "#ffe4ec",   # Light Pink Background
    "color": "#a61d62",             # Dark Pink Text
    "borderRadius": "10px",
    "padding": "20px",
    "fontFamily": "Arial, sans-serif",
    "fontWeight": "500",            # Slightly bolder text
}

BUTTON_STYLE = {
    "backgroundColor": "#d63384",   # Darker Pink Button
    "color": "white",
    "border": "none",
    "borderRadius": "8px",
    "padding": "8px 16px",
    "margin": "5px",
    "boxShadow": "2px 2px 5px rgba(0,0,0,0.1)",
    "fontWeight": "bold",
    "textAlign": "center",
    "cursor": "pointer"
}

BUTTON_OUTLINE_STYLE = {
    "backgroundColor": "transparent",
    "color": "#d63384",
    "border": "2px solid #d63384",
    "borderRadius": "8px",
    "padding": "8px 16px",
    "margin": "5px",
    "boxShadow": "2px 2px 5px rgba(0,0,0,0.1)",
    "fontWeight": "bold",
    "textAlign": "center",
    "cursor": "pointer"
}

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Taxonomy Explorer"

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
], style={"backgroundColor": "#fff0f5", "minHeight": "100vh"})  # Overall pinkish background


def landing_layout():
    return dbc.Container([
        html.H1("Taxonomy Search", className="text-center my-4 text-pink"),
        dbc.Row([
            dbc.Col(dcc.Input(id="keyword", type="text", placeholder="Enter keyword", className="form-control"), width=6),
            dbc.Col(dcc.Dropdown(
                id="mode",
                options=[{"label": m.title(), "value": m} for m in ["contains", "starts with", "ends with"]],
                value="contains",
                className="form-control"
            ), width=3),
            dbc.Col(html.Button("Search", id="search-btn", className="btn btn-pink w-100", style=BUTTON_STYLE), width=3)
        ], className="mb-4"),
        html.Div(id="redirect")
    ], style=PINK_STYLE)


def results_layout(params):
    keyword = params.get("keyword", [""])[0]
    mode = params.get("mode", ["contains"])[0]
    page = int(params.get("page", [1])[0])

    try:
        r = requests.get(f"{BACKEND_URL}/search", params={"keyword": keyword, "mode": mode, "page": page, "items_per_page": 10})
        r.raise_for_status()
        results = r.json()
    except Exception:
        return html.Div("Error fetching search results.", style={"color": "red"})

    table_rows = [
        html.Tr([
            html.Td(html.A(str(row["taxon_id"]), href=f"/taxon/{row['taxon_id']}?{urlencode(params, doseq=True)}")),
            html.Td(row["name"]),
            html.Td(row["name_class"])
        ]) for row in results
    ]

    table = dbc.Table([
        html.Thead(html.Tr([html.Th("Taxon ID"), html.Th("Name"), html.Th("Class")])),
        html.Tbody(table_rows)
    ], bordered=True, hover=True, striped=True)

    return dbc.Container([
        html.H2("Search Results", className="my-4 text-pink"),
        table,
        dbc.Row([
            dbc.Col(html.A("Previous", href=f"/results?{urlencode({**params, 'page': page-1})}", className="btn btn-outline-pink"), width="auto"),
            dbc.Col(html.Span(f"Page {page}", className="mx-2 text-pink"), width="auto"),
            dbc.Col(html.A("Next", href=f"/results?{urlencode({**params, 'page': page+1})}", className="btn btn-outline-pink"), width="auto")
        ], className="my-3"),
        html.A("Back to Search", href="/", className="btn btn-link text-pink")
    ], style=PINK_STYLE)

def taxon_detail_layout(taxon_id, params):
    try:
        r = requests.get(f"{BACKEND_URL}/taxa", params={"tax_id": taxon_id})
        r.raise_for_status()
        data = r.json()
    except Exception:
        return html.Div("Error fetching taxon details.", style={"color": "red"})

    parent_id = data.get("parent_id")
    rank = data.get("rank", "")
    children = data.get("children", [])
    name_rows = [html.Tr([html.Td(n["name"]), html.Td(n["name_class"])]) for n in data.get("names", [])]
    child_rows = [html.Tr([
        html.Td(html.A(str(cid), href=f"/taxon/{cid}?{urlencode(params, doseq=True)}"))
    ]) for cid in children]

    return dbc.Container([
        html.H2(f"Taxon {taxon_id}", className="my-4 text-pink"),
        html.P(f"Rank: {rank}", className="text-pink"),
        html.H4("Parent", className="text-pink"),
        html.P(html.A(f"Taxon {parent_id}", href=f"/taxon/{parent_id}?{urlencode(params, doseq=True)}") if parent_id else "None"),
        html.H4("Children", className="text-pink"),
        dbc.Table([html.Thead(html.Tr([html.Th("Child Taxon ID")]))] + child_rows, bordered=True) if child_rows else html.P("No children."),
        html.H4("Names", className="text-pink"),
        dbc.Table([html.Thead(html.Tr([html.Th("Name"), html.Th("Class")]))] + name_rows, bordered=True),
        html.Br(),
        html.A("Back to Search Results", href=f"/results?{urlencode(params, doseq=True)}", className="btn btn-link text-pink")
    ], style=PINK_STYLE)



@app.callback(
    Output("redirect", "children"),
    Input("search-btn", "n_clicks"),
    State("keyword", "value"),
    State("mode", "value")
)
def update_redirect(n_clicks, keyword, mode):
    if n_clicks and keyword:
        params = urlencode({"keyword": keyword, "mode": mode, "page": 1})
        return dcc.Location(href=f"/results?{params}", id="dummy")
    return ""


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input("url", "search")
)
def render_page(pathname, search):
    params = parse_qs(search[1:]) if search else {}

    if pathname.startswith("/results"):
        return results_layout(params)

    elif pathname.startswith("/taxon/"):
        taxon_id = pathname.split("/")[-1]
        return taxon_detail_layout(taxon_id, params)

    return landing_layout()


if __name__ == "__main__":
    app.run(debug=True, port = 8051)
