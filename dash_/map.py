import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import time
import json

from app import dashapp
from data import socio_eda_mpios, geojson_mpios

inicio = time.time()

soct = pd.read_parquet(socio_eda_mpios)

with open(geojson_mpios) as geo_json:
    mpios_json = json.load(geo_json)

available_indicators = ['ingr_prom','prom_gasto_pper','porc_gast']

layout = html.Div([
    dcc.Dropdown(
					id='map_type',
					options=[{'label': i, 'value': i} for i in available_indicators],
					value='porc_gast'
				),
    dcc.Graph(id='indicator-map')])#, style={'width': '100%', 'display': 'inline-block'})])
	
"""dbc.Card([
		dbc.CardHeader([
			html.Div([
				dcc.Dropdown(
					id='map_type',
					options=[{'label': i, 'value': i} for i in available_indicators],
					value='porc_gast'
				),
			],style={'width': '48%', 'display': 'inline-block'}),
		]),
		dbc.CardBody(
			dcc.Graph(id='indicator-map', style={'width': '100%', 'display': 'inline-block'})
		)
	])
])
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


def update(valor=None):
	if valor is None: valor = 'prom_gasto_pper'
	layout = html.Div([
		html.H4("Socioecomonics - Dataset Variables?", className="display-4"),
		dbc.Card([
			dbc.CardHeader([
				html.Div([
					dcc.Dropdown(
						id='map_type',
						name=valor,
						options=[{'label': i, 'value': i} for i in available_indicators],
						value=""
					),
				],style={'width': '48%', 'display': 'inline-block'}),
			]),
			dbc.CardBody(
				dcc.Graph(id='indicator-map', style={'width': '100%', 'display': 'inline-block'})
			)
		])
	])
	return layout

