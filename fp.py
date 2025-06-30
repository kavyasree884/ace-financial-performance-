


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# --- Page Configuration (Attractive Theme & Icon) ---
st.set_page_config(
    page_title="Financial Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    # You can choose 'light' or 'dark' theme. 'dark' often looks more modern.
    # For custom themes, you'd define them in config.toml or via st.markdown(unsafe_allow_html=True) with CSS
    theme='dark',
    icon="📈" # Adding a page icon
)

# --- Load Data (Now reading from CSV) ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("financial_data.csv")
        
        # --- Data Preparation ---
        df.columns = df.columns.str.strip()
        
        currency_cols = ['Units Sold', 'Manufacturing Price', 'Sale Price', 
                         'Gross Sales', 'Discounts', 'Sales', 'COGS', 'Profit']
        
        for col in currency_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        
        df['Year'] = df['Date'].dt.year
        df['Month Name'] = df['Date'].dt.month_name()
        df['Quarter'] = df['Date'].dt.quarter.apply(lambda x: f'Qtr {x}')

        df['Profit Margin'] = df['Profit'] / df['Sales'].replace(0, pd.NA)
        df['Total Discounts'] = df['Discounts'].abs()
        df['Total Revenue (Gross Sales)'] = df['Gross Sales']
        df['COGS to Sales'] = df['COGS'] / df['Sales'].replace(0, pd.NA)
        df['Net Sales'] = df['Gross Sales'] - df['Total Discounts']

        df['Profit Margin'].fillna(0, inplace=True)
        df['COGS to Sales'].fillna(0, inplace=True)

        return df
    except FileNotFoundError:
        st.error("Dataset file 'financial_data.csv' not found. Please ensure it's in the correct directory.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading or processing data: {e}")
        st.stop()

df = load_data()

# Initialize session state for filters
if 'selected_countries' not in st.session_state:
    st.session_state.selected_countries = df['Country'].unique().tolist()
if 'selected_segments' not in st.session_state:
    st.session_state.selected_segments = df['Segment'].unique().tolist()
if 'selected_years' not in st.session_state:
    st.session_state.selected_years = sorted(df['Year'].unique().tolist())
if 'selected_quarters' not in st.session_state:
    st.session_state.selected_quarters = sorted(df['Quarter'].unique().tolist())
if 'date_range' not in st.session_state:
    st.session_state.date_range = (df['Date'].min().date(), df['Date'].max().date())

# --- Sidebar Filters ---
st.sidebar.header("📊 Filter Options")

all_countries = df['Country'].unique().tolist()
st.session_state.selected_countries = st.sidebar.multiselect(
    "🌍 Select Country", all_countries, default=st.session_state.selected_countries
)

all_segments = df['Segment'].unique().tolist()
st.session_state.selected_segments = st.sidebar.multiselect(
    "👥 Select Segment", all_segments, default=st.session_state.selected_segments
)

all_years = sorted(df['Year'].unique().tolist())
st.session_state.selected_years = st.sidebar.multiselect(
    "📅 Select Year", all_years, default=st.session_state.selected_years
)

all_quarters = sorted(df['Quarter'].unique().tolist())
st.session_state.selected_quarters = st.sidebar.multiselect(
    "🗓️ Select Quarter", all_quarters, default=st.session_state.selected_quarters
)

min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
st.session_state.date_range = st.sidebar.date_input(
    "📆 Select Date Range", value=st.session_state.date_range, min_value=min_date, max_value=max_date
)

# Reset Filters Button
if st.sidebar.button("🔄 Reset All Filters"):
    st.session_state.selected_countries = all_countries
    st.session_state.selected_segments = all_segments
    st.session_state.selected_years = all_years
    st.session_state.selected_quarters = all_quarters
    st.session_state.date_range = (min_date, max_date)
    st.experimental_rerun()

# Filter data based on selections
if isinstance(st.session_state.date_range, tuple) and len(st.session_state.date_range) == 2:
    start_date, end_date = st.session_state.date_range
else: 
    start_date = st.session_state.date_range[0]
    end_date = st.session_state.date_range[0]

filtered_df = df[
    (df['Country'].isin(st.session_state.selected_countries)) &
    (df['Segment'].isin(st.session_state.selected_segments)) &
    (df['Year'].isin(st.session_state.selected_years)) &
    (df['Quarter'].isin(st.session_state.selected_quarters)) &
    (df['Date'].dt.date >= start_date) &
    (df['Date'].dt.date <= end_date)
]

# --- Main Dashboard ---
st.title("🌟 Financial Performance Dashboard 💰")
st.markdown("An interactive dashboard to analyze financial performance across different dimensions.")

# --- Key Performance Indicators (KPIs) ---
st.markdown("## ✨ Key Financial Metrics Overview")
col1, col2, col3, col4, col5 = st.columns(5)

