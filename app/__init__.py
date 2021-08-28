import os
from flask import Flask

from dash import Dash
import dash_bootstrap_components as dbc

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.from_object('app.config.Config')

#inicialización de la APP DASH
dashapp = Dash( __name__,
                server=app,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                routes_pathname_prefix='/dash/'
                #url_base_pathname='/dash/'
)
dashapp.config.suppress_callback_exceptions = True 
dashapp.title = 'DS4A - Team 12'

from app import views
import dash_