# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + [
                                        {'label': site, 'value': site}
                                        for site in sorted(spacex_df['Launch Site'].unique())
                                    ],
                                    value='ALL',                             # default selection
                                    placeholder='Select a Launch Site here',
                                    searchable=True,
                                    clearable=False
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload],   # uses the values you computed above
                                    marks={0: '0', 2500: '2.5k', 5000: '5k', 7500: '7.5k', 10000: '10k'},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)

def update_success_pie(selected_site):
    if selected_site == 'ALL':
        # sum of successes (class==1) per site
        df_all = (spacex_df.groupby('Launch Site')['class']
                            .sum()
                            .reset_index())
        fig = px.pie(
            df_all,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # success vs failure for the selected site
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        outcome = (df_site['class']
                   .value_counts()
                   .rename({1: 'Success', 0: 'Failure'})
                   .reset_index())
        outcome.columns = ['Outcome', 'Count']
        fig = px.pie(
            outcome,
            values='Count',
            names='Outcome',
            title=f'Total Success vs. Failure for {selected_site}'
        )
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    # filter by payload range first
    dff = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                    (spacex_df['Payload Mass (kg)'] <= high)]
    # filter by site if not ALL
    if selected_site != 'ALL':
        dff = dff[dff['Launch Site'] == selected_site]

    title = ('Correlation between Payload and Success for all Sites'
             if selected_site == 'ALL'
             else f'Correlation between Payload and Success for {selected_site}')

    fig = px.scatter(
        dff,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title,
        labels={'class': 'Launch Outcome'}
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
