import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import time
import json

from app.utils import translate_dataframe
from app import dashapp
from data import socio_eda_mpios, geojson_mpios

inicio = time.time()

soct = pd.read_parquet(socio_eda_mpios)

with open(geojson_mpios) as geo_json:
    mpios_json = json.load(geo_json)

transl = {'ingr_prom':'Household inc(avg).','prom_gasto_pper':'spending_food_PPER','porc_gast':'spending_food'}

soct = translate_dataframe(soct, transl)

available_indicators = ['Household inc(avg).','spending_food_PPER','spending_food']

layout = html.Div([

	dbc.Card([
		dbc.CardHeader([
			html.Div([
				dbc.FormGroup([dbc.Label(html.B("Variable:"), html_for="xaxis-column"),
				dcc.Dropdown(
					id='map_type',
					options=[{'label': i, 'value': i} for i in available_indicators],
					value='spending_food'
				),
				]),
				
			],style={'width': '48%', 'display': 'inline-block'}),
		]),
		dbc.CardBody(
			dcc.Graph(id='indicator-map', style={'width': '100%', 'display': 'inline-block'})
		)
	])
])
"""
    dcc.Dropdown(
					id='map_type',
					options=[{'label': i, 'value': i} for i in available_indicators],
					value='porc_gast'
				),
    dcc.Graph(id='indicator-map')])#, style={'width': '100%', 'display': 'inline-block'})])
	
"""

@dashapp.callback(
    Output('indicator-map', 'figure'),
    [Input('map_type', 'value')])
def update_graph(map_type=False):
	if not map_type:
		map_type = 'porc_gast'
	
	fig = px.choropleth(
        soct,
        geojson=mpios_json,
        featureidkey="properties.MPIO_CCNCT",
        locations='cod_mpio',
        projection='mercator',
        color=map_type,
        color_continuous_scale=px.colors.sequential.OrRd,
        hover_data=['nom_mpio','nom_dpto', map_type]
        )

	fig.update_geos(fitbounds="locations", visible=False)
	fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
	
	return fig


def alt_map(valor=None):
	if valor is None: valor = 'spending_food_PPER'
	layout = html.Div([
		dbc.Card([
			dbc.CardHeader([
				html.Div([
					dbc.FormGroup([dbc.Label(html.B("Variable:"), html_for="xaxis-column"),
					dcc.Dropdown(
						id='map_type',
						options=[{'label': i, 'value': i} for i in available_indicators],
						value=valor
					),
					]),
					
				],style={'width': '48%', 'display': 'inline-block'}),
			]),
			dbc.CardBody(
				dcc.Graph(id='indicator-map', style={'width': '100%', 'display': 'inline-block'})
			)
		])
	])
	return layout

