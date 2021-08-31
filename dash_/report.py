import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import duckdb

from data import tomas_pq, points_z
from app.misc import cols
from app.utils import nutrition_monitoring_plot

points_plot = pd.read_csv(points_z)


def report(idBen):
    col_query = ', '.join(cols)
    try:
        con = duckdb.connect()    #Inicialización de Duckdb para hacer query sobre un .parquet
        con.execute("PRAGMA threads=2")
        con.execute("PRAGMA enable_object_cache")
        query = f"SELECT * FROM '{tomas_pq}' WHERE IdBeneficiario = {idBen}"
        ben_df = con.execute(query).df()
        print(ben_df)
    except:
        print('Error al conectar tomas.parquet')
	
    fig = nutrition_monitoring_plot(idBen, ben_df, points_plot, 'spanish')
    if fig:
        layout= html.Div(id='my-div', children=[
                dcc.Graph(
                    id='my-graph-id',
                    figure=fig
                )
            ])
        return layout
