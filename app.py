import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

from dash.dependencies import Input, Output, State
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt

# importing mean() 
from statistics import mean # - DeJans


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server


# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

# Dictionary of important locations in New York
list_of_locations = {
    "Millennium Park": {"lat": 41.882583, "lon": -87.622554},
    "Wrigley Field": {"lat": 41.948536, "lon": -87.655337},
    "O'Hare International Airport": {"lat": 41.979781, "lon": -87.905655},
    "Chicago Midway International Airport": {"lat": 41.786772, "lon": -87.752144},
    "Chicago History Museum": {"lat": 41.911945, "lon": -87.631660},
    "DePaul University": {"lat": 41.924788, "lon": -87.656453},
}

# Initialize data frame
# df1 = pd.read_csv(
    # "uber-rides-data1.csv",
    # dtype=object,
# )
# df2 = pd.read_csv(
    # "uber-rides-data2.csv",
    # dtype=object,
# )
# df3 = pd.read_csv(
    # "uber-rides-data3.csv",
    # dtype=object,
# )
# df = pd.concat([df1, df2, df3], axis=0)

dfChicago = pd.read_csv(
    #"https://gist.github.com/addejans/07c304e4d223f4d2aa69ea63ab8daab1",
    "Taxi_Trips.csv",
    dtype=object,
    usecols=['Date/Time','Lat','Lon','DO_Lat','DO_Lon','Miles','Fare','Hour']
)
df = dfChicago

df["Date/Time"] = pd.to_datetime(df["Date/Time"], format="%Y-%m-%d %H:%M")
df.index = df["Date/Time"]
df.drop("Date/Time", 1, inplace=True)
totalList = []
for month in df.groupby(df.index.month):
    dailyList = []
    for day in month[1].groupby(month[1].index.day):
        dailyList.append(day[1])
    totalList.append(dailyList)
totalList = np.array(totalList)


# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        # html.Img(
                            # className="logo", src=app.get_asset_url("dash-logo-new.png")
                        # ),
                        # html.H1("RouteSim Analytics"),
                        html.H2("CHICAGO TAXI DATA"),
                        html.P(
                            """Select different days using the date picker.\n
                            Select different hours for Taxi Trip Time Map by selecting
                            different time frames on the histogram."""
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=dt(2020, 1, 15),
                                    max_date_allowed=dt(2020, 1, 29),
                                    initial_visible_month=dt(2020, 1, 22),
                                    date=dt(2020, 1, 22).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="location-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_locations
                                            ],
                                            placeholder="Zoom to point of interst",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select times
                                        dcc.Dropdown(
                                            id="bar-selector",
                                            options=[
                                                {
                                                    "label": str(n) + ":00",
                                                    "value": str(n),
                                                }
                                                for n in range(24)
                                            ],
                                            multi=True,
                                            placeholder="Select certain hours",
                                        ),
                                        html.P([html.Br(), 'Select PUDO data to be displayed:']),
                                        dcc.RadioItems(
                                            id = 'PUDO-selector',
                                            inputStyle={"margin-right": "10px"},
                                            style = {
                                                'padding-left': '20px'
                                            },
                                            options=[
                                                {'label': 'Pickups', 'value': 'PU'},
                                                {'label': 'Dropoffs', 'value': 'DO'},
                                                {'label': 'Pickups & Dropoffs', 'value': 'PUDO'},
                                                {'label': 'Pickups & Dropoffs w/ trips (limit 100 lines)', 'value': 'PUDOTrips'}
                                            ],
                                            value='PU'
                                        ),
                                        # html.P([html.Br(), 'Display trip lines:']),
                                        # dcc.Checklist(
                                            # id = "trip-selector",
                                            # inputStyle={"margin-right": "10px"},
                                            # style = {
                                                # 'padding-left': '20px'
                                            # },
                                            # options=[
                                                # {'label': 'Show trip line*', 'value': 'TRUE'}
                                            # ],
                                            # value=[],
                                            # labelStyle={'display': 'inline-block'}
                                        # ),
                                        # html.P("*must be showing PUDO points, limit 100 lines")
                                        # daq.ToggleSwitch(
                                            # label='Display Trips',
                                            # labelPosition='bottom'
                                        # ),  
                                    ],
                                ),
                            ],
                        ),
                        dcc.Markdown(
                            children=[
                                "---",
                                "###### Overall Day Data:"
                            ],
                        ),
                        html.P(id="total-rides"),
                        html.P(id="average-miles"), #-DeJans
                        html.P(id="average-fare"), #-DeJans
                        dcc.Markdown(
                            children=[
                                "---",
                                "###### Selected Hourly Data:"
                            ]
                        ),
                        html.P(id="total-rides-selection"),
                        html.P(id="average-fare-selection"), #-DeJans
                        html.P(id="date-value"),
                        dcc.Markdown(
                            children=[
                                "---",
                                "###### Selected Fare Data:"
                            ]
                        ),
                        html.P(
                            """Select trips to be displayed based on taxi fare."""
                        ),
                        # RangeSlider has included=True by default #-DeJans
                        dcc.RangeSlider(
                            id='fare-slider',
                            #//TODO: Figure out how to display value selected above dot
                            #updatemode = 'drag',  
                            #Note: Turning drag on has shown poor performance when generating the map
                            min=0,
                            max=55,
                            value=[0, 50],
                            marks={
                                0: {'label': '$0', 'style': {'color': '#f50'}},
                                5: {'label': '$5', 'style': {'color': '#32cd32'} },
                                10: {'label': '$10', 'style': {'color': '#32cd32'}},
                                15: {'label': '$15', 'style': {'color': '#32cd32'}},
                                20: {'label': '$20', 'style': {'color': '#32cd32'}},
                                25: {'label': '$25', 'style': {'color': '#32cd32'}},
                                30: {'label': '$30', 'style': {'color': '#32cd32'}},
                                35: {'label': '$35', 'style': {'color': '#32cd32'}},
                                40: {'label': '$40', 'style': {'color': '#32cd32'}},
                                45: {'label': '$45', 'style': {'color': '#32cd32'}},
                                50: {'label': '$50', 'style': {'color': '#32cd32'}},
                                55: {'label': '$55+', 'style': {'color': '#f50'}}
                            }
                        ),
                        html.P([html.Br()]),
                        html.P(id='total-fare-range'),
                        html.P(id='selected-fare-range'),
                        # html.P([html.Br(), 'Trip Length Distribution:']),
                        html.P([html.Br()]),
                        dcc.Graph(
                            id='length-graph',
                        ),
                        dcc.Markdown(
                            children=[
                                "---",
                                "Source: [Chicago Data Portal](https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew/data)"
                            ]
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Markdown(
                            children=[
                                "#### Taxi Fare Heat-Map",
                                "Use fare range-slider to filter trips based on fare."
                            ]
                        ),
                        dcc.Graph(id="heat-graph"),
                        dcc.Markdown(
                            children=[
                                "---",
                                "#### Taxi Trip Time Heat-Map"
                            ]
                        ),
                        dcc.Graph(id="map-graph"),
                        html.Div(
                            className="text-padding",
                            children=[
                                "Select any of the bars on the histogram to section data by time."
                            ],
                        ),
                        dcc.Graph(id="histogram"),
                    ],
                ),
            ],
        )
    ]
)



# Gets the amount of days in the specified month
# Index represents month (0 is March 2019, 1 is April 2019, ... etc.)
daysInMonth = [31,29]

# Get index for the specified month in the dataframe
monthIndex = pd.Index(["Jan", "Feb"])

# Get the amount of rides per hour based on the time selected
# This also higlights the color of the histogram bars based on
# if the hours are selected
def get_selection(month, day, selection):
    xVal = []
    yVal = []
    xSelected = []
    colorVal = [
        "#F4EC15",
        "#DAF017",
        "#BBEC19",
        "#9DE81B",
        "#80E41D",
        "#66E01F",
        "#4CDC20",
        "#34D822",
        "#24D249",
        "#25D042",
        "#26CC58",
        "#28C86D",
        "#29C481",
        "#2AC093",
        "#2BBCA4",
        "#2BB5B8",
        "#2C99B4",
        "#2D7EB0",
        "#2D65AC",
        "#2E4EA4",
        "#2E38A4",
        "#3B2FA0",
        "#4E2F9C",
        "#603099",
    ]

    # Put selected times into a list of numbers xSelected
    xSelected.extend([int(x) for x in selection])

    for i in range(24):
        # If bar is selected then color it white
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = "#FFFFFF"
        xVal.append(i)
        # Get the number of rides at a particular time
        yVal.append(len(totalList[month][day][totalList[month][day].index.hour == i]))
    return [np.array(xVal), np.array(yVal), np.array(colorVal)]
    
    
