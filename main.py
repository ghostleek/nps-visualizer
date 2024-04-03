import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Function to process and transform the data


def process_data(data, period='M'):
    # Convert 'timestamp' to datetime
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Categorize NPS responses
    conditions = [
        (data['nps'] <= 6),  # Detractors
        (data['nps'] >= 9),  # Promoters
        (data['nps'].between(7, 8)),  # Passives
    ]
    choices = ['detractor', 'promoter', 'passive']
    data['category'] = np.select(conditions, choices, default='unknown')

    # Group by selected period
    data.set_index('timestamp', inplace=True)
    grouped = data.groupby(
        [pd.Grouper(freq=period), 'category']).size().unstack(fill_value=0)
    grouped['total'] = grouped.sum(axis=1)
    grouped = grouped.div(grouped['total'], axis=0) * \
        100  # Convert to percentage

    # Reset index for Plotly
    grouped.reset_index(inplace=True)
    return grouped.melt(id_vars=['timestamp', 'total'], var_name='category', value_name='percentage')

# Function to plot the data with Plotly


def plot_data(grouped):
    fig = px.bar(grouped, x='timestamp', y='percentage', color='category', text='percentage',
                 hover_data=['total'], labels={'timestamp': 'Date'}, title='NPS Score Distribution Over Time')
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='inside')
    fig.update_layout(barmode='stack', xaxis={
                      'categoryorder': 'total descending'})
    return fig


# Streamlit UI
st.title('NPS Score Visualization')
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, usecols=['timestamp', 'nps'])

    # Period selection
    period = st.selectbox('Select the period to group by:',
                          ('W', 'M', 'Q', 'Y'),
                          format_func=lambda x: {'W': 'Week', 'M': 'Month', 'Q': 'Quarter', 'Y': 'Year'}[x])

    processed_data = process_data(data, period)
    fig = plot_data(processed_data)
    st.plotly_chart(fig, use_container_width=True)
