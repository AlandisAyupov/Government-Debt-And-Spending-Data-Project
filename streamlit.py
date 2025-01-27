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
econ_df['govt_debt'] = econ_df['govt_debt']/1000
econ_df['net_income'] = econ_df['receipts'] - econ_df['expenditure']
econ_df['deficit_spending'] = (econ_df['receipts'] - econ_df['expenditure']) * -1
econ_df['interest_percent_of_gdp'] = econ_df['interest_expenditure']/econ_df['gdp'] * 100
econ_df['debt_percent_of_gdp'] = (econ_df['govt_debt'])/econ_df['gdp'] * 100
econ_df['interest_percent_of_expenditure'] = econ_df['interest_expenditure']/econ_df['expenditure'] * 100
econ_df['projected_interest_payments'] = ((econ_df['fed_funds_rate']/100) * (econ_df['govt_debt']/1000))/econ_df['gdp'] * 100

# PAGE CONFIG
# Sets page title, sets layout to be wide.
st.set_page_config(page_title="Government Debt and Spending Data", layout="wide")

# WIDGETS
# Adds logo to dashboard.
st.logo(image="images/treasury.jpg", 
        icon_image="images/treasury.jpg")

# SEABORN
# Sets theme.
sns.set_theme()

# SIDEBAR
with st.sidebar:
    # Adds title/header to sidebar.
    st.title("Government Debt and Spending Data")
    st.header("⚙️ Settings")
    
    min_date = econ_df['observation_date'].min().date()
    max_date = econ_df['observation_date'].max().date()
    default_start_date = min_date
    default_end_date = max_date
    # Adds date input to sidebar.
    start_date = st.date_input("Start date", default_start_date, min_value=econ_df['observation_date'].min().date(), max_value=max_date)
    end_date = st.date_input("End date", default_end_date, min_value=econ_df['observation_date'].min().date(), max_value=max_date)

    freq = st.selectbox("Select Frequency", ["N", "Y", "Custom"])
    if freq == "Custom":
        years = st.number_input("Number of years", min_value=1, max_value=10, value=1)


# AGGREGATE DATA
def aggregate_data(df, metric, freq, years):
    if freq == 'N':
        return df
    elif freq == 'Custom' and years:
        df = df.copy()
        # Creates a new column 'observation_date' by dividing the year of the existing 'observation_date' by years and multiplying by years.
        df['observation_date'] = (df['observation_date'].dt.year // years) * years
        # Applies last aggregation to the metric column.
        df_agg = df.groupby('observation_date').agg({
            metric: 'last'
        })
        # Converts the index to datetime format.
        df_agg.index = pd.to_datetime(df_agg.index, format='%Y')
        return df_agg
    else:
        # Applies last aggregation to the metric column.
        return df.resample(freq, on='observation_date').agg({
            metric: 'last'
        })


# CHARTS
def chart(metric, title, chart_type, freq, years, scale='None'):
    df_display = econ_df.set_index('observation_date')
    mask = (df_display.index >= pd.Timestamp(start_date)) & (df_display.index <= pd.Timestamp(end_date))
    df_filtered = df_display.loc[mask].reset_index()
    
    df_agg = aggregate_data(df_filtered, metric, freq, years)

    # Apply scaling
    if scale == "Millions":
        df_agg[metric] = df_agg[metric] * 1000
    elif scale == "Trillions":
        df_agg[metric] = df_agg[metric] / 1000

    # Calculate Standard Deviation, Sum, Median, Percent Increase, and Average
    std_dev = df_agg[metric].std()
    sum_metric = df_agg[metric].sum()
    median_metric = df_agg[metric].median()
    average_metric = df_agg[metric].mean()
    percent_increase = ((df_agg[metric].iloc[-1] - df_agg[metric].iloc[0]) / df_agg[metric].iloc[0]) * 100
    
    st.write(title)
    
    if chart_type == "Altair":
        hover = alt.selection_single(
            fields=["observation_date"],
            nearest=True,
            on="mouseover",
            empty="none",
        )

        click = alt.selection_single(
            fields=["observation_date"],
            nearest=True,
            on="click",
            empty="none",
        )

        drag = alt.selection_interval(
            encodings=['x']
        )

        line = alt.Chart(df_agg.reset_index()).mark_line(strokeWidth=5).encode(
            x=alt.X('observation_date:T', title='Date'),
            y=alt.Y(metric, title=title)
        ).properties(
            height=700
        )

        points = line.mark_point().encode(
            opacity=alt.condition(hover | click | drag, alt.value(1), alt.value(0))
        ).add_selection(hover, click, drag)

        st.altair_chart(line + points, use_container_width=True)
        
    elif chart_type == "Seaborn":
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_agg.reset_index(), x='observation_date', y=metric)
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel(metric)
        plt.xticks(rotation=45)
        st.pyplot(plt)

    # Display metrics in a card
    st.markdown(
        f"""
        <div style="background-color: #f9f9f9; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #333;">Metrics</h4>
            <hr style="border: none; border-top: 1px solid #eee;">
            <p><strong>Standard Deviation:</strong> {std_dev:.2f}</p>
            <p><strong>Sum:</strong> {sum_metric:.2f}</p>
            <p><strong>Median:</strong> {median_metric:.2f}</p>
            <p><strong>Average:</strong> {average_metric:.2f}</p>
            <p><strong>Percent Increase:</strong> {percent_increase:.2f}%</p>
        </div>
        """, unsafe_allow_html=True
    )

# SIDEBAR
chart_type = st.sidebar.selectbox("Select Chart Type", ["Altair", "Seaborn"])

# SIDEBAR
pages = {
    "Gross Domestic Product": lambda: chart("gdp", "GDP (" + scale + " of Dollars)", chart_type, freq, years if freq == "Custom" else None, scale),
    "Deficit Spending": lambda: chart("deficit_spending", "Deficit Spending (" + scale + " of Dollars)", chart_type, freq, years if freq == "Custom" else None, scale),
    "Interest Percent of GDP": lambda: chart("interest_percent_of_gdp", "Interest Percent of GDP", chart_type, freq, years if freq == "Custom" else None),
    "Debt Percent of GDP": lambda: chart("debt_percent_of_gdp", "Debt Percent of GDP", chart_type, freq, years if freq == "Custom" else None),
    "Interest Percent of Expenditure": lambda: chart("interest_percent_of_expenditure", "Interest Percent of Expenditure", chart_type, freq, years if freq == "Custom" else None)
}

demo = st.sidebar.selectbox("Chart", options=pages.keys(), format_func=lambda x: str(x))

# Conditional selectbox for GDP and Deficit Spending
if demo in ["Gross Domestic Product", "Deficit Spending"]:
    scale = st.sidebar.selectbox("Additional Option", ["Millions", "Billions", "Trillions"])

pages[demo]()