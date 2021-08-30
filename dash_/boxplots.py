
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

inicio = time.time()

dt = pd.read_parquet(boxplots_pq)
available_indicators = ['Sexo','PresentaDiscapacidad', 'ZonaUbicacionBeneficiario', 'GrupoEtnico']
dt_sexo = dt.dropna(subset=['Sexo'])[['Sexo','ZScorePesoTallaT1']].sample(30000)
dt_disc = dt.dropna(subset=['PresentaDiscapacidad'])[['PresentaDiscapacidad','ZScorePesoTallaT1']].sample(30000)
dt_Ubicacion = dt.dropna(subset=['ZonaUbicacionBeneficiario'])[['ZonaUbicacionBeneficiario','ZScorePesoTallaT1']].sample(30000)
dt_Grupo = dt.dropna(subset=['GrupoEtnico'])[['GrupoEtnico','ZScorePesoTallaT1']].sample(150000)

fin = time.time()
print(f"Tiempo de ejecucion: {fin-inicio}")

layout = html.Div([
    html.H4("Boxplot - Dataset Variables", className="display-4"),
	dbc.Card([
	   #html.Div([
		dbc.CardHeader([
			html.Div([
				dcc.Dropdown(
					id='xaxis-column',
					options=[{'label': i, 'value': i} for i in available_indicators],
					value='Sexo'
				)
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
	if x == 'Sexo':
		fig = px.box(data_frame=dt_sexo, x= x, y='ZScorePesoTallaT1')
	elif x == 'PresentaDiscapacidad':
		fig = px.box(data_frame=dt_disc, x= x, y='ZScorePesoTallaT1')
	elif x == 'ZonaUbicacionBeneficiario':
		fig = px.box(data_frame=dt_Ubicacion, x= x, y='ZScorePesoTallaT1')
	elif x == 'GrupoEtnico':
		fig = px.box(data_frame=dt_Grupo, x= x, y='ZScorePesoTallaT1')

	fig.update_layout(
		title=f'G{x} - Zscore',
		yaxis=dict(
			autorange=True,
			gridwidth=0.5
			),
		showlegend=False
	)
	return fig

