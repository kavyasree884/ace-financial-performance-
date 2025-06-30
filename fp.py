import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------
# Load your data (replace with your actual data source)
# ----------------------------------------
# Note: .twbx files are Tableau Packaged Workbooks and can't be read directly by pandas.
# You need to export the underlying data to CSV/Excel first.
# For this template, I'll assume you have a CSV exported.
# Example: financial_data.csv

# Replace this with your exported CSV file
df = pd.read_csv('financial_data.csv')

# ----------------------------------------
# Sidebar Filters
# ----------------------------------------
st.sidebar.title("Filters")
region = st.sidebar.multiselect(
    "Select Region", options=df['Region'].unique(), default=df['Region'].unique())
country = st.sidebar.multiselect(
    "Select Country", options=df['Country'].unique(), default=df['Country'].unique())
quarter = st.sidebar.multiselect(
    "Select Quarter", options=df['Quarter'].unique(), default=df['Quarter'].unique())
year = st.sidebar.multiselect(
    "Select Year", options=df['Year'].unique(), default=df['Year'].unique())

# Filter the dataframe
df_filtered = df[
    (df['Region'].isin(region)) &
    (df['Country'].isin(country)) &
    (df['Quarter'].isin(quarter)) &
    (df['Year'].isin(year))
]

# ----------------------------------------
# KPI Metrics
# ----------------------------------------
gross_profit = df_filtered['Gross Profit'].sum()
ebitda = df_filtered['EBITDA'].sum()
operating_profit = df_filtered['Operating Profit'].sum()
pbit = df_filtered['PBIT'].sum()
net_profit = df_filtered['Net Profit'].sum()

st.title("Financial Performance Dashboard")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric(label="Gross Profit", value=f"${gross_profit:,.0f}")
kpi2.metric(label="EBITDA", value=f"${ebitda:,.0f}")
kpi3.metric(label="Operating Profit", value=f"${operating_profit:,.0f}")
kpi4.metric(label="PBIT", value=f"${pbit:,.0f}")
kpi5.metric(label="Net Profit", value=f"${net_profit:,.0f}")

# ----------------------------------------
# Charts
# ----------------------------------------

# Sales, Gross Profit, Net Profit over time
fig1 = px.bar(df_filtered, x="Month", y=["Sales", "Gross Profit", "Net Profit"],
              barmode='group', title="Sales | Gross Profit | Net Profit")
st.plotly_chart(fig1, use_container_width=True)

# Sales Margin chart
fig2 = px.line(df_filtered, x="Month", y=["GP Margin", "NP Margin"],
               title="Sales | GP Margin | NP Margin")
st.plotly_chart(fig2, use_container_width=True)

# Gross Profit, EBITDA, Operating Profit over time
fig3 = px.area(df_filtered, x="Month", y=[
               "Gross Profit", "EBITDA", "Operating Profit"], title="Gross Profit | EBITDA | Operating Profit")
st.plotly_chart(fig3, use_container_width=True)

# Sales & Marketing Expenses
fig4 = px.area(df_filtered, x="Month", y=[
               "Sales Expenses", "Marketing Expenses"], title="Sales and Marketing Expenses")
st.plotly_chart(fig4, use_container_width=True)

# ----------------------------------------
# Profit and Loss Statement Table
# ----------------------------------------
st.subheader("Profit and Loss Statement")
st.dataframe(df_filtered)

