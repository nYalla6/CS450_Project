import dash
from dash import dcc, html, Input,Output,State
import seaborn as sns
import plotly.express as px
from dash.exceptions import PreventUpdate
import io
import base64
import pandas as pd

countries_continents = {
    "Africa": [
        "Algeria", "Angola", "Benin", "Botswana", "Burkina", "Burundi",
        "Cameroon", "Cape Verde", "Central African Republic", "Chad",
        "Comoros", "Congo", "Congo, Democratic Republic of", "Djibouti",
        "Egypt", "Equatorial Guinea", "Eritrea", "Ethiopia", "Gabon",
        "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast",
        "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi",
        "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique",
        "Namibia", "Niger", "Nigeria", "Rwanda", "Sao Tome and Principe",
        "Senegal", "Seychelles", "Sierra Leone", "Somalia", "South Africa",
        "South Sudan", "Sudan", "Swaziland", "Tanzania", "Togo", "Tunisia",
        "Uganda", "Zambia", "Zimbabwe"
    ],
    "Asia": [
        "Afghanistan", "Bahrain", "Bangladesh", "Bhutan", "Brunei",
        "Burma (Myanmar)", "Cambodia", "China", "East Timor", "India",
        "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan",
        "Korea, North", "Korea, South", "Kuwait", "Kyrgyzstan", "Laos",
        "Lebanon", "Malaysia", "Maldives", "Mongolia", "Nepal", "Oman",
        "Pakistan", "Philippines", "Qatar", "Russian Federation",
        "Saudi Arabia", "Singapore", "Sri Lanka", "Syria", "Tajikistan",
        "Thailand", "Turkey", "Turkmenistan", "United Arab Emirates",
        "Uzbekistan", "Vietnam", "Yemen"
    ],
    "Europe": [
        "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus",
        "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus",
        "CZ", "Denmark", "Estonia", "Finland", "France", "Georgia", "Germany",
        "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia",
        "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia", "Malta",
        "Moldova", "Monaco", "Montenegro", "Netherlands", "Norway", "Poland",
        "Portugal", "Romania", "San Marino", "Serbia", "Slovakia", "Slovenia",
        "Spain", "Sweden", "Switzerland", "Ukraine", "United Kingdom",
        "Vatican City"
    ],
    "North America": [
        "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada",
        "Costa Rica", "Cuba", "Dominica", "Dominican Republic", "El Salvador",
        "Grenada", "Guatemala", "Haiti", "Honduras", "Jamaica", "Mexico",
        "Nicaragua", "Panama", "Saint Kitts and Nevis", "Saint Lucia",
        "Saint Vincent and the Grenadines", "Trinidad and Tobago", "US"
    ],
    "Oceania": [
        "Australia", "Fiji", "Kiribati", "Marshall Islands", "Micronesia",
        "Nauru", "New Zealand", "Palau", "Papua New Guinea", "Samoa",
        "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu"
    ],
    "South America": [
        "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
        "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"
    ]
}
#graph configuration 
custom_config = {
    #'modeBarButtonsToRemove': ['zoom','zoomIn','zoomOut','autoScale','pan2d','resetScale','toImage'],
    #'modeBarButtonsToAdd': ['drawopenpath'],
    'displayModeBar': False,  # Show or hide display mode bar
    'displaylogo': False,  # Hide plotly logo
    'responsive': False, # Turning Off Responsiveness
    'staticPlot': True, # Making A Static Chart
}

# Load the my_df dataset from the csv in the folder
# Try reading the CSV file with different encodings
my_df = pd.read_csv('App4/country_statistics.csv', encoding='latin1')

#edit the GNI to be floats
my_df['Gross national income (GNI) per capita'] = my_df['Gross national income (GNI) per capita'].str.replace(',', '').astype(float)

model_pipeline=None
cont_list = ["None"] + list(countries_continents.keys())


continent_dropdown = html.Div(className="dropdown2_div",children=[html.P("Select Continent: "),dcc.Dropdown(id='ctry_dropdown',options=cont_list, value=None,style=dict(width=150,marginLeft=2))])
# radio_items=dcc.RadioItems(id='cat_radio_items_id',options=categorical_columns, value=None,inline=True)

num_buckets_slider = html.Div(className="slider_parent",children=[dcc.Slider(id='bucket_slider', min=2, max=20, value=10, step=1)])

#radio items for filter
filter_list = ['All', 10, 20, 30]
filter_radio = html.Div(className="fil_radio", children=[html.P("Num elements displayed: "),dcc.RadioItems(id='radio_itm', options=filter_list, value='All', inline=True)])

