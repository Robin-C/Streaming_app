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


app = dash.Dash(__name__)


app.layout = html.Div(
    [   html.H1(children='World leaders twitter popularity contest'),

        html.Div(children=
        'Number of mention of world leaders in the last 30 minutes on twitter.'),
        html.P(children=
        ['Under the hood, tweets are streamed through Tweepy, a Kafka producer then sends', html.Br(), 'the data to a topic which is consummed and stored to a postgres database.', html.Br(), 'Dash then queries the data on a callback loop. All this in real time.']),
        
        dcc.Graph(id='live-graph', animate=True),
        dcc.Graph(id='live-graph2', animate=True),        
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
      data = []
      cursor.execute('select * from count_leaders order by count desc')
      response = cursor.fetchall()
      data = response
      df = pd.DataFrame(data, columns=['leaders', 'count'])
      fig = px.bar(df,
            x=df['leaders'],
            y=df['count'],
            text=df['count'],
            color=df['leaders']
            )
    # set labels outside       
      fig.update_traces(textposition='outside')   
    # set y axis at 25% above the maximum value   
      fig.update_yaxes(range=[0, df['count'].max() * 1.25])  
     # set white background
      fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)'
            })
        
      return fig

@app.callback(Output('live-graph2', 'figure'),
              [Input('graph-update', 'n_intervals')])
def get_data_graph2(n):
      data = []
      cursor.execute("""with detail as (
	select date_trunc('minutes', created_at) as minutes, tweet as leaders, count(*) as leader_count
	from fact_tweets
	group by 1, 2
),

total as (
    select date_trunc('minutes', created_at) as minutes, count(*) as total_count
	from fact_tweets
	group by 1
),

final as (
    select detail.minutes, detail.leaders, cast(detail.leader_count as float) / cast(total.total_count as float) * 100 as percent
	from detail
	inner join total on detail.minutes = total.minutes
	order by 1 desc, 3 desc
)

select *
from final""")
      response = cursor.fetchall()
      data = response
      df = pd.DataFrame(data, columns=['minutes', 'leaders', 'percent'])
      df = df.round(2)
      fig = px.bar(df,
            x=df['minutes'],
            y=df['percent'],
            color=df['leaders'],
            barmode='stack'
            )
    # set labels outside       
     # fig.update_traces(textposition='outside')   
    # set y axis at 25% above the maximum value   
      fig.update_xaxes(range=[df['minutes'].min(), df['minutes'].max()])  
     # set white background
      fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)'
            })
        
      return fig     

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
