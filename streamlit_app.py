import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style = "darkgrid")

sales_ts = pd.read_csv("monthly_sales.csv")

st.title("Monthly Sales")

CountryFilterList = sales_ts["Country"].drop_duplicates()

with st.sidebar:
    CountryFilter = st.multiselect(label = "Country",
                                 options = CountryFilterList,
                                 default = CountryFilterList)

filter_idx = sales_ts["Country"].isin(CountryFilter)

printTable = sales_ts.loc[filter_idx, :]
    
fig = plt.figure(figsize=(10, 4))
sns.lineplot(x = "InvoiceMonthYear", y = "InvoiceSale",
             hue = "Country",
             data = printTable)
st.pyplot(fig)
