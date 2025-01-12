# IMPORTS
import pandas as pd
import altair as alt
import streamlit as st

# LOADING DATA
econ_df = pd.read_csv('data/CombinedData.csv')

# DATA CREATION
econ_df['net_income'] = econ_df['receipts'] - econ_df['expenditure']
econ_df['deficit_spending'] = (econ_df['receipts'] - econ_df['expenditure']) * -1
econ_df['interest_percent_of_gdp'] = econ_df['interest_expenditure']/econ_df['gdp'] * 100
econ_df['debt_percent_of_gdp'] = (econ_df['govt_debt']/1000)/econ_df['gdp'] * 100
econ_df['interest_percent_of_expenditure'] = econ_df['interest_expenditure']/econ_df['expenditure'] * 100
econ_df['projected_interest_payments'] = ((econ_df['fed_funds_rate']/100) * (econ_df['govt_debt']/1000))/econ_df['gdp'] * 100

# CHARTS
def gdp():
    st.write("""
    # GDP
    """)
    chart = alt.Chart(econ_df).mark_line().encode(
        x=alt.X('observation_date:T', title='Date'),
        y=alt.Y('gdp:Q', title='GDP (Billions of Dollars)')
    )
    st.altair_chart(chart, use_container_width=True)

def deficit_spending_chart():
    st.write("""
    # Deficit Spending
    """)
    chart = alt.Chart(econ_df).mark_line().encode(
        x=alt.X('observation_date:T', title='Date'),
        y=alt.Y('deficit_spending:Q', title='Deficit Spending (Billions of Dollars)')
    )
    st.altair_chart(chart, use_container_width=True)

def interest_percent_of_gdp_chart():
    st.write("""
    # Interest Payments as Percent of GDP
    """)
    chart = alt.Chart(econ_df).mark_line().encode(
        x=alt.X('observation_date:T', title='Date'),
        y=alt.Y('interest_percent_of_gdp:Q', title='Interest Percent of GDP')
    )
    st.altair_chart(chart, use_container_width=True)

def debt_percent_of_gdp_chart():
    st.write("""
    # Debt as Percent of GDP
    """)
    chart = alt.Chart(econ_df).mark_line().encode(
        x=alt.X('observation_date:T', title='Date'),
        y=alt.Y('debt_percent_of_gdp:Q', title='Debt Percent of GDP')
    )
    st.altair_chart(chart, use_container_width=True)

def interest_percent_of_expenditure_chart():
    st.write("""
    # Interest Payments as Percent of Expenditure
    """)
    chart = alt.Chart(econ_df).mark_line().encode(
        x=alt.X('observation_date:T', title='Date'),
        y=alt.Y('interest_percent_of_expenditure:Q', title='Interest Percent of Expenditure')
    )
    st.altair_chart(chart, use_container_width=True)

# SIDEBAR
pages = {
    "Gross Domestic Product": gdp,
    "Deficit Spending": deficit_spending_chart,
    "Interest Percent of GDP": interest_percent_of_gdp_chart,
    "Debt Percent of GDP": debt_percent_of_gdp_chart,
    "Interest Percent of Expenditure": interest_percent_of_expenditure_chart
}

demo = st.sidebar.selectbox("Chart", options=pages.keys(), format_func=lambda x: str(x))
pages[demo]()