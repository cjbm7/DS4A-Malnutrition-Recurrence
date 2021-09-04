import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import json

from app.utils import translate_dataframe

from data import socio_eda_mpios, geojson_mpios, incid_mpio

incid = pd.read_parquet(incid_mpio)

with open(geojson_mpios) as geo_json:
    mpios_json = json.load(geo_json)

diction = {'fracc_desnutricion': 'wasting_prop.', 'fracc_recuperacion':'recover_prop.', 'fracc_reincidenci':'recurrence_prop.'}

incid = translate_dataframe(incid, diction)

available_indicator = ['wasting_prop.', 'recover_prop.', 'recurrence_prop.']

def update_g(dpto='all', mpio='all'):
	print(f'//////////{dpto, mpio}//////////')
	if mpio != 'all':
		df = incid[incid['cod_mpio']==mpio]
	elif dpto != 'all': 
		df = incid[incid['cod_dpto']==dpto]
	else:
		df = incid
	map_type = 'wasting_prop.'
	print(df)
	fig = px.choropleth(
        df,
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
	
	
	layout= html.Div(id='my-div', children=[
			dcc.Graph(
				id='my-graph-id',
				figure=fig
			)
		])
	return layout
