import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
import plotly as py

st.title("Product Relationships Analysis")

@st.cache
def load_data(category, x):
    data = pd.read_csv('relationship.csv')
    data = data[data['lift'] >= x]
    data = data[['item_A','freqAB','confidenceAtoB','confidenceBtoA','lift','Product_Relationship']]
    data = data[data['Product_Relationship']==category]
    return data

category = st.sidebar.selectbox(
    'Relationship',
    ('Positive Relationship', 'Negative Relationship')
)

x = st.sidebar.number_input('lift score', 0.0, 20.0, 10.0)

st.subheader("Relationship Table")
data = load_data(category, x)
count = data['item_A'].count()
freq_Ave = data['freqAB'].mean()

data
st.write('Count Products %i' % count)
st.write('Average times in basket together %i' % freq_Ave)

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write(data)
