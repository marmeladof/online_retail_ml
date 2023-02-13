import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns

pd.options.display.max_columns = None
sns.set_theme(style = "darkgrid")

data_path = "data/"
data_file = "Online Retail.xlsx"

io_data = data_path + data_file

data_df = pd.read_excel(io_data)

# distinct value counts

print(data_df.count())
print(data_df.nunique())

# description of numeric columns
print(data_df.loc[:, ["Quantity", "UnitPrice"]].describe())

# filtering to sales

sales_idx = (data_df["UnitPrice"] > 0) & \
                (data_df["Quantity"] > 0)

sales_df = data_df.loc[sales_idx, :]

print(sales_df.count())
print(sales_df.nunique())

# standardising of SKU descriptions

sku_df = sales_df.loc[:, ["StockCode", "Description", "InvoiceDate"]] \
                 .drop_duplicates() \
                 .groupby(["StockCode", "Description"])["InvoiceDate"].max() \
                 .reset_index()

sku_df["rank"] = sku_df.groupby(["StockCode"])["InvoiceDate"] \
                       .rank(method = "dense", ascending = False)

dupes_idx = sku_df["rank"] == 1

sku_df = sku_df.loc[dupes_idx, ["StockCode", "Description"]]
sku_df.columns = ["StockCode", "NewDescription"]

print(sku_df.nunique())

sales_df = pd.merge(left = sales_df, right = sku_df, how = "left",
                    on = "StockCode")

print(sales_df.nunique())

# monthly sales per country

sales_df["InvoiceDay"] = sales_df["InvoiceDate"].dt.to_period("d")

sales_df["InvoiceMonthYear"] = sales_df["InvoiceDate"].dt.to_period("M")

sales_df["InvoiceYear"] = sales_df["InvoiceDate"].dt.to_period("Y")

sales_df["InvoiceSale"] = sales_df["Quantity"] * sales_df["UnitPrice"]

sales_ts = sales_df.groupby(["Country", "InvoiceMonthYear"])["InvoiceSale"] \
                    .sum().reset_index()

sales_ts.columns = ["country", "year_month", "total_sales"]

sales_ts.to_csv(data_path + "monthly_sales.csv")

# monthly tickets per country

tickets_ts = sales_df.groupby(["Country",
                               "InvoiceMonthYear",
                               "InvoiceNo"])["InvoiceSale"] \
                    .sum().reset_index()

tickets_ts = tickets_ts.groupby(["Country",
                               "InvoiceMonthYear"]) \
                    .agg({"InvoiceSale": ["mean", "median", "count"]}).reset_index()

tickets_ts.columns = ["country",
                      "year_month",
                      "mean_invoice_sale",
                      "median_invoice_sale",
                      "invoice_count"]

tickets_ts.to_csv(data_path + "monthly_tickets.csv")


# Plot the responses for different events and regions
sns.lineplot(x = "year_month", y = "total_sales",
             hue = "country",
             data = sales_ts)