#dropdown for criteria
criteria_list = ['Human Development Index (HDI)', 'Life expectancy at birth', 'Gross national income (GNI) per capita']
criteria_dropdown = html.Div(className="crit_drop",children=[html.P("Select Continent: "),dcc.Dropdown(id='criteria_dropdown',options=criteria_list, value=None,style=dict(width=300,marginLeft=2))])

app = dash.Dash(__name__)
server = app.server


#### layout
app.layout = html.Div(className="parent_container", children=[
    #row one holds the title
    html.Div("Countries and Quality of Life", id="row1"),

    #row 2 holds the two graphs and their interactive components
    html.Div(id="row2", children=[
        #graph 1: scatter of hdi index vs life expectancy
        html.Div(className="row2_child1", children=[
            continent_dropdown,
            html.Div(dcc.Graph(id='graph1', config=custom_config),style=dict(width="100%"))
        ]),
        #graph 2: histogram of GNI
        html.Div(className="row2_child2", children=[
            num_buckets_slider,
            html.Div(dcc.Graph(id='graph2', config=custom_config),style=dict(width="100%"))
        ])
    ]),

    #row 3, similar to row 2 holding graph 1 and 2
    html.Div(id="row3", children=[
        #graph 1: scatterplot of expected schooling vs life expectancy, bigger for higher gni
        html.Div(className="row2_child1", children=[
            filter_radio,
            html.Div(dcc.Graph(id='graph3', config=custom_config),style=dict(width="100%"))
        ]),
        #graph 4: ordered bar chart of countries based on a given criteria
        html.Div(className="row2_child2", children=[
            criteria_dropdown,
            html.Div(dcc.Graph(id='graph4', config=custom_config),style=dict(width="100%"))
        ])
    ]),


])




### Define callback function for graph 1, the hdi versus life expectancy
@app.callback(Output('graph1', 'figure'), Input('ctry_dropdown', 'value'))
def update_graph1(target_variable):
    title = ""
    if target_variable is None:
        # If no continent selected, show all continents, HDI vs life expectancy
        fig = px.scatter(x=my_df['Human Development Index (HDI)'], y=my_df['Life expectancy at birth'])
        fig.update_xaxes(title_text='Human Development Index (HDI)')
        fig.update_yaxes(title_text='Life expectancy at birth')

        title = "All Countries: HDI Index vs. Life Expectancy"
    else:
        # Get the list of countries for the selected continent
        if target_variable == "None":
            countries_displayed = list(countries_continents.keys())
        else :
            countries_displayed = countries_continents[target_variable]
        
        # Filter the DataFrame to include only the countries from the selected continent
        filtered_df = my_df[my_df['Country'].isin(countries_displayed)]
        # Plot HDI vs life expectancy for the selected continent
        fig = px.scatter(x=filtered_df['Human Development Index (HDI)'], y=filtered_df['Life expectancy at birth'])
        fig.update_xaxes(title_text='Human Development Index (HDI)')
        fig.update_yaxes(title_text='Life expectancy at birth')
        title = f"{target_variable}: HDI Index vs. Life Expectancy"
        
    #customizing the title/graph
    custom_fig_title = dict(text=title, x=0.5,font=dict(family='Arial',size=20,color='Black')) #fig.update_layout(title=customize.custom_fig_title)
    fig.layout = dict(title=custom_fig_title,
                    margin=dict(l=20,r=40,t=50,b=50,pad=0),
                    plot_bgcolor="white", #Sets the background color of the plotting area in-between x and y axes.
                    paper_bgcolor='rgba(192, 242, 204, 0.8)', #Sets the background color of the paper where the graph is drawn.
                    modebar=dict(orientation='v', activecolor='gray',bgcolor="white", color="#ededed"),
                    hovermode=False, # one of ( "x" | "y" | "closest" | False | "x unified" | "y unified" )
                    )

    return fig

