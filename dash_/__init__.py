import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, dashapp

import dash_.data, dash_.scatter, dash_.map, dash_.Box_Plot
from .scatter import update_graph
from .map import update, update_g
# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {

}

content = html.Div(id="page-content", style=CONTENT_STYLE)

dashapp.layout = html.Div([dcc.Location(id="url"), content])


@dashapp.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    pathnm = str(pathname)
    if pathname == "/dash":
        #return homelayout
        return scatter.layout
    elif pathname == "/dash/scatter":
        return scatter.layout
    elif pathname == "/dash/maps":
        return map.layout
    elif pathname == "/dash/boxplots":
        return Box_Plot.layout

    elif pathnm.startswith('/dash/col'):
        url_ = pathnm.split('/')
        print(f'**************{url_}************')
        dpto = url_[3]
        mpio= url_[4]
        return update_g(dpto, mpio)
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )
