import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly as py
import plotly.express as px
import sqlalchemy
import psycopg2
from dotenv import load_dotenv
import os
import dash
from dash import dcc, html, Input, Output
import dash_table
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine, text

load_dotenv()

api_key = os.getenv("api_key")
db_host = os.getenv("host")
db_port = os.getenv("port")
db_name = os.getenv("dbname")
db_user = os.getenv("user")
db_password = os.getenv("password")

# Database connection
DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('user')}:{os.getenv('password')}"
    f"@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('dbname')}"
)
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
query = text("SELECT * FROM public.monthly_avg")
result = session.execute(query)
df = pd.DataFrame(result.fetchall(), columns=result.keys())
session.close()

df_2 = df[df['country'] == "Germany"]

iso_codes = {
    "Amsterdam": "NL",
    "Berlin": "DE",
    "Brussels": "BE",
    "Bucharest": "RO",
    "Budapest": "HU",
    "Copenhagen": "DK",
    "Dublin": "IE",
    "Edinburgh": "GB",
    "Helsinki": "FI",
    "Lisbon": "PT",
    "London": "GB",
    "Madrid": "ES",
    "Moscow": "RU",
    "Oslo": "NO",
    "Paris": "FR",
    "Prague": "CZ",
    "Reykjavik": "IS",
    "Rome": "IT",
    "Stockholm": "SE",
    "Vienna": "AT",
    "Warsaw": "PL",
    "Zurich": "CH"
}

df['alpha-3'] = df['country'].map(iso_codes)

df_countries = df[df['country'].isin(['Germany', 'Italy', 'Portugal'])]
df_germany = df[df['country'].isin(['Germany'])]

fig = px.choropleth(
    df,
    locations='alpha-3',
    color='avg_temp_month',
    hover_name='country',
    animation_frame='month',
    color_continuous_scale=px.colors.sequential.Plasma,
    projection='orthographic',
    title='Average Temperature Over Time',
    height=800,
    width=1200
)

fig.update_geos(showcoastlines=True, coastlinecolor="RebeccaPurple")

fig.update_layout(
    plot_bgcolor="#222222",
    paper_bgcolor="#222222",
    font_color="white"
)

graph2 = dcc.Graph(figure=fig)

table_updated2 = dash_table.DataTable(
    df_germany.to_dict('records'),
    [{"name": i, "id": i} for i in df_germany.columns],
    style_data={'color': 'white', 'backgroundColor': 'black'},
    style_header={
        'backgroundColor': 'rgb(210, 210, 210)',
        'color': 'black',
        'fontWeight': 'bold'
    },
    style_table={
        'minHeight': '400px', 'height': '400px', 'maxHeight': '400px',
        'minWidth': '900px', 'width': '900px', 'maxWidth': '900px',
        'margin': 'auto'
    }
)

fig = px.bar(df_countries,
             x='month',
             y='avg_temp_month',
             color='country',
             barmode='group',
             height=300,
             title="Germany vs Italy & Portugal",
             color_discrete_map={'Germany': '#7FD4C1', 'Italy': '#8690FF', 'Portugal': '#F7C0BB'})

fig.update_layout(
    plot_bgcolor="#222222",
    paper_bgcolor="#222222",
    font_color="white"
)

graph = dcc.Graph(figure=fig)

app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div([
    html.H1('The Avg Temperature in Germany', style={'textAlign': "center", 'color': 'blue'}),
    html.Div(html.P('Welcome'), style={'marginLeft': 50, 'marginRight': 50}),
    html.Div([
        html.Div('Here the challenge for this week!',
                 style={'backgroundColor': '#636EFA', 'color': 'white', 'width': '1050px', 'margin': 'auto'}),
        table_updated2,
        dcc.Dropdown(
            id='country-dropdown',
            options=[
                {'label': 'Germany', 'value': 'Germany'},
                {'label': 'Italy', 'value': 'Italy'},
                {'label': 'Portugal', 'value': 'Portugal'}
            ],
            value='Germany',
            style={'width': '200px'}
        ),
        graph,
        graph2
    ])
])


@app.callback(
    Output(table_updated2, "data"),
    Input("country-dropdown", "value"))
def update_table(selected_country):
    filtered_df = df[df['country'] == selected_country]
    return filtered_df.to_dict('records')


if __name__ == "__main__":
    app.run_server()