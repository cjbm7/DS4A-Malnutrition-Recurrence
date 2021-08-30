import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import json

from data import socio_eda_mpios, geojson_mpios

soct = pd.read_parquet(socio_eda_mpios)

with open(geojson_mpios) as geo_json:
    mpios_json = json.load(geo_json)

def update_g(dpto='all', mpio='all'):
	print(f'//////////{dpto, mpio}//////////')
	if mpio != 'all':
		df = soct[soct['cod_mpio']==mpio]
	elif dpto != 'all': 
		df = soct[soct['cod_dpto']==dpto]
	else:
		df = soct
	map_type = 'prom_gasto_pper'
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