# Get the amount of rides per hour based on the time selected
# This also higlights the color of the histogram bars based on
# if the hours are selected
def get_length_selection(month, day, selection, selectedRange):
        
    listCoords = getLatLonColor(selection, month, day)
    listCoords = getLatLonFareColor2(listCoords, selectedRange)
    max_length_value = int(listCoords['Miles'].astype(float).max())
    min_length_value = int(listCoords['Miles'].astype(float).min())
    
    xVal = []
    yVal = []
    xSelected = []
    colorVal = [
        "#FF8000" for i in range(max_length_value)
    ]

    # Put selected times into a list of numbers xSelected
    # xSelected.extend([int(x) for x in selection])

    step = 2 #//TODO: return the step to be used for the ticks.
    for i in range(min_length_value,max_length_value+step,step):
        # ## If bar is selected then color it white
        # if i in xSelected and len(xSelected) < 24:
            # colorVal[i] = "#add8e6"
        xVal.append(i)
        # Get the number of rides at a particular mileage range
        yVal.append(len(listCoords[(listCoords['Miles'].astype(float) < i) & (listCoords['Miles'].astype(float) >= i - step)]))
    return [np.array(xVal), np.array(yVal), np.array(colorVal)], max_length_value, min_length_value, step


# Selected Data in the Histogram updates the Values in the DatePicker
@app.callback(
    Output("bar-selector", "value"),
    [Input("histogram", "selectedData"), Input("histogram", "clickData")],
)
def update_bar_selector(value, clickData):
    holder = []
    if clickData:
        holder.append(str(int(clickData["points"][0]["x"])))
    if value:
        for x in value["points"]:
            holder.append(str(int(x["x"])))
    return list(set(holder))



# Clear Selected Data if Click Data is used
@app.callback(Output("histogram", "selectedData"), [Input("histogram", "clickData")])
def update_selected_data(clickData):
    if clickData:
        return {"points": []}
        
# Clear Selected Data if Click Data is used
# @app.callback(Output("length-graph", "selectedData"), [Input("length-graph", "clickData")])
# def update_selected_data(clickData):
    # if clickData:
        # return {"points": []}

        
# Update the total number of rides, avg miles, and avg fare Tag
@app.callback([Output("total-rides", "children"), Output("average-miles", "children"), Output("average-fare", "children")], [Input("date-picker", "date")])
def update_total_rides(datePicked):
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    day_total_rides = "Total Number of rides: {:,d}".format(len(totalList[date_picked.month - 1][date_picked.day - 15]))
    day_avg_miles = "Day Average Miles: {:,.2f}".format(mean(list(map(float, totalList[date_picked.month - 1][date_picked.day - 15]['Miles']))))
    day_avg_fare = "Day Average Fare: ${:,.2f}".format(mean(list(map(float, totalList[date_picked.month - 1][date_picked.day - 15]['Fare']))))
    return day_total_rides, day_avg_miles, day_avg_fare
 

# Update the total number of rides Tag
# @app.callback(Output("total-rides", "children"), [Input("date-picker", "date")])
# def update_total_rides(datePicked):
    # date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    # return "Total Number of rides: {:,d}".format(
        # len(totalList[date_picked.month - 1][date_picked.day - 1])
    # )
 
# Update the average miles Tag - DeJans
# @app.callback(Output("average-miles", "children"), [Input("date-picker", "date")])
# def update_average_miles(datePicked):
    # date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    # return "Day Average Miles: {:,.2f}".format(
        # mean(list(map(float, totalList[date_picked.month - 1][date_picked.day - 1]['Miles'])))
    # )

# Update the average fare Tag - DeJans
# @app.callback(Output("average-fare", "children"), [Input("date-picker", "date")])
# def update_average_miles(datePicked):
    # date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    # return "Day Average Fare: ${:,.2f}".format(
        # mean(list(map(float, totalList[date_picked.month - 1][date_picked.day - 1]['Fare'])))
    # )
 
