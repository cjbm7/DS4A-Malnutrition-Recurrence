
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

from app import dashapp

inicio = time.time()
dt = pd.read_parquet('data/TomasDPImelted.parquet') #, engine='fastparquet')
fin = time.time()
print(f"Tiempo de ejecucion: {fin-inicio}")
dc = dt.sample(3000)
df = dc.select_dtypes(include= np.number)
available_indicators = df.columns

layout = html.Div([
    html.H4("Scatterplots - Dataset Variables", className="display-4"),
	dbc.Card([
	   #html.Div([
		dbc.CardHeader([
			html.Div([
				dcc.Dropdown(
					id='xaxis-column',
					options=[{'label': i, 'value': i} for i in available_indicators],
					value='Peso'
				),
				dbc.RadioItems(
					className = "form-check-inline pr-10",
					id='xaxis-type',
					options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
					value='Linear',
					labelStyle={'display': 'inline-block'}
				)
			],style={'width': '48%', 'display': 'inline-block'}),

			html.Div([
				dcc.Dropdown(
					id='yaxis-column',
					options=[{'label': i, 'value': i} for i in available_indicators],
					value='Talla'
				),
				dbc.RadioItems(
					className = "form-check-inline",
					id='yaxis-type',
					options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
					value='Linear',
					labelStyle={'display': 'inline-block, padding-right: 10px;'}
				)
			],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
		]),
		dbc.CardBody(
			dcc.Graph(id='indicator-graphic', style={'width': '100%', 'display': 'inline-block'})
		)
	])
])


@dashapp.callback(
    Output('indicator-graphic', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value'),
     Input('xaxis-type', 'value'),
     Input('yaxis-type', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type):
    dff = df

    return {
        'data': [dict(
            x = dff[xaxis_column_name],
			y = dff[yaxis_column_name],
			text= dff['IdBeneficiario'],
            mode='markers',
			marker_color=dff['Talla'],
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': dict(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }
