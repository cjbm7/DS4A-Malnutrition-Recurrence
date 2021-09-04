import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import time
import plotly.express as px

from app.utils import translate_dataframe
from app import dashapp
from data import tom3000_pq

inicio = time.time()
dt = pd.read_parquet(tom3000_pq)
fin = time.time()
print(f"Tiempo de ejecucion tomas3000: {fin-inicio}")


english = {
      'IdToma':'IdTake',
      'Registro': 'Record',
      'Vigencia': 'Year',
      'Toma': 'Take',
      'Servicio': 'Service',
      'FechaValoracionNutricional': 'Date nutr assessment',
      'EdadMeses': 'Age (mo)',
      'FechaMedicionPerimetroBraquial': 'Date arm circ measurement',
      'MedicionPerimetroBraquial': 'Arm circunference',
      'Peso': 'Weight',
      'Talla': 'Height', 
      'ZScoreTallaEdad': 'Height-for-age z-score',
      'ZScorePesoEdad': 'Weight-for-age z-score',
      'ZScorePesoTalla': 'Weight-for-height z-score',
      'ZScoreIMC': 'IMC z-score',
      'EstadoTallaEdad': 'Height-for-age status',
      'EstadoPesoEdad': 'Weight-for-age status',
      'EstadoPesoTalla': 'Weight-for-height status',
      'EstadoIMC': 'IMC status',
      'Flag': 'Flags',
      'FechaRegistroSaludNutricion': 'Date registration',
      'PresentaCarneVacunacion': 'Vaccination card',
      'ControlesCrecimDesarrollo': 'Growth and development control',
      'AntecedentePremadurez': 'Prematurity antecedent',
      'Direccion': 'Direction',
      'IdBeneficiario': 'IdBeneficiary',
      'Riesgo desnutricion (1 meses)': 'Undernutrition risk (1 mo)',
      'Riesgo desnutricion (2 meses)': 'Undernutrition risk (2 mo)',
      'Riesgo desnutricion (3 meses)': 'Undernutrition risk (3 mo)',
      'Sexo': 'Sex',
      'Estrato': 'Stratum',
      'ingresos_promP_imp': 'Household income',
      }

dt = translate_dataframe(dt, english)

available_indicators = ['Age (mo)',
						'Arm circunference',
						'Weight',
						'Height',
						'Height-for-age z-score',
						'Weight-for-age z-score',
						'Weight-for-height z-score',
						'IMC z-score',
						'Sex',
						'Stratum',
						'cod_mpio',
						'cod_dpto',
						'Household income',]

clusters = available_indicators  #Pendiente

layout = html.Div([
	dbc.Card([	
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
																value='Height'
																#value='Talla'
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
																value='Weight'
																#value='Peso'
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
													dbc.Label(html.B("Hue"), html_for="cluster-column"),

													dcc.Dropdown(
														id='cluster-column',
														options=[{'label': i, 'value': i} for i in clusters],
														value='Weight-for-height z-score'
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

    fig = px.scatter(dt, x=xaxis_column_name, y=yaxis_column_name, opacity=0.5, color=cluster_column, hover_data=['IdBeneficiary'])

    fig.update_layout(margin={'l': 10, 'b': 10, 't': 10, 'r': 0}, hovermode='closest')
	
    fig.update_traces(marker=dict(size=15), selector=dict(mode='markers'), line=dict(width=3, color='white'))
    
    fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log') 
    
    fig.update_yaxes(title=yaxis_column_name, type='linear' if yaxis_type == 'Linear' else 'log') 

    return fig