# Update the total number of rides & average fare in selected times
@app.callback(
    [Output("total-rides-selection", "children"), Output("average-fare-selection", "children"), Output("date-value", "children")],
    [Input("date-picker", "date"), Input("bar-selector", "value")],
)
def update_total_rides_selection(datePicked, selection):
    firstOutput = ""
    secondOutput = ""

    if selection is not None and len(selection) is not 0:
        date_picked = dt.strptime(datePicked, "%Y-%m-%d")
        totalInSelection = 0
        averageFareInSelection = 0
        for x in selection:
            totalInSelection += len(
                totalList[date_picked.month - 1][date_picked.day - 15][
                    totalList[date_picked.month - 1][date_picked.day - 15].index.hour
                    == int(x)
                ]
            )
            for idx, hr in enumerate(totalList[date_picked.month - 1][date_picked.day - 15]['Hour']):
                if int(hr) == int(x):
                    averageFareInSelection += float(totalList[date_picked.month - 1][date_picked.day - 15]['Fare'][idx])
        if selection: averageFareInSelection /= totalInSelection
        firstOutput = "Total rides in selection: {:,d}".format(totalInSelection)
        secondOutput = "Average fare in selection: ${:,.2f}".format(averageFareInSelection)

    if (
        datePicked is None
        or selection is None
        or len(selection) is 24
        or len(selection) is 0
    ):
        return firstOutput, secondOutput, (datePicked, " - showing all hours")

    holder = sorted([int(x) for x in selection])

    if holder == list(range(min(holder), max(holder) + 1)):
        if len(holder) > 1:
            return (
                firstOutput,
                secondOutput, # - DeJans
                (
                    datePicked,
                    " - showing hours: ",
                    holder[0],
                    "-",
                    holder[len(holder) - 1],
                ),
            )
        else:
            return (
                firstOutput,
                secondOutput, # - DeJans
                (
                    datePicked,
                    " - showing hour: ",
                    holder[0],
                ),
            )

    holder_to_string = ", ".join(str(x) for x in holder)
    return firstOutput, secondOutput, (datePicked, " - showing hour(s): ", holder_to_string) #avg here - DeJans

# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
    Output("histogram", "figure"),
    [Input("date-picker", "date"), Input("bar-selector", "value")],
)
def update_histogram(datePicked, selection):
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    monthPicked = date_picked.month - 1
    dayPicked = date_picked.day - 15

    [xVal, yVal, colorVal] = get_selection(monthPicked, dayPicked, selection)

    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            ticksuffix=":00",
        ),
        yaxis=dict(
            range=[0, max(yVal) + max(yVal) / 4],
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
        annotations=[
            dict(
                x=xi,
                y=yi,
                text=str(yi),
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(color="white"),
            )
            for xi, yi in zip(xVal, yVal)
        ],
    )

    return go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=dict(color=colorVal), hoverinfo="x"),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal / 2,
                hoverinfo="none",
                mode="markers",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )
    
# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
    Output("length-graph", "figure"),
    [
        Input("date-picker", "date"), 
        Input("bar-selector", "value"),
        Input('fare-slider', 'value')
    ],
)
def update_length_histogram(datePicked, selection, selectedRange):
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    monthPicked = date_picked.month - 1
    dayPicked = date_picked.day - 15

    [xVal, yVal, colorVal], max_length_value, min_length_value, step = get_length_selection(monthPicked, dayPicked, selection, selectedRange)
    layout = go.Layout(
        title= 'Trip Length Distribution for selection:',
        bargap=0.1, #0.01
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=20, r=20, t=50, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            range=[min_length_value-0.5, max_length_value + 1.5],
            showgrid=False,
            nticks=max_length_value - min_length_value,
            fixedrange=True,
            title="Miles",
            #ticksuffix=":00",
        ),
        yaxis=dict(
            range=[0, max(yVal) + max(yVal) / 8],
            showticklabels=True,
            showgrid=True,
            fixedrange=True,
            rangemode="nonnegative",
            title="Number of rides",
            zeroline=False,
        ),
        annotations=[
            dict(
                x=xi,
                y=yi,
                text=str(yi),
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(color="white"),
            )
            for xi, yi in zip(xVal, yVal)
        ],
    )

    return go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=dict(color=colorVal), hoverinfo="x"),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal / 2,
                hoverinfo="none",
                mode="markers",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )


# Get the Coordinates of the chosen months, dates and times
def getLatLonColor(selectedData, month, day):
    listCoords = totalList[month][day]

    # No times selected, output all times for chosen month and date
    if selectedData is None or len(selectedData) is 0:
        return listCoords
    listStr = "listCoords["
    for time in selectedData:
        if selectedData.index(time) is not len(selectedData) - 1:
            listStr += "(totalList[month][day].index.hour==" + str(int(time)) + ") | "
        else:
            listStr += "(totalList[month][day].index.hour==" + str(int(time)) + ")]"
    return eval(listStr)
    
