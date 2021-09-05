
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import pandas as pd
import numpy as np
import duckdb
import time
import plotly 
import plotly.express as px
from app import dashapp
from data import boxplots_pq
from app.utils import translate_dataframe

inicio = time.time()

dt = pd.read_parquet(boxplots_pq)

transl = {'ZScorePesoTallaT1':'Weight-Height Zscore', 'Sexo': 'Gender','PresentaDiscapacidad':'HasDisability', 'ZonaUbicacionBeneficiario':'BeneficiaryLocation', 'GrupoEtnico':'EthnicGroup'}

dt = translate_dataframe(dt, transl)

available_indicators = ['Gender','HasDisability', 'BeneficiaryLocation', 'EthnicGroup']
dt_sexo = dt.dropna(subset=['Gender'])[['Gender','Weight-Height Zscore']].sample(30000)
dt_disc = dt.dropna(subset=['HasDisability'])[['HasDisability','Weight-Height Zscore']].sample(30000)
dt_Ubicacion = dt.dropna(subset=['BeneficiaryLocation'])[['BeneficiaryLocation','Weight-Height Zscore']].sample(30000)
dt_Grupo = dt.dropna(subset=['EthnicGroup'])[['EthnicGroup','Weight-Height Zscore']].sample(150000)

fin = time.time()
print(f"Tiempo de ejecucion: {fin-inicio}")

layout = html.Div([
    #html.H4("Boxplot - Dataset Variables", className="display-4"),
	dbc.Card([
	   #html.Div([
		dbc.CardHeader([
			html.Div([
				dbc.FormGroup([dbc.Label(html.B("Variable:"), html_for="xaxis-column"),
				dcc.Dropdown(
					id='xaxis-column',
					options=[{'label': i, 'value': i} for i in available_indicators],
					value='Gender'
				)
				])
			],style={'width': '48%', 'display': 'inline-block'}),
		]),
		dbc.CardBody(
			dcc.Graph(id='box-plot', style={'width': '100%', 'display': 'inline-block'})
		)
	])
])

@dashapp.callback(
    Output('box-plot', 'figure'),
    [Input('xaxis-column', 'value'),])
def update_graph(x):
	if x == 'Gender':
		fig = px.box(data_frame=dt_sexo, x= x, y='Weight-Height Zscore', color = x)
	elif x == 'HasDisability':
		fig = px.box(data_frame=dt_disc, x= x, y='Weight-Height Zscore', color = x)
	elif x == 'BeneficiaryLocation':
		fig = px.box(data_frame=dt_Ubicacion, x= x, y='Weight-Height Zscore', color = x)
	elif x == 'EthnicGroup':
		fig = px.box(data_frame=dt_Grupo, x= x, y='Weight-Height Zscore', color = x)

	fig.update_layout(
		title=f'{x} - Zscore',
		yaxis=dict(
			autorange=True,
			gridwidth=0.5
			),
		showlegend=False
	)
	return fig

