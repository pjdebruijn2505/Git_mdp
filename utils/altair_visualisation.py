# Simple class that can create interactive plots using the vega Altair package. Currently only a scatterplot is implemented
# but in more methods can easily be added to the class if desired. 

import altair as alt
import pandas as pd

class Graph_tana():
    def __init__(self, dataset):
        self.dataset = dataset
    
    # Method that creates scatterplot of the waterlevel based on warning level (specified water level in which it is
    # known that floods can occur, and a time period to plot. ß
    
    def scatterplot_waterlevel(self, start_date, end_date, warning_level, y_axis_name):
        alt.data_transformers.enable("vegafusion")
        interval = alt.selection_interval(encodings=['x'], empty=True)

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        date_filter = self.dataset[(self.dataset['date'] >= start_date) & (self.dataset['date'] <= end_date)]

        # Create the base chart
        base = alt.Chart(date_filter).mark_circle(size=10).encode(
            x='date:T',
            y=f'{y_axis_name}:Q',
            tooltip=['date:T', 'waterlevel(m):Q'],
            color=alt.condition(
                alt.datum['waterlevel(m)'] > warning_level,
                alt.value('red'),
                alt.value('blue')
            )
        ).properties(
            width=800,
            height=400
        ).add_params(interval)

        chart = base.interactive()

        return chart