# callback and update for graph two, the histogram with the bucket slider
@app.callback(Output('graph2', 'figure'), Input('bucket_slider', 'value'))
def update_graph2(num_buckets):
    title = "GNI by Groups"
    if num_buckets is None:
        filtered_df = my_df.sort_values(by='Gross national income (GNI) per capita')

        
        fig = px.histogram(filtered_df, x='Gross national income (GNI) per capita', nbins=8)
        fig.update_layout(xaxis_title='Gross National Income (GNI) per Capita', yaxis_title='Number of countries')
    else:
        #sort the gni
        # filtered_df = my_df.sort_values(by='Gross national income (GNI) per capita')
        filtered_df = my_df.sort_values(by='Gross national income (GNI) per capita')

        
        fig = px.histogram(filtered_df, x='Gross national income (GNI) per capita', nbins=num_buckets)
        fig.update_layout(xaxis_title='Gross National Income (GNI) per Capita', yaxis_title='Number of countries')
    
    custom_fig_title = dict(text=title, x=0.5,font=dict(family='Arial',size=20,color='Black')) #fig.update_layout(title=customize.custom_fig_title)
    fig.layout = dict(title=custom_fig_title,
                    margin=dict(l=20,r=40,t=50,b=50,pad=0),
                    plot_bgcolor="white", #Sets the background color of the plotting area in-between x and y axes.
                    paper_bgcolor='rgba(192, 242, 204, 0.8)', #Sets the background color of the paper where the graph is drawn.
                    modebar=dict(orientation='v', activecolor='gray',bgcolor="white", color="#ededed"),
                    hovermode=False, # one of ( "x" | "y" | "closest" | False | "x unified" | "y unified" )
                    )    
    return fig

#update graph3 with the filters 
@app.callback(Output('graph3', 'figure'), Input('radio_itm', 'value'))
def update_graph3(filter_num):
    if filter_num == None or filter_num == "All":
         fig = px.scatter(my_df, 
                     x='Expected years of schooling', 
                     y='Life expectancy at birth',
                     size='Gross national income (GNI) per capita',
                     hover_data=['Country'],
                     title=f'Expected Years of Schooling vs. Life Expectancy for Countries with Expected Years of Schooling {filter_num} or Less',
                     labels={'Expected years of schooling': 'Expected Years of Schooling', 
                             'Life expectancy at birth': 'Life Expectancy at Birth'}
                 )
    else:
        sorted_df = my_df.sort_values(by='Gross national income (GNI) per capita', ascending=False)
        fig = px.scatter(sorted_df.head(filter_num), 
                    x='Expected years of schooling', 
                    y='Life expectancy at birth',
                    size='Gross national income (GNI) per capita',
                    hover_data=['Country'],
                    title=f'Expected Years of Schooling vs. Life Expectancy for Countries with Expected Years of Schooling {filter_num} or Less',
                    labels={'Expected years of schooling': 'Expected Years of Schooling', 
                            'Life expectancy at birth': 'Life Expectancy at Birth'}
                )
    title = "Expected years of Schooling vs Life Expectancy, GNI as size"
    custom_fig_title = dict(text=title, x=0.5,font=dict(family='Arial',size=20,color='Black')) #fig.update_layout(title=customize.custom_fig_title)
    fig.layout = dict(title=custom_fig_title,
                    margin=dict(l=20,r=40,t=50,b=50,pad=0),
                    plot_bgcolor="white", #Sets the background color of the plotting area in-between x and y axes.
                    paper_bgcolor='rgba(192, 242, 204, 0.8)', #Sets the background color of the paper where the graph is drawn.
                    modebar=dict(orientation='v', activecolor='gray',bgcolor="white", color="#ededed"),
                    hovermode=False, # one of ( "x" | "y" | "closest" | False | "x unified" | "y unified" )
                    )
    return fig

#update graph4
@app.callback(Output('graph4', 'figure'), Input('criteria_dropdown', 'value'))
def update_graph4(criteria):
    print("column: ", criteria)
    if criteria is None:
        PreventUpdate
    else:
        sorted_df = my_df.sort_values(by=criteria, ascending=False).head(10) 
        sorted_df = sorted_df.sort_values(by=criteria, ascending=True)
        fig = px.bar(sorted_df,
             x=criteria,  
             y='Country', # Categories for the bars
             orientation='h',
             
            )
        title="Top Ten Countries"
        custom_fig_title = dict(text=title, x=0.5,font=dict(family='Arial',size=20,color='Black')) #fig.update_layout(title=customize.custom_fig_title)
        fig.layout = dict(title=custom_fig_title,
                    margin=dict(l=20,r=40,t=50,b=50,pad=0),
                    plot_bgcolor="white", #Sets the background color of the plotting area in-between x and y axes.
                    paper_bgcolor='rgba(192, 242, 204, 0.8)', #Sets the background color of the paper where the graph is drawn.
                    modebar=dict(orientation='v', activecolor='gray',bgcolor="white", color="#ededed"),
                    hovermode=False, # one of ( "x" | "y" | "closest" | False | "x unified" | "y unified" )
                    )
    return fig




if __name__ == '__main__':
    app.run_server(debug=False)