# Get the Coordinates of the chosen months, dates and fares range

def getLatLonFareColor2(listCoords, fareRange): 
#//TODO: Replace listStr logic to add "& (totalList[month][day].Fair >= value[0]) & ((totalList[month][day].Fair <= value[1])"
   
    # No fare selected, output all times for chosen month and date
    large_constant = 10000
    min_fare = fareRange[0]
    if fareRange[1] == 55:
        max_fare = large_constant
    else:
        max_fare = fareRange[1]
        
    if min_fare is 0 and max_fare is large_constant: 
    #//TODO: Why doesn't fareRange == [0,55] work?
        return listCoords
    listStr = "listCoords["
    for idx,fare in enumerate([min_fare, max_fare]):
        if idx is not len(fareRange) - 1:
            listStr += "(listCoords['Fare'].astype(float) >=" + str(float(fare)) + ") & "
        else:
            listStr += "(listCoords['Fare'].astype(float) <=" + str(float(fare)) + ") ] "
    return eval(listStr)
    
# Get the Coordinates of the chosen months, dates and fares range
# def getLatLonFareColor(selectedData, month, day, fareRange): 
    # listCoords = totalList[month][day]
    
    ###No fare selected, output all times for chosen month and date
    # large_constant = 10000
    # min_fare = fareRange[0]
    # if fareRange[1] == 55:
        # max_fare = large_constant
    # else:
        # max_fare = fareRange[1]
        
    # if selectedData is not None and len(selectedData)>0:
        # listStr = "listCoords["
        # for time in selectedData:
            # if selectedData.index(time) is not len(selectedData) - 1:
                # listStr += "(totalList[month][day].index.hour==" + str(int(time)) + "& listCoords['Fare'].astype(float) >=" + str(float(min_fare)) + " & listCoords['Fare'].astype(float) <=" + str(float(max_fare)) + ") | "
            # else:
                # listStr += "(totalList[month][day].index.hour==" + str(int(time)) + "& listCoords['Fare'].astype(float) >=" + str(float(min_fare)) + " & listCoords['Fare'].astype(float) <=" + str(float(max_fare)) + ") ] "
        # return eval(listStr)
    
    # if min_fare is 0 and max_fare is large_constant: 
    ###//TODO: Why doesn't fareRange == [0,55] work?
        # return listCoords
    # listStr = "listCoords["
    # for idx,fare in enumerate([min_fare, max_fare]):
        # if idx is not len(fareRange) - 1:
            # listStr += "(listCoords['Fare'].astype(float) >=" + str(float(fare)) + ") & "
        # else:
            # listStr += "(listCoords['Fare'].astype(float) <=" + str(float(fare)) + ") ] "
    # return eval(listStr)


# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph", "figure"),
    [
        Input("date-picker", "date"),
        Input("bar-selector", "value"),
        Input("location-dropdown", "value"),
        Input("PUDO-selector", "value"),
        Input('fare-slider', 'value')
        #Input("trip-selector", "value"),
    ],
)
def update_graph(datePicked, selectedData, selectedLocation, pudoSelection, selectedRange):
    zoom = 9.0
    latInitial = 41.867983
    lonInitial = -87.6315037
    bearing = 0

    if selectedLocation:
        zoom = 13.0
        latInitial = list_of_locations[selectedLocation]["lat"]
        lonInitial = list_of_locations[selectedLocation]["lon"]

    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    monthPicked = date_picked.month - 1
    dayPicked = date_picked.day - 15
    listCoords = getLatLonColor(selectedData, monthPicked, dayPicked)
    listCoords = getLatLonFareColor2(listCoords, selectedRange)
    
    if pudoSelection == "PU":
        lat = listCoords["Lat"]
        lon = listCoords["Lon"]
    elif pudoSelection == "DO":  
        lat = listCoords["DO_Lat"]
        lon = listCoords["DO_Lon"]
    else: #//TODO: one of the "PUDO" cases
        fromLat = listCoords[["Lat"]].to_numpy().astype(float).transpose()[0]
        toLat = listCoords[["DO_Lat"]].to_numpy().astype(float).transpose()[0]
        fromLon = listCoords[["Lon"]].to_numpy().astype(float).transpose()[0]
        toLon = listCoords[["DO_Lon"]].to_numpy().astype(float).transpose()[0]
        lat = listCoords["Lat"].append(listCoords["DO_Lat"])
        lon = listCoords["Lon"].append(listCoords["DO_Lon"])
        listCoords = listCoords.append(listCoords[["DO_Lat","DO_Lon","Hour"]].rename({'DO_Lat': 'Lat', 'DO_Lon': 'Lon'}, axis=1))

    data = [
            # Data for all rides based on date and time
            Scattermapbox(
                # lat=listCoords["Lat"],
                # lon=listCoords["Lon"],
                lat = lat,
                lon = lon,
                mode="markers",
                hoverinfo="lat+lon+text",
                text=listCoords.index.hour,
                marker=dict(
                    showscale=True,
                    color=np.append(np.insert(listCoords.index.hour, 0, 0), 23),
                    opacity=0.5,
                    size=7,
                    colorscale=[
                        [0, "#F4EC15"],
                        [0.04167, "#DAF017"],
                        [0.0833, "#BBEC19"],
                        [0.125, "#9DE81B"],
                        [0.1667, "#80E41D"],
                        [0.2083, "#66E01F"],
                        [0.25, "#4CDC20"],
                        [0.292, "#34D822"],
                        [0.333, "#24D249"],
                        [0.375, "#25D042"],
                        [0.4167, "#26CC58"],
                        [0.4583, "#28C86D"],
                        [0.50, "#29C481"],
                        [0.54167, "#2AC093"],
                        [0.5833, "#2BBCA4"],
                        [1.0, "#613099"],
                    ],
                    colorbar=dict(
                        title="Time of<br>Day",
                        x=0.93,
                        xpad=0,
                        nticks=12,
                        tickfont=dict(color="#d8d8d8"),
                        titlefont=dict(color="#d8d8d8"),
                        thicknessmode="pixels",
                    ),
                ),
            ),
            #//TODO: Find a way to dynamically add these Scattermapbox() fcns
            # go.Scattermapbox(
                # lat=[41.906920, 41.996920],
                # lon=[-87.693434, -87.603434],
                # mode="lines",
                # line=dict(width=2, color="#FF00FF")
            # ),
            # go.Scattermapbox(
                # lat=[41.906920, 41.996920],
                # lon=[-87.663434, -87.573434],
                # mode="lines",
                # line=dict(width=2, color="#FF00FF")
            # ),
            # Plot of important locations on the map
            Scattermapbox(
                lat=[list_of_locations[i]["lat"] for i in list_of_locations],
                lon=[list_of_locations[i]["lon"] for i in list_of_locations],
                mode="markers",
                hoverinfo="text",
                text=[i for i in list_of_locations],
                marker=dict(size=8, color="#ffa0a0"),
            ),
        ]
        
    #logic for dynamically creating lines for trip data.
    if pudoSelection == "PUDOTrips":
        idx = 0
        len_data = len(fromLat) # I really want the len(zip()) but that doesn't have length
        jump = max(1,len_data//100) #integer divison
        for from_lat,to_lat,from_lon,to_lon in zip(fromLat[::jump],toLat[::jump],fromLon[::jump],toLon[::jump]):
            if idx > len_data-1: break
            data.append(
            go.Scattermapbox(
                    # text=fromLat, #this definitely doesn't work.
                    # hoverinfo = "text",
                    lat=[from_lat, to_lat],
                    lon=[from_lon, to_lon],
                    mode="lines",
                    line=dict(width=2, color="#FF00FF")
                ))
            idx += jump
    return go.Figure(
        data=data,
        layout=Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=latInitial, lon=lonInitial),  # 40.7272  # -73.991251
                style="dark",
                bearing=bearing,
                zoom=zoom,
            ),
            updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": 9,
                                        "mapbox.center.lon": "-87.6315037",
                                        "mapbox.center.lat": "41.867983",
                                        "mapbox.bearing": 0,
                                        "mapbox.style": "dark",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )

# Update Fare Heat Map Graph based on date-picker
@app.callback(
    Output("heat-graph", "figure"),
    [
        Input("date-picker", "date"),
        Input("bar-selector", "value"),
        Input("location-dropdown", "value"),
        Input('fare-slider', 'value'), 
        Input('PUDO-selector', 'value'),
        #Input("trip-selector", "value"),
    ],
)
def update_graph(datePicked, selectedData, selectedLocation, selectedRange, pudoSelection):
    zoom = 9.0
    latInitial = 41.867983
    lonInitial = -87.6315037
    bearing = 0

    if selectedLocation:
        zoom = 13.0
        latInitial = list_of_locations[selectedLocation]["lat"]
        lonInitial = list_of_locations[selectedLocation]["lon"]
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    monthPicked = date_picked.month - 1
    dayPicked = date_picked.day - 15
    #try sequential
    listCoords = getLatLonColor(selectedData, monthPicked, dayPicked)
    listCoords = getLatLonFareColor2(listCoords, selectedRange)
    
    if pudoSelection == "PU":
        lat = listCoords["Lat"]
        lon = listCoords["Lon"]
    elif pudoSelection == "DO":  
        lat = listCoords["DO_Lat"]
        lon = listCoords["DO_Lon"]
    else: #one of the "PUDO" cases: w/ or w/o trip lines, this doesn't really matter for the markers.
        fromLat = listCoords[["Lat"]].to_numpy().astype(float).transpose()[0]
        toLat = listCoords[["DO_Lat"]].to_numpy().astype(float).transpose()[0]
        fromLon = listCoords[["Lon"]].to_numpy().astype(float).transpose()[0]
        toLon = listCoords[["DO_Lon"]].to_numpy().astype(float).transpose()[0]
        lat = listCoords["Lat"].append(listCoords["DO_Lat"])
        lon = listCoords["Lon"].append(listCoords["DO_Lon"])
        listCoords = listCoords.append(listCoords[["DO_Lat","DO_Lon","Fare"]].rename({'DO_Lat': 'Lat', 'DO_Lon': 'Lon'}, axis=1))
        
    data = [
            # Data for all rides based on date and time
            Scattermapbox(
                # lat=listCoords["Lat"],
                # lon=listCoords["Lon"],
                lat = lat,
                lon = lon,
                mode="markers",
                hoverinfo="text",
                # text=listCoords.index.hour,
                text=listCoords['Fare'],
                marker=dict(
                    showscale=True,
                    # color=np.append(np.insert(listCoords.index.hour, 0, 0), 50),
                    color=np.append(np.insert(listCoords[["Fare"]].to_numpy().astype(float).astype(int), 0, 0), 50),
                    opacity=0.5,
                    size=7,
                    colorscale=[
                        #Red Scheme
                        # [0, "#FFFFFF"],
                        # [0.05, "#FFCCCC"],
                        # [0.10, "#FFCCCC"],
                        # [0.15, "#FF9999"],
                        # [0.20, "#FF9999"],
                        # [0.25, "#FF6666"],
                        # [0.30, "#FF6666"],
                        # [0.35, "#FF3333"],
                        # [0.40, "#FF3333"],
                        # [0.45, "#FF0000"],
                        # [0.50, "#FF0000"],
                        # [0.55, "#CC0000"],
                        # [0.60, "#CC0000"],
                        # [0.65, "#990000"],
                        # [0.70, "#990000"],
                        # [0.75, "#660000"],
                        # [0.80, "#660000"],
                        # [0.85, "#330000"],
                        # [0.90, "#330000"],
                        # [0.95, "#000000"],
                        # [1.00, "#000000"],
                        #Green Scheme
                        [0, "#EAFAF1"],
                        [0.05, "#EAFAF1"],
                        [0.10, "#D4EFDF"],
                        [0.15, "#D4EFDF"],
                        [0.20, "#A9DFBF"],
                        [0.25, "#A9DFBF"],
                        [0.30, "#7DCEA0"],
                        [0.35, "#7DCEA0"],
                        [0.40, "#52BE80"],
                        [0.45, "#52BE80"],
                        [0.50, "#27AE60"],
                        [0.55, "#27AE60"],
                        [0.60, "#229954"],
                        [0.65, "#229954"],
                        [0.70, "#1E8449"],
                        [0.75, "#1E8449"],
                        [0.80, "#196F3D"],
                        [0.85, "#196F3D"],
                        [0.90, "#145A32"],
                        [0.95, "#145A32"],
                        [1.00, "#0B5345"],
                    ],
                    colorbar=dict(
                        title="Fare price",
                        x=0.93,
                        xpad=0,
                        nticks=20,
                        tickfont=dict(color="#d8d8d8"),
                        titlefont=dict(color="#d8d8d8"),
                        thicknessmode="pixels",
                    ),
                ),
            ),
            # Plot of important locations on the map
            Scattermapbox(
                lat=[list_of_locations[i]["lat"] for i in list_of_locations],
                lon=[list_of_locations[i]["lon"] for i in list_of_locations],
                mode="markers",
                hoverinfo="text",
                text=[i for i in list_of_locations],
                marker=dict(size=8, color="#FFFF00"),
            ),
        ]
        
    #logic for dynamically creating lines for trip data.
    if pudoSelection == "PUDOTrips":
        idx = 0
        len_data = len(fromLat) # I really want the len(zip()) but that doesn't have length
        jump = max(1,len_data//100) #integer divison
        for from_lat,to_lat,from_lon,to_lon in zip(fromLat[::jump],toLat[::jump],fromLon[::jump],toLon[::jump]):
            if idx > len_data-1: break
            data.append(
            go.Scattermapbox(
                    lat=[from_lat, to_lat],
                    lon=[from_lon, to_lon],
                    mode="lines",
                    line=dict(width=2, color="#FF00FF") #//TODO: relate color to fare price
                ))
            idx += jump
    
    return go.Figure(
        data= data,
        layout=Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=latInitial, lon=lonInitial),  # 40.7272  # -73.991251
                style="dark",
                bearing=bearing,
                zoom=zoom,
            ),
            updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": 9,
                                        "mapbox.center.lon": "-87.6315037",
                                        "mapbox.center.lat": "41.867983",
                                        "mapbox.bearing": 0,
                                        "mapbox.style": "dark",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )

