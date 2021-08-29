
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
import plotly.express as px

from app import dashapp

inicio = time.time()
dt = pd.read_parquet('data/tomas_3000_act.parquet') #, engine='fastparquet')
fin = time.time()
print(f"Tiempo de ejecucion tomas3000: {fin-inicio}")
clusters = dt.columns

available_indicators = [ 'EdadMeses',
						 'MedicionPerimetroBraquial',
						 'Peso',
						 'Talla',
						 'ZScoreTallaEdad',
						 'ZScorePesoEdad',
						 'ZScorePesoTalla',
						 'ZScoreIMC'
						 'Sexo',
						'Estrato',
						'cod_mpio',
						'cod_dpto',
						'ingresos_promP_imp']

layout = html.Div([
    #html.H4("Scatterplots - Dataset Variables", className="display-4"),
	dbc.Card([
	   #html.Div([

		
		dbc.CardHeader([
				dbc.Row(
						[
							dbc.Col(
								[
									dbc.FormGroup(
												[
													dbc.Label(html.B("X - Axis"), html_for="xaxis-column"),

													dcc.Dropdown(
																id='xaxis-column',
																options=[{'label': i, 'value': i} for i in available_indicators],
																value='Talla'
															),
													
													dbc.RadioItems(
																className = "form-check-inline pr-10",
																id='xaxis-type',
																options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
																value='Linear',
																labelStyle={'display': 'inline-block'}
															),
												]
											)
								], md=4),

							dbc.Col(
								[
									dbc.FormGroup(
												[
													dbc.Label(html.B("Y - Axis"), html_for="yaxis-column"),

													dcc.Dropdown(
																id='yaxis-column',
																options=[{'label': i, 'value': i} for i in available_indicators],
																value='Peso'
															),
													
													dbc.RadioItems(
																className = "form-check-inline pr-10",
																id='yaxis-type',
																options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
																value='Linear',
																labelStyle={'display': 'inline-block'}
															),
												]
											)

								], md=4),
							dbc.Col(
								[

									dbc.FormGroup(
												[
													dbc.Label(html.B("Cluster"), html_for="cluster-column"),

													dcc.Dropdown(
														id='cluster-column',
														options=[{'label': i, 'value': i} for i in clusters],
														value='ZScorePesoTalla'
													)
												]
											)
								], md=4),
						]
					),
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
     Input('yaxis-type', 'value'),
	 Input('cluster-column', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type, cluster_column):

    fig = px.scatter(dt, x=xaxis_column_name, y=yaxis_column_name, opacity=0.5, color=cluster_column, hover_data=['IdBeneficiario'])

    fig.update_layout(margin={'l': 10, 'b': 10, 't': 10, 'r': 0}, hovermode='closest')
	
    fig.update_traces(marker=dict(size=15), selector=dict(mode='markers'), line=dict(width=3, color='white'))
    
    fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log') 
    
    fig.update_yaxes(title=yaxis_column_name, type='linear' if yaxis_type == 'Linear' else 'log') 

    return fig
    """return {
        'data': [dict(
            x = dff[xaxis_column_name],
			y = dff[yaxis_column_name],
			text= dff['IdBeneficiario'],
            mode='markers',
            marker={
				'color' : dff['EstadoIMC'],
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
    }"""

"""
	fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species",
                 size='petal_length', hover_data=['petal_width'])
				 
	fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    
    fig.update_xaxes(title=xaxis_column_name, 
                     type='linear' if xaxis_type == 'Linear' else 'log') 
    
    fig.update_yaxes(title=yaxis_column_name, 
                     type='linear' if yaxis_type == 'Linear' else 'log') 
"""




'''
dbc.CardHeader([
	html.Div([
		dcc.Dropdown(
			id='xaxis-column',
			options=[{'label': i, 'value': i} for i in available_indicators],
			value='Talla'
		),
		dbc.RadioItems(
			className = "form-check-inline pr-10",
			id='xaxis-type',
			options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
			value='Linear',
			labelStyle={'display': 'inline-block'}
		)
	],style={'width': '20%', 'display': 'inline-block'}),

	html.Div([
		dcc.Dropdown(
			id='yaxis-column',
			options=[{'label': i, 'value': i} for i in available_indicators],
			value='Peso'
		),
		dbc.RadioItems(
			className = "form-check-inline",
			id='yaxis-type',
			options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
			value='Linear',
			labelStyle={'display': 'inline-block, padding-right: 10px;'}
		)
	],style={'width': '20%', 'display': 'inline-block'}),
	
	html.Div([
		dcc.Dropdown(
			id='cluster-column',
			options=[{'label': i, 'value': i} for i in clusters],
			value='ZScorePesoTalla'
		)
	],style={'width': '20%', 'display': 'inline-block'}),
	
	
	
])
'''