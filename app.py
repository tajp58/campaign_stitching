import dash
import pandas as pd
import numpy as np
from dash import html, dcc, dash_table, Input, Output, State
from dash.exceptions import PreventUpdate

# Define your dataframe or import it as you did before
losers = pd.read_csv('./src/dash/data/campaignstitch.csv')
# Drop the columns that do not matter
losers.drop(['Volume', 'Avg Vol (3 month)', 'PE Ratio (TTM)', '52 Week Range'], axis='columns', inplace=True)
losers.columns = ['Symbol', 'Company Name', 'Price', 'Change', '% Change', 'Mkt Cap']
# Add the initial selected_campaigns column with default value
losers['selected_campaigns'] = 0

losers['platform'] = np.random.randint(1, 3, losers.shape[0])
# Create a copy of the 'Symbol' column and name it 'Symbol Reference'
losers['Reference'] = losers['Symbol']
# Add a unique identifier for each row
losers['ID'] = range(len(losers))

# Function to update selected campaigns
def update_selected_campaigns(selected_ids, current_value):
    for ID in selected_ids:
        losers.loc[losers['ID'] == ID, 'selected_campaigns'] = current_value

# Create the tables to show the information
table = html.Div([
    dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in losers.columns],
        data=losers.to_dict('records'),
        editable=False,
        style_as_list_view=True,
        style_data_conditional=[
            {'if': {'state': 'active'}, 'backgroundColor': 'white', 'border': '1px solid white'},
            {'if': {'column_id': 'Company Name'}, 'textAlign': 'left', 'text-indent': '10px', 'width': 100},
            {'if': {'filter_query': '{selected_campaigns} ne 0'}, 'display': 'none'} # Hide rows with selected_campaigns != 0
        ],
        fixed_rows={'headers': True},
        id='table',
        style_data={"font-size": "14px", 'width': 15, "background": "white", 'text-align': 'center'},
        row_selectable='multi',
        selected_rows=[],  # Initialize selected_rows as empty list
    )
])

# Create dropdown menu options
dropdown_options = [{'label': symbol_ref, 'value': symbol_ref} for symbol_ref in losers['Reference'].unique()]

app = dash.Dash(__name__)

# Layout of the page:
app.layout = html.Div([
    html.H2("Today's Company Losers"),
    html.H4("Select a Reference", id="Message1"),
    html.Button("Toggle Uncategorized", id="toggle_button", n_clicks=0),
    dcc.Dropdown(id='symbol_dropdown', options=dropdown_options, placeholder="Select a Reference"),
    html.Div(style={'margin-top': '20px'}),  # Add space between dropdown and table
    html.Div(table, style={'width': '60%'}),
    html.Button('Store Selections', id='store_button', n_clicks=0),
    html.Button('Complete & Export', id='export_button', n_clicks=0)
])

# Callback to update selected campaigns when button is clicked
@app.callback(Output("Message1", "children"),
              Output('table', 'selected_rows'),
              [Input('store_button', 'n_clicks')],
              [State('table', 'selected_rows'),
               State('table', 'data')])
def store_selections(n_clicks, selected_rows, data):
    if n_clicks > 0:
        current_value = n_clicks
        update_selected_campaigns(selected_rows, current_value)
        return f"{n_clicks} campaigns stored.", []
    else:
        raise PreventUpdate

# Callback to export dataframe to CSV when button is clicked
@app.callback(Output('export_button', 'n_clicks'),
              [Input('export_button', 'n_clicks')])
def export_to_csv_callback(n_clicks):
    if n_clicks > 0:
        losers.to_csv('campaignstitch_selected.csv', index=False)
        return 0
    else:
        raise PreventUpdate

# Callback to filter the table based on the selected symbol reference
@app.callback(Output('table', 'data'),
              [Input('symbol_dropdown', 'value')])
def filter_table(symbol_reference):
    if symbol_reference:
        filtered_data = losers[losers['Reference'] == symbol_reference].to_dict('records')
    else:
        filtered_data = losers.to_dict('records')
    return filtered_data

# Callback to toggle visibility of uncategorized campaigns
@app.callback(Output('table', 'style_data_conditional'),
              [Input('toggle_button', 'n_clicks')],
              [State('table', 'style_data_conditional')])
def toggle_uncategorized(n_clicks, current_style):
    if n_clicks % 2 == 0:  # Even number of clicks
        # Hide rows with selected_campaigns != 0
        current_style.append({'if': {'filter_query': '{selected_campaigns} ne 0'}, 'display': 'none'})
    else:
        # Show all rows
        current_style = [style for style in current_style if 'filter_query' not in style]
    return current_style

if __name__ == "__main__":
    app.run_server(debug=True)