if not filtered_df.empty:
    with col1:
        total_sales = filtered_df['Sales'].sum()
        st.metric(label="Total Sales", value=f"${total_sales:,.2f}")

    with col2:
        total_gross_sales = filtered_df['Gross Sales'].sum()
        st.metric(label="Total Gross Sales", value=f"${total_gross_sales:,.2f}")

    with col3:
        total_profit = filtered_df['Profit'].sum()
        st.metric(label="Total Profit", value=f"${total_profit:,.2f}")

    with col4:
        gross_profit = filtered_df['Gross Sales'].sum() - filtered_df['COGS'].sum()
        st.metric(label="Gross Profit", value=f"${gross_profit:,.2f}")
    
    with col5:
        net_profit_calc = filtered_df['Profit'].sum() - filtered_df['Total Discounts'].sum()
        st.metric(label="Net Profit", value=f"${net_profit_calc:,.2f}")
else:
    st.warning("⚠️ No data available for the selected filters. Please adjust your selections.")


# --- Profit and Loss Statement (Table) ---
st.markdown("---")
st.markdown("## 📋 Profit and Loss Statement Summary")

if not filtered_df.empty:
    pnl_data = {}
    years_in_data = sorted(filtered_df['Year'].unique())
    
    for year in years_in_data:
        year_df = filtered_df[filtered_df['Year'] == year]
        pnl_data[year] = {
            'Sales': year_df['Sales'].sum(),
            'Cost of Sales': year_df['COGS'].sum(),
            'Gross Profit': year_df['Gross Sales'].sum() - year_df['COGS'].sum(),
            'Operating Expenses': year_df['Operating Expenses'].sum() if 'Operating Expenses' in year_df.columns else 0,
            'EBITDA': year_df['Profit'].sum(), 
            'Operating Profit': year_df['Profit'].sum(), 
            'Net Profit': year_df['Profit'].sum() - year_df['Total Discounts'].sum()
        }
    
    pnl_df = pd.DataFrame(pnl_data).rename_axis('Account').reset_index()
    pnl_df_styled = pnl_df.style.format(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x)
    st.dataframe(pnl_df_styled, use_container_width=True)
else:
    st.info("ℹ️ No data to display Profit and Loss Statement for the selected filters.")

# --- Visualizations ---
st.markdown("---")

col_vis1, col_vis2 = st.columns(2)

with col_vis1:
    st.markdown("### 📈 Sales | Gross Profit | Net Profit Trend Over Time")
    if not filtered_df.empty:
        sales_profit_over_time = filtered_df.groupby('Year')[['Sales', 'Gross Sales', 'Profit']].sum().reset_index()
        fig_line = px.line(sales_profit_over_time, x='Year', y=['Sales', 'Gross Sales', 'Profit'],
                          title='Sales, Gross Profit, and Net Profit Trend Over Time',
                          labels={'value': 'Amount ($)', 'variable': 'Metric'},
                          color_discrete_sequence=px.colors.qualitative.Bold) # Bold color palette
        fig_line.update_layout(hovermode="x unified")
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("ℹ️ No data for Sales, Gross Profit, Net Profit Trend Over Time.")

with col_vis2:
    st.markdown("### 🗺️ Sales | GP | NP by Country")
    if not filtered_df.empty:
        sales_profit_by_country = filtered_df.groupby('Country')[['Sales', 'Gross Sales', 'Profit']].sum().reset_index()
        fig_bar_country = px.bar(sales_profit_by_country, x='Country', y=['Sales', 'Gross Sales', 'Profit'],
                                 barmode='group',
                                 title='Sales, Gross Profit, and Net Profit by Country',
                                 labels={'value': 'Amount ($)', 'variable': 'Metric'},
                                 color_discrete_sequence=px.colors.qualitative.Pastel) # Pastel color palette
        st.plotly_chart(fig_bar_country, use_container_width=True)
    else:
        st.info("ℹ️ No data for Sales, GP, NP by Country.")

st.markdown("---")

col_vis3, col_vis4 = st.columns(2)

with col_vis3:
    st.markdown("### 📊 Gross Profit | EBITDA | Operating Profit Trend")
    if not filtered_df.empty:
        kpi_trend = filtered_df.groupby('Year').agg(
            {'Gross Sales': 'sum', 'COGS': 'sum', 'Profit': 'sum'}
        ).reset_index()
        kpi_trend['Gross Profit'] = kpi_trend['Gross Sales'] - kpi_trend['COGS']
        kpi_trend['EBITDA'] = kpi_trend['Profit'] 
        kpi_trend['Operating Profit'] = kpi_trend['Profit'] 

        fig_kpi_trend = px.area(kpi_trend, x='Year', y=['Gross Profit', 'EBITDA', 'Operating Profit'],
                                title='Gross Profit, EBITDA, Operating Profit Trend',
                                labels={'value': 'Amount ($)', 'variable': 'Metric'},
                                color_discrete_sequence=px.colors.qualitative.G10) # G10 color palette
        st.plotly_chart(fig_kpi_trend, use_container_width=True)
    else:
        st.info("ℹ️ No data for Gross Profit, EBITDA, Operating Profit Trend.")

