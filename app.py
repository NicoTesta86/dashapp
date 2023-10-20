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
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output, State
from dash import dash_table
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text


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
# Create an engine
engine = create_engine(DATABASE_URL)
# Establish a session using the engine
Session = sessionmaker(bind=engine)
session = Session()
# Execute the SQL query and fetch data into a pandas DataFrame
query = text("SELECT * FROM public.monthly_avg")
result = session.execute(query)
df = pd.DataFrame(result.fetchall(), columns=result.keys())
# Close the session
session.close()



df_2=df[df['country'] == "Germany"]

iso_codes =  {
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

import plotly.express as px

# Create the animated choropleth map
fig = px.choropleth(
    merged_df,
    locations="alpha-3",
    color="avg_temp_month",
    animation_frame="year",  
    scope="europe",
    title="Temperature Over Time in Selected Countries",
    height=800,
    width=1200
)


# Customize the map appearance if needed
fig.update_geos(projection_type="natural earth")


# Personalizza l'aspetto della mappa
fig.update_geos(showcoastlines=True, coastlinecolor="RebeccaPurple")

# Personalizza l'aspetto generale del grafico
fig.update_layout(
    plot_bgcolor="#222222",
    paper_bgcolor="#222222",
    font_color="white"
)

graph2 = dcc.Graph(figure=fig)


table_updated2 = dash_table.DataTable(df_germany.to_dict('records'),
                                  [{"name": i, "id": i} for i in df_germany.columns],
                               style_data={'color': 'white','backgroundColor': 'black'},
                              style_header={
                                  'backgroundColor': 'rgb(210, 210, 210)',
                                  'color': 'black','fontWeight': 'bold'}, 
                                     style_table={
                                         'minHeight': '400px', 'height': '400px', 'maxHeight': '400px',
                                         'minWidth': '900px', 'width': '900px', 'maxWidth': '900px', 
                                         'margin': 'auto'} 
                                     )


fig = px.bar(df_countries, 
             x='month', 
             y='avg_temp_month',  
             color='country',
             barmode='group',
             height=300, title = "Germany vs Italy & Portugal",)

fig = fig.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white"
    )

graph = dcc.Graph(figure=fig)

app =dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

hidden_columns = ['lat', 'lon', 'alpha-3']

radio= dcc.RadioItems(id="countries",options=['Germany', 'Italy', 'Portugal'], value="Germany", 
                      inline=True, style ={'paddingRight': '30px'})


app.layout = html.Div([html.H1('The Avg Temperature in Berlin', style={'textAlign':"center",
                                                                      'color':'blue'}), 
                       html.Div(html.P('Welcome'), style={'marginLeft': 50, 'marginRight': 50}),
                       html.Div([html.Div('Here the challenge fot this week!', 
                                          style={'backgroundColor': '#636EFA', 'color': 'white', 
                                                 'width': '1050px', 'margin': 'auto' }),
                                 table_updated2  , radio, graph,  graph2])
                      ])



@callback(
    Output(graph, "figure"), 
    Input("countries", "value"))



#let's also define discrete colors for each bar, so we can distinguish them easily, everytime we change our selection

def update_bar_chart(country): 
    mask = df_countries["country"]==(country)
    fig =px.bar(df_countries[mask], 
             x='month', 
             y='avg_temp_month',  
             color='country',
             color_discrete_map = {'Germany': '#7FD4C1', 'Italy': '#8690FF', 'Portugal': '#F7C0BB'},
             barmode='group',
             height=300, title = "Berlin vs Rome & Lisbon",)
    fig = fig.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white"
    )

    return fig 



if __name__ == "__main__":
    app.run_server()



server = app.server