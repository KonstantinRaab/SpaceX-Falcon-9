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

# Prepare dropdown options for launch sites
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
    dropdown_options.append({'label': site, 'value': site})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    html.Div([
        dcc.Dropdown(
            id='site-dropdown',
            options=dropdown_options,
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True
        ),
        html.Br() # Add a line break for spacing
    ]),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Pie Chart Callback
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    
    if entered_site == 'ALL':
        # Calculate total success count for ALL sites
        fig = px.pie(
            filtered_df, 
            names='Launch Site', 
            values='class', 
            title='Total Successful Launches By Site (All Sites)'
        )
    else:
        # Filter the dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Calculate success (1) and failure (0) counts for the selected site
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['Outcome', 'count']
        
        fig = px.pie(
            success_counts, 
            names='Outcome', 
            values='count', 
            title=f'Launch Outcomes for Site: {entered_site}',
            labels={'Outcome': 'Launch Outcome'}, 
            color_discrete_map={'0': 'red', '1': 'green'}
        )
    return fig

# TASK 4: Scatter Plot Callback
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    
    # Filter by Payload Mass Range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    # Filter by Launch Site
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
    # Create the scatter plot
    fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class',
        color='Booster Version',
        title=f'Payload vs. Launch Outcome for Site: {entered_site} (Payload Range: {low}kg - {high}kg)',
        labels={'class': 'Launch Outcome (1=Success, 0=Failure)'},
        hover_data=['Booster Version']
    )
    
    return fig


# Run the app
if __name__ == '__main__':
    # Using app.run() as app.run_server() is deprecated
    app.run()
