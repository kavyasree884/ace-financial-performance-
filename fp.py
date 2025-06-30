import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(
    page_title="Financial Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Data (replace with your actual data loading) ---
@st.cache_data
def load_data():
    # Replace with the actual path to your dataset
    df = pd.read_excel("your_financial_data.xlsx")
    # Data Cleaning and Type Conversion
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month Name'] = df['Date'].dt.month_name()
    # Add calculated fields
    df['Profit Margin'] = df['Profit'] / df['Sales']
    df['Total Discounts'] = df['Discounts']
    df['COGS to Sales'] = df['COGS'] / df['Sales']
    # Handle potential division by zero
    df['Profit Margin'].fillna(0, inplace=True)
    df['COGS to Sales'].fillna(0, inplace=True)
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")

all_countries = df['Country'].unique().tolist()
selected_countries = st.sidebar.multiselect("Select Country", all_countries, default=all_countries)

all_segments = df['Segment'].unique().tolist()
selected_segments = st.sidebar.multiselect("Select Segment", all_segments, default=all_segments)

all_years = sorted(df['Year'].unique().tolist())
selected_years = st.sidebar.multiselect("Select Year", all_years, default=all_years)

# Assuming you have Quarter information or can derive it
# For simplicity, let's assume 'Quarter' column exists or derive from 'Date'
# df['Quarter'] = df['Date'].dt.quarter.apply(lambda x: f'Qtr {x}')
# all_quarters = sorted(df['Quarter'].unique().tolist())
# selected_quarters = st.sidebar.multiselect("Select Quarter", all_quarters, default=all_quarters)

# Date Range Filter
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input("Select Date Range", value=(min_date, max_date))

# Filter data based on selections
filtered_df = df[
    (df['Country'].isin(selected_countries)) &
    (df['Segment'].isin(selected_segments)) &
    (df['Year'].isin(selected_years)) &
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1])
]

# Reset Filters Button
if st.sidebar.button("Reset Filters"):
    st.session_state.selected_countries = all_countries
    st.session_state.selected_segments = all_segments
    st.session_state.selected_years = all_years
    st.session_state.date_range = (min_date, max_date)
    st.experimental_rerun() # Rerun the app to apply default filters

# --- Main Dashboard ---
st.title("Financial Performance Dashboard :money_with_wings:")

# --- KPI Section ---
st.markdown("## Key Financial Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_sales = filtered_df['Sales'].sum()
    st.metric(label="Total Sales", value=f"${total_sales:,.2f}")

with col2:
    total_profit = filtered_df['Profit'].sum()
    st.metric(label="Total Profit", value=f"${total_profit:,.2f}")

with col3:
    total_cogs = filtered_df['COGS'].sum()
    st.metric(label="Total COGS", value=f"${total_cogs:,.2f}")

with col4:
    gross_profit = filtered_df['Gross Sales'].sum() - filtered_df['COGS'].sum()
    st.metric(label="Gross Profit", value=f"${gross_profit:,.2f}")

with col5:
    net_profit = filtered_df['Net Profit'].sum() if 'Net Profit' in filtered_df.columns else filtered_df['Profit'].sum() - filtered_df['Discounts'].sum()
    st.metric(label="Net Profit", value=f"${net_profit:,.2f}")


# --- Profit and Loss Statement (Table) ---
st.markdown("## Profit and Loss Statement")
# This part would require more complex aggregation and pivoting for a full P&L
# For a simplified version, you can show a summary table
pnl_summary = filtered_df.groupby('Year')[['Sales', 'Cost of Sales', 'Operating Expenses', 'Profit', 'Net Profit']].sum().T
st.dataframe(pnl_summary.style.format("${:,.2f}"))


# --- Visualizations ---
st.markdown("---")

col_vis1, col_vis2 = st.columns(2)

with col_vis1:
    st.markdown("### Sales, Gross Profit, Net Profit by Year")
    # Aggregate data for line chart
    sales_profit_over_time = filtered_df.groupby('Year')[['Sales', 'Gross Sales', 'Profit']].sum().reset_index()
    fig_line = px.line(sales_profit_over_time, x='Year', y=['Sales', 'Gross Sales', 'Profit'],
                      title='Sales, Gross Profit, and Net Profit Trend Over Time',
                      labels={'value': 'Amount ($)', 'variable': 'Metric'})
    fig_line.update_layout(hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

with col_vis2:
    st.markdown("### Gross Profit | EBITDA | Operating Profit")
    # This would require more specific data columns for EBITDA and Operating Profit
    # Assuming for demonstration, we will use simplified aggregations
    kpi_agg = filtered_df.groupby('Year').agg(
        {'Gross Sales': 'sum', 'Discounts': 'sum', 'COGS': 'sum', 'Profit': 'sum'}
    ).reset_index()
    kpi_agg['Gross Profit'] = kpi_agg['Gross Sales'] - kpi_agg['COGS']
    # You would calculate EBITDA and Operating Profit based on your specific P&L structure
    # For now, let's use Gross Profit as an example
    fig_bar_kpi = px.bar(kpi_agg, x='Year', y=['Gross Profit', 'Profit'],
                         title='Gross Profit and Profit by Year',
                         labels={'value': 'Amount ($)', 'variable': 'Metric'})
    st.plotly_chart(fig_bar_kpi, use_container_width=True)

st.markdown("---")

col_vis3, col_vis4 = st.columns(2)

with col_vis3:
    st.markdown("### Sales, Gross Profit, Net Profit by Region")
    sales_by_region = filtered_df.groupby('Region')[['Sales', 'Gross Sales', 'Profit']].sum().reset_index()
    fig_region_bar = px.bar(sales_by_region, x='Region', y=['Sales', 'Gross Sales', 'Profit'],
                            barmode='group', title='Sales, Gross Profit, Net Profit by Region')
    st.plotly_chart(fig_region_bar, use_container_width=True)

with col_vis4:
    st.markdown("### Sales by Product and Discount Band (Heat Map)")
    # Pivot data for heatmap
    heatmap_data = filtered_df.pivot_table(index='Product', columns='Discount Band', values='Sales', aggfunc='sum')
    fig_heatmap, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax)
    plt.title('Sales by Product and Discount Band')
    plt.xlabel('Discount Band')
    plt.ylabel('Product')
    st.pyplot(fig_heatmap, use_container_width=True)

st.markdown("---")

st.markdown("### Sales and Marketing Expenses")
# Assuming you have a way to categorize expenses as "Sales and Marketing"
# For demonstration, let's just plot 'Operating Expenses' if available or a generic expense category
if 'Operating Expenses' in filtered_df.columns:
    expenses_over_time = filtered_df.groupby('Year')['Operating Expenses'].sum().reset_index()
    fig_expenses = px.area(expenses_over_time, x='Year', y='Operating Expenses',
                           title='Operating Expenses Over Time')
    st.plotly_chart(fig_expenses, use_container_width=True)
else:
    st.info("No 'Operating Expenses' column found to display Sales and Marketing Expenses.")
