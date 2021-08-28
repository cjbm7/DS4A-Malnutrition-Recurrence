import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import plotly.express as px
import pandas as pd
import numpy as np
import duckdb
import time
import json

from app import dashapp

inicio = time.time()

con = duckdb.connect()
con.execute("PRAGMA threads=2")
con.execute("PRAGMA enable_object_cache")
soct = con.execute("SELECT cod_mpio, COUNT(cod_mpio) as cant_mpio, AVG(ingresos_promP_imp) AS ingr_prom,	AvG(gasto_alim_ppers_imp) AS prom_gasto_pper, AVG(porc_gasto_alim) AS porc_gast FROM 'data/Sociodemo_pre.parquet' GROUP BY cod_mpio").df()
soct.cod_mpio = soct.cod_mpio.astype('str')
soct.cod_mpio = soct.cod_mpio.str.zfill(5)

fin = time.time()

print(f"Tiempo de ejecucion: {fin-inicio}")

with open('data/co_2018_MGN_MPIO_POLITICO.geojson') as geo_json:
    mpios_json = json.load(geo_json)

lst_mpios = []
for mpio in mpios_json['features']:
  lst_mpios.append(mpio['properties']['MPIO_CCNCT'])

x = len(soct.columns)
xa = np.full((x), 0)
not_disp = []
for i in lst_mpios:
  if i not in soct['cod_mpio'].unique():
    xa[0] = i
    a_series = pd.Series(xa.copy(), index = soct.columns)
    soct = soct.append(a_series, ignore_index=True)

def nom(cod_mpio):
	for mpio in mpios_json['features']:
		if cod_mpio == mpio['properties']['MPIO_CCNCT']:
			return mpio['properties']['MPIO_CNMBR']
	  

soct['nom_mpio'] = soct['cod_mpio'].apply(lambda x: nom(x))

	
available_indicators = soct.columns

layout = html.Div([
    html.H4("Socioecomonics - Dataset Variables?", className="display-4"),
	dbc.Card([
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
        hover_data=['cod_mpio', 'nom_mpio', map_type]
        )

	fig.update_geos(fitbounds="locations", visible=False)
	fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
	
	return fig