with col_vis4:
    st.markdown("### 📉 Sales and Marketing Expenses Trend")
    if not filtered_df.empty and 'Operating Expenses' in filtered_df.columns and not filtered_df['Operating Expenses'].isnull().all():
        expenses_over_time = filtered_df.groupby('Year')['Operating Expenses'].sum().reset_index()
        fig_expenses = px.area(expenses_over_time, x='Year', y='Operating Expenses',
                               title='Sales and Marketing Expenses Over Time',
                               labels={'Operating Expenses': 'Amount ($)'},
                               color_discrete_sequence=['firebrick']) # A distinct red for expenses
        st.plotly_chart(fig_expenses, use_container_width=True)
    else:
        st.info("ℹ️ No 'Operating Expenses' data to display Sales and Marketing Expenses.")

st.markdown("---")

st.markdown("### 🏷️ Gross Sales vs Discounts (Scatter Plot)")
if not filtered_df.empty:
    fig_scatter = px.scatter(filtered_df, x='Gross Sales', y='Discounts',
                             color='Product',
                             size='Sales', 
                             hover_data=['Country', 'Segment'],
                             title='Gross Sales vs Discounts by Product',
                             labels={'Gross Sales': 'Gross Sales ($)', 'Discounts': 'Discounts ($)'},
                             color_discrete_sequence=px.colors.qualitative.Set2) # Another qualitative palette
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("ℹ️ No data for Gross Sales vs Discounts Scatter Plot.")

st.markdown("---")

st.markdown("### 🔥 Sales by Product and Discount Band (Heat Map)")
if not filtered_df.empty:
    heatmap_data = filtered_df.pivot_table(index='Product', columns='Discount Band', values='Sales', aggfunc='sum')
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=.5, linecolor='black') # YlGnBu is a good sequential cmap
    plt.title('Sales by Product and Discount Band', fontsize=16)
    plt.xlabel('Discount Band', fontsize=12)
    plt.ylabel('Product', fontsize=12)
    st.pyplot(plt)
else:
    st.info("ℹ️ No data for Sales by Product and Discount Band Heat Map.")

# --- Financial Performance Enhancement Tips ---
st.markdown("---")
st.markdown("## 💡 Financial Performance Enhancement Tips :bulb:")

with st.expander("Click to view actionable tips"):
    st.markdown("""
    Here are some general strategies and tips that can help improve financial performance based on common business analysis:

    ### 📈 **Revenue Growth Strategies:**
    * **Expand Market Reach:** Explore new countries or segments that show high potential for your products.
    * **Product Diversification:** Introduce new products or enhance existing ones to meet evolving customer needs.
    * **Pricing Optimization:** Regularly review and adjust pricing strategies to ensure competitiveness and maximize revenue without alienating customers.
    * **Upselling/Cross-selling:** Encourage customers to purchase higher-value items or complementary products.

    ### 💰 **Profitability Improvement:**
    * **Cost of Goods Sold (COGS) Reduction:** Negotiate better deals with suppliers, optimize manufacturing processes, or explore alternative, cheaper raw materials without compromising quality.
    * **Improve Efficiency:** Streamline operations to reduce waste and increase productivity, which directly impacts profit margins.
    * **Strategic Discounting:** Analyze the "Sales by Product and Discount Band" heatmap carefully. Are high discounts truly driving proportionally higher sales and profit? If not, re-evaluate your discount strategy to protect margins.
    * **Focus on High-Profit Products/Segments:** Identify your most profitable products and segments and allocate more resources to them.

    ### 💸 **Cost Optimization:**
    * **Operating Expense Review:** Regularly audit your operating expenses (e.g., Sales and Marketing Expenses, Administrative Costs) to identify areas for reduction without impacting core business functions.
    * **Technology Adoption:** Invest in technologies that automate tasks, reduce manual labor, and improve overall efficiency, leading to long-term cost savings.
    * **Energy Efficiency:** Implement energy-saving measures to reduce utility costs.

    ### 📊 **Data-Driven Decision Making:**
    * **Continuous Monitoring:** Regularly review this dashboard to identify trends, opportunities, and potential issues early.
    * **Variance Analysis:** Compare actual performance against budgeted or previous period's performance to understand deviations and their causes.
    * **Customer Lifetime Value (CLTV):** Focus on retaining high-value customers, as customer acquisition can be more expensive than retention.

    By consistently applying these principles and leveraging the insights from this dashboard, you can drive sustainable financial growth and improve overall business health.
    """)


# --- Information/About Section ---
st.markdown("---")
st.markdown("### ℹ️ About This Dashboard")
st.info("""
This dashboard is developed as part of a Business Analyst project to visualize and analyze financial performance.
It leverages Streamlit for interactive web application development and Plotly/Matplotlib/Seaborn for rich data visualizations.
The goal is to provide comprehensive insights into sales, profit, and costs across various dimensions like country, segment, and time.
""")

st.markdown("---")
st.markdown("Developed by: Your Name/Unified Mentor")
st.markdown("Project Difficulty Level: Intermediate")
