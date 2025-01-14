# IMPORTS
import pandas as pd
import altair as alt
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# CONSTANTS
HEIGHT = 700

# LOADING DATA
econ_df = pd.read_csv('data/usGovernmentFinancialData.csv')

# DATA CREATION
econ_df['observation_date'] = pd.to_datetime(econ_df['observation_date'])
econ_df['net_income'] = econ_df['receipts'] - econ_df['expenditure']
econ_df['deficit_spending'] = (econ_df['receipts'] - econ_df['expenditure']) * -1
econ_df['interest_percent_of_gdp'] = econ_df['interest_expenditure']/econ_df['gdp'] * 100
econ_df['debt_percent_of_gdp'] = (econ_df['govt_debt']/1000)/econ_df['gdp'] * 100
econ_df['interest_percent_of_expenditure'] = econ_df['interest_expenditure']/econ_df['expenditure'] * 100
econ_df['projected_interest_payments'] = ((econ_df['fed_funds_rate']/100) * (econ_df['govt_debt']/1000))/econ_df['gdp'] * 100

# PAGE CONFIG
st.set_page_config(page_title="Government Debt and Spending Data", layout="wide")

# WIDGETS
st.logo(image="images/treasury.jpg", 
        icon_image="images/treasury.jpg")

# SEABORN
sns.set_theme()

# SIDEBAR
with st.sidebar:
    st.title("Government Debt and Spending Data")
    st.header("⚙️ Settings")
    
    min_date = econ_df['observation_date'].min().date()
    max_date = econ_df['observation_date'].max().date()
    default_start_date = min_date
    default_end_date = max_date
    start_date = st.date_input("Start date", default_start_date, min_value=econ_df['observation_date'].min().date(), max_value=max_date)
    end_date = st.date_input("End date", default_end_date, min_value=econ_df['observation_date'].min().date(), max_value=max_date)

# CHARTS
def chart(metric, title, chart_type):
    df_display = econ_df.set_index('observation_date')
    mask = (df_display.index >= pd.Timestamp(start_date)) & (df_display.index <= pd.Timestamp(end_date))
    df_filtered = df_display.loc[mask].reset_index()
    
    if chart_type == "Altair":
        st.write(title + " Over Time")
        chart = alt.Chart(df_filtered).mark_line().encode(
            x=alt.X('observation_date:T', title='Date'),
            y=alt.Y(metric, title=title),
        ).properties(
            height=700
        )
        st.altair_chart(chart, use_container_width=True)
    elif chart_type == "Seaborn":
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_filtered, x='observation_date', y=metric)
        plt.title(title + " Over Time")
        plt.xlabel('Date')
        plt.ylabel(title)
        plt.xticks(rotation=45)
        st.pyplot(plt)

# SIDEBAR
chart_type = st.sidebar.selectbox("Select Chart Type", ["Altair", "Seaborn"])

pages = {
    "Gross Domestic Product": lambda: chart("gdp", "GDP (Billions of Dollars)", chart_type),
    "Deficit Spending": lambda: chart("deficit_spending", "Deficit Spending (Billions of Dollars)", chart_type),
    "Interest Percent of GDP": lambda: chart("interest_percent_of_gdp", "Interest Percent of GDP", chart_type),
    "Debt Percent of GDP": lambda: chart("debt_percent_of_gdp", "Debt Percent of GDP", chart_type),
    "Interest Percent of Expenditure": lambda: chart("interest_percent_of_expenditure", "Interest Percent of Expenditure", chart_type)
}

demo = st.sidebar.selectbox("Chart", options=pages.keys(), format_func=lambda x: str(x))
pages[demo]()