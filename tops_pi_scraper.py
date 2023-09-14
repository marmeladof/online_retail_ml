
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
import itertools
from datetime import datetime

def dataget(data, key):
    try:
        out = data[key]
    except:
        out = np.nan
    
    return out

def str2datetime(instr, format = "%Y-%m-%dT%H:%M:%S.%fZ"):
    try:
        out = datetime.strptime(instr, format)
    except:
        out = instr
    
    return out

user_agent_str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" + \
                    " (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"

headers = {"User-Agent": ""} 

base_url = ["https://www.portalinmobiliario.com"]
base_api_url = "https://api.mercadolibre.com/items?ids="
n_api_max = 20
operation_url = ["venta"]
proptype_url = ["casa"]
propsubtype_url = ["propiedades-usadas"]
council_url = ["las-condes"]
region_url = ["rm-metropolitana"]

url_ls = list(itertools.product(base_url,
                                operation_url,
                                proptype_url,
                                propsubtype_url,
                                region_url,
                                council_url))

url_ls = ["/".join(list(i)) for i in url_ls]
filter_url0 = ""
stop_url = "/".join(base_url + operation_url + proptype_url)

df = pd.DataFrame()

for url in url_ls:
    cnt = 0
    propsubtype, region, council = url.replace(stop_url, "").split("/")[1:]

    listing_url_ls = []
    listing_price_txt_ls = []
    listing_price_symb_ls = []
    listing_price_frac_ls = []
    listing_prop_attr1_ls = []
    listing_prop_attr2_ls = []
    listing_site_page_ls = []
    listing_site_page_pos_ls = []
    
    while cnt < 10:
        if cnt == 0:
            filter_url = filter_url0
        else:
            filter_num = cnt * 50 + 1
            filter_url = "/_Desde_" + str(filter_num)
        
        page = requests.get(url + filter_url, headers = headers)
        
        mssg = region + "/" + council + "/" + filter_url
        print(mssg)
        mssg = "response code: " + str(page.status_code)
        print(mssg)
        mssg = "bs_url: " + str(page.url)
        print(mssg)
    
        if (page.status_code == 200) & (page.url != stop_url):
            soup = BeautifulSoup(page.text, "html.parser")
            
            listings = soup.find_all("a",
                                     class_ = 'ui-search-result__content-wrapper ui-search-link')
            
            aux_listing_url_ls = []
            aux_listing_price_txt_ls = []
            aux_listing_price_symb_ls = []
            aux_listing_price_frac_ls = []
            aux_listing_prop_attr1_ls = []
            aux_listing_prop_attr2_ls = []
            aux_listing_site_page_ls = []
            aux_page_pos_ls = []
            
            
            for listing in listings:
                    
                aux_listing_url_ls += [listing.attrs["href"]]
                
                aux_listing_site_page_ls += [cnt + 1]
                
                class_txt = "price-tag-text-sr-only"
                aux_listing_price_txt_ls += [listing \
                                             .find_all(class_ = class_txt)[0] \
                                                 .text]
            
                class_txt = "price-tag-symbol"
                aux_listing_price_symb_ls += [listing \
                                             .find_all(class_ = class_txt)[0] \
                                                 .text]
            
                class_txt = "price-tag-fraction"
                aux_listing_price_frac_ls += [listing \
                                                  .find_all(class_ = class_txt)[0] \
                                                      .text]
                class_txt = "ui-search-card-attributes__attribute"
                attr_ls = listing.find_all(class_ = class_txt)
                if len(attr_ls) >= 2:
                    attr1 = attr_ls[0].text.split(" ")[0]
                    try:
                        attr1 = int(attr1)
                    except:
                        attr1 = np.nan
                    aux_listing_prop_attr1_ls += [attr1]
                    
                    attr2 = attr_ls[1].text.split(" ")[0]
                    try:
                        attr2 = int(attr2)
                    except:
                        attr2 = np.nan
                    aux_listing_prop_attr2_ls += [attr2]
                elif len(attr_ls) == 1:
                    attr1 = attr_ls[0].text.split(" ")[0]
                    try:
                        attr1 = int(attr1)
                    except:
                        continue
                    aux_listing_prop_attr1_ls += [attr1]
                    aux_listing_prop_attr2_ls += [np.nan]
                elif len(attr_ls) == 0:
                    aux_listing_prop_attr1_ls += [np.nan]
                    aux_listing_prop_attr2_ls += [np.nan]
            
            aux_page_pos_ls = list(range(len(aux_listing_site_page_ls)))
            
            listing_url_ls += aux_listing_url_ls
            listing_price_txt_ls += aux_listing_price_txt_ls
            listing_price_symb_ls += aux_listing_price_symb_ls
            listing_price_frac_ls += aux_listing_price_frac_ls
            listing_prop_attr1_ls += aux_listing_prop_attr1_ls
            listing_prop_attr2_ls += aux_listing_prop_attr2_ls
            listing_site_page_ls += aux_listing_site_page_ls
            listing_site_page_pos_ls += aux_page_pos_ls
            
        else:
            break
        
        cnt += 1

    data_dict = {"region": region,
                 "council": council,
                 "prop_subtype": propsubtype,
                 "site_page": listing_site_page_ls,
                 "site_page_rnk": listing_site_page_pos_ls,
                 "url": listing_url_ls,
                 "usable_sqm": listing_prop_attr1_ls,
                 "room_cnt": listing_prop_attr2_ls,
                 "price_text": listing_price_txt_ls,
                 "currency": listing_price_symb_ls}

    aux_df = pd.DataFrame(data_dict)
    aux_df["price"] = aux_df["price_text"].apply(lambda x: float(x.split(" ")[0]))
    aux_df["publication_id"] = aux_df["url"].apply(lambda x: x.split("-")[1])
    aux_df["url"] = aux_df["publication_id"].apply(lambda x: base_url[0] + "/" + x)
    aux_df["publication_id"] = aux_df["publication_id"].apply(lambda x: "MLC" + x)
    aux_df["site_page_rnk"] = aux_df["site_page_rnk"] + 1
    
    df = pd.concat([df, aux_df], ignore_index = True)

id_ls = list(df["publication_id"])

id_ls = [id_ls[i:i+20] for i in range(0, len(id_ls), n_api_max)]

api_df = pd.DataFrame()

mssg = "getting API data"
print(mssg)

for pubs in id_ls:
    id_ls_str = ",".join(pubs)
    api_url = base_api_url + id_ls_str
    api_url_data = requests.get(api_url, headers = headers)
    api_json_data = api_url_data.json()
    
    aux_api_df = pd.DataFrame()
    
    for data_row in api_json_data:
        data = data_row["body"]
        
        data_dict_keys = ["publication_id",
                          "seller_id",
                          "seller_address_id",
                          "official_store_id",
                          "title",
                          "subtitle",
                          "currency_id",
                          "listing_type_id",
                          "start_time",
                          "stop_time",
                          "neighborhood",
                          "health",
                          "status",
                          "thumbnail",
                          "date_created",
                          "last_updated"]
        try:
            data_dict_keys += [i["id"].lower() for i in data["attributes"]]
        except:
            continue
        try:
            data_dict_keys += [i for i in data["tags"]]
        except:
            continue
        try:
            data_dict_keys += [i for i in data["warnings"]]
        except:
            continue
        
        try:
            data_dict_keys += [data["sale_terms"][0]["id"].lower()]
        except:
            continue
            
        
        data_dict_vals = [[dataget(data, "id")],
                          [dataget(data, "seller_id")],
                          [data["seller_address"]["id"]],
                          [dataget(data, "official_store_id")],
                          [dataget(data, "title")],
                          [dataget(data, "subtitle")],
                          [dataget(data, "currency_id")],
                          [dataget(data, "listing_type_id")],
                          [dataget(data, "start_time")],
                          [dataget(data, "stop_time")],
                          [data["location"]["neighborhood"]["name"]],
                          [dataget(data, "health")],
                          [dataget(data, "status")],
                          [dataget(data, "thumbnail")],
                          [dataget(data, "date_created")],
                          [dataget(data, "last_updated")]]
        try:
            data_dict_vals += [i["value_name"] for i in data["attributes"]]
        except:
            continue
        try:
            data_dict_vals += [1 for i in data["tags"]]
        except:
            continue
        try:
            data_dict_vals += [1 for i in data["warnings"]]
        except:
            continue
        
        try:
            data_dict_vals += [data["sale_terms"][0]["value_name"]]
        except:
            continue
        
        data_dict = dict(zip(data_dict_keys, data_dict_vals))
        
        aux_api_df = pd.concat([aux_api_df,
                                pd.DataFrame(data_dict)], ignore_index = True)
        
    api_df = pd.concat([api_df, aux_api_df], ignore_index = True)

df = pd.merge(df, api_df, how = "left", on = "publication_id")

df["dw_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
df["start_time"] = df["start_time"].apply(str2datetime)
df["stop_time"] = df["stop_time"].apply(str2datetime)
df["date_created"] = df["date_created"].apply(str2datetime)
df["last_updated"] = df["last_updated"].apply(str2datetime)

time_pre = datetime.now().strftime("%Y%m%d%H%M%S")
out_filename = "C:/Users/gring/Documents/pi_data/" + time_pre + "_" + \
    "topoftheprops.csv"

mssg = "writing data to " + out_filename
print(mssg)


df.to_csv(out_filename, index = False)