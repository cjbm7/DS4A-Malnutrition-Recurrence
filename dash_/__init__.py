import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import dashapp

import dash_.scatter, dash_.map, dash_.boxplots, dash_.report
from .region import update_g
from .report import report
CONTENT_STYLE = {
}

content = html.Div(id="page-content", style=CONTENT_STYLE)

dashapp.layout = html.Div([dcc.Location(id="url"), content])

@dashapp.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    pathnm = str(pathname)
    if pathname == "/dash":
        return scatter.layout
    elif pathname == "/dash/scatter":
        return scatter.layout
    elif pathname == "/dash/maps":
        return map.layout
    elif pathname == "/dash/boxplots":
        return boxplots.layout

    elif pathnm.startswith('/dash/col'):
        url_ = pathnm.split('/')
        dpto = url_[3]
        mpio= url_[4]
        return update_g(dpto, mpio)
    
    elif pathnm.startswith('/dash/nut'):
        url_ = pathnm.split('/')
        idBen = url_[3]
        return report(idBen)

    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )
