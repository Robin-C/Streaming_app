import psycopg2
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.express as px
from dash.dependencies import Input, Output

connection = psycopg2.connect(user="root",
                              password="root",
                              host="postgres",
                              port="5432",
                              database="tweets")

cursor = connection.cursor()
df = pd.DataFrame(columns=['leaders', 'count'])
data = []


app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1*2000,
            n_intervals=0
        ),
    ]
)

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def get_data(n):
      cursor.execute('select * from count_leaders order by count desc')
      response = cursor.fetchall()
      data = response
      df = pd.DataFrame(data, columns=['leaders', 'count'])
     # df = pd.DataFrame(data=[['prout', 1], ['test', 2]], columns=["column1", "column2"])
      fig = px.bar(df,
            x=df['leaders'],
            y=df['count'],
            text=df['count'],
            color=df['leaders']
            )
     # set white background
      fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)'
            })

    
      return fig


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
