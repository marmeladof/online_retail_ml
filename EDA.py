import pandas as pd

pd.options.display.max_columns = None

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

# analysis of SKU descriptions

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