@app.callback(
    Output('fare-slider', 'marks'),
    [Input('fare-slider', 'value')],
    [State('fare-slider', 'marks')]
)
def update_marks(vals, marks):
    for k in marks:
        if int(k) >= vals[0] and int(k) <= vals[1]:
            marks[k]['style']['color'] = 'green'
        else:
            marks[k]['style']['color'] = 'gray'
    return marks

@app.callback(
    Output('total-fare-range', 'children'),
    [Input("date-picker", "date"), Input('fare-slider', 'value')]
)
def update_total_fare_range(datePicked, vals):
    if vals[1] == 55:
        max_val = 10000 #some large constant
    else:
        max_val = vals[1]
    min_val = vals[0]
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    averageFareInSelection = 0
    totalInSelection = len(
        totalList[date_picked.month - 1][date_picked.day - 15][
            totalList[date_picked.month - 1][date_picked.day - 15]['Fare'].astype(float) <= float(max_val) 
        ]
        ) - len(
            totalList[date_picked.month - 1][date_picked.day - 15][
                totalList[date_picked.month - 1][date_picked.day - 15]['Fare'].astype(float) < float(min_val) 
            ]
        )
    return "Total rides in fare range: {:,d}".format(totalInSelection)

@app.callback(
    Output('selected-fare-range', 'children'),
    [Input("date-picker", "date"), Input('fare-slider', 'value'), Input("bar-selector", "value")]
)
def update_selected_fare_range(datePicked, vals, selection):
    if vals[1] == 55:
        max_val = 10000 #some large constant
    else:
        max_val = vals[1]
    min_val = vals[0]
    firstOutput = ""

    if selection is not None and len(selection) is not 0:
        date_picked = dt.strptime(datePicked, "%Y-%m-%d")
        totalInSelection = 0
        averageFareInSelection = 0
        for x in selection:
            totalInSelection += len(
                totalList[date_picked.month - 1][date_picked.day - 15][
                    (totalList[date_picked.month - 1][date_picked.day - 15].index.hour
                    == int(x)) & (totalList[date_picked.month - 1][date_picked.day - 15]['Fare'].to_numpy().astype(float) 
                    >= min_val) & (totalList[date_picked.month - 1][date_picked.day - 15]['Fare'].to_numpy().astype(float) 
                    <= max_val)
                ]
            )
            for idx, hr in enumerate(totalList[date_picked.month - 1][date_picked.day - 15]['Hour']):
                if int(hr) == int(x):
                    averageFareInSelection += float(totalList[date_picked.month - 1][date_picked.day - 15]['Fare'][idx])
        if selection: averageFareInSelection /= totalInSelection
        firstOutput = "Total rides in fare range with selected hours: {:,d}".format(totalInSelection)
    if (
        datePicked is None
        or selection is None
        or len(selection) is 24
        or len(selection) is 0
    ):
        return firstOutput
    return "Total rides in fare range with selected hours: {:,d}".format(totalInSelection)
    

if __name__ == "__main__":
    app.run_server(debug=True)
