import dash                     
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import plotly.express as px     
import pandas as pd             


df = pd.read_csv("Animals_Inventory.csv")
df["intake_time"] = pd.to_datetime(df["intake_time"])
df["intake_time"] = df["intake_time"].dt.hour



app = dash.Dash(__name__, external_stylesheets= ['https://codepen.io/chriddyp/pen/bWLwgP.css'])

app.layout = html.Div([
    html.H1("Dashboard of Animal Shelter", style={"textAlign":"center"}),
    html.Hr(),
    html.P("Select an animal:"),
    html.Div(html.Div([
        dcc.RadioItems(id='animal', inline= True,
                     value="CAT",
                     options=[{'label': 'DOG', 'value': 'DOG'},
                              {'label': 'CAT', 'value': 'CAT'},
                              {'label': 'BIRD', 'value': 'BIRD'},
                              {'label': 'WILDLIFE', 'value': 'WILDLIFE'}]),
    ],className="three columns"),className="row"),

    html.Div(id="output", children=[]),
])


@app.callback(Output(component_id="output", component_property="children"),
              Input(component_id="animal", component_property="value"),
)
def make_graphs(animal_chosen):
    # HISTOGRAM
    df_hist = df[df["animal_type"]==animal_chosen]
    fig_hist = px.histogram(df_hist, x="animal_breed", labels= {"animal_breed" : "Animal Breed"}, histnorm= "percent", title= "Histogram")

    # STRIP CHART
    fig_strip = px.strip(df_hist, x="animal_stay_days", y="intake_type", labels= {"animal_stay_days" : "Animal stay Days", "intake_type" : "Intake Type"}, title= "Strip Chart")

    # SUNBURST
    df_sburst = df.dropna(subset=['chip_status'])
    df_sburst = df_sburst[df_sburst["intake_type"].isin(["STRAY", "FOSTER", "OWNER SURRENDER"])]
    fig_sunburst = px.sunburst(df_sburst, path=["animal_type", "intake_type", "chip_status"], title= "Sunburst hierarchial data")

    # Empirical Cumulative Distribution
    df_emp = df[df["animal_type"].isin(["DOG","CAT"])]
    fig_emp = px.ecdf(df_emp, x="animal_stay_days", color="animal_type", labels= {"animal_stay_days" : "Animal stay Days", "animal_type" : "Animal Type"}, title= "Empirical Cumulative Distribution")

    # LINE CHART
    df_line = df.sort_values(by=["intake_time"], ascending=True)
    df_line = df_line.groupby(
        ["intake_time", "animal_type"]).size().reset_index(name="count")
    fig_line = px.line(df_line, x="intake_time", y="count",
                       color="animal_type", markers=True, labels= {"intake_time" : "Intake Time"})

    return [
        html.Div([
            html.Div([dcc.Graph(figure=fig_hist)], className="six columns", style= {"textAlign":"center"}),
            html.Div([dcc.Graph(figure=fig_strip)], className="six columns", style= {"textAlign":"center"}),
        ], className="row"),
        html.Hr(),
        html.Div([
            html.Div([dcc.Graph(figure=fig_sunburst)], className="six columns"),
            html.Div([dcc.Graph(figure=fig_emp)], className="six columns"),
        ], className="row"),
        html.Div([
            html.Div([dcc.Graph(figure=fig_line)], className="twelve columns"),
        ], className="row"),
    ]


if __name__ == '__main__':
    app.run_server(debug=True)