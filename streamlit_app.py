import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style = "darkgrid")

data_path = "data/"
sales_filename = "monthly_sales.csv"
tickets_filename = "monthly_tickets.csv"

sales_ts = pd.read_csv(data_path + sales_filename)
tickets_ts = pd.read_csv(data_path + tickets_filename)

st.title("Monthly Sales")

CountryFilterList = sales_ts["country"].drop_duplicates()

with st.sidebar:
    CountryFilter = st.multiselect(label = "Country",
                                   options = CountryFilterList,
                                   default = CountryFilterList)

filter_idx = sales_ts["country"].isin(CountryFilter)

printTable = sales_ts.loc[filter_idx, :]
    
fig = plt.figure(figsize=(10, 4))
sns.lineplot(x = "InvoiceMonthYear", y = "InvoiceSale",
             hue = "Country",
             data = printTable)
st.pyplot(fig)
