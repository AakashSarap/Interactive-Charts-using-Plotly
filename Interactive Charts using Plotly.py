#!/usr/bin/env python
# coding: utf-8

# #### In this part our main focus will be to engineer the key Metric that captures the core value that our product delivers to cusomters. Figuring this out will help us to do a deep dive analysis. Considering our dataset of an Online Retail store, we can go with Monthly Revenue as our key Metric. 

# #### Importing required Libraries & the Dataset

# In[1]:


get_ipython().run_cell_magic('HTML', '', '<style type="text/css">\ntable.dataframe td, table.dataframe th {\n    border: 1px  black solid !important;\n  color: black !important;\n}\n</style>')


# In[2]:


# importing libraries

from __future__ import division
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker 


# plotly

import chart_studio.plotly as py
import plotly.offline as pyoff
import plotly.graph_objs as go

# initiating viz. library for notebook

pyoff.init_notebook_mode()

# loading the dataset

df = pd.read_excel("Online Retail.xlsx")


# In[3]:


# let's have a look at our dataset

df.head(10)


# In[4]:


# Checking the data types

df.info()


# #### Engineering our Revenue Metric

# In[6]:


# creating Month & Year field from Invoice Date
df['InvoiceYearMonth'] = pd.to_datetime(df['InvoiceDate']).dt.strftime('%Y-%m')
# calculating Revenue using a custom function storing it in a new dataframe with Year & Month - Revenue
from Data_Transformation import Revenue
df['Revenue'] = Revenue(df['Quantity'], df['UnitPrice'])
df_rev = df.groupby(['InvoiceYearMonth'])['Revenue'].sum().reset_index()
df_rev


# #### Visualizing the revenue using a line graph

# In[7]:


# X and Y axis inputs for Plotly graph. We use Scatter for line graphs
plot_data = [
    go.Scatter(
        x = df_rev['InvoiceYearMonth'],
        y = df_rev['Revenue'],
    )
]

plot_layout = go.Layout(
    xaxis = {"type": "category"},
    title = 'Monthly Revenue'
)

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# The above graph clearly shows that our revenue is increasing especially in August 2011 onwards. The downward peak in data for December 2011 is due to the incomplete data

# #### Monthly Revenue Growth Rate

# In[8]:


# calculating monthly percentage change using pct_change() function
df_rev['MonthlyGrowth'] = df_rev['Revenue'].pct_change()

# showing first 5 rows
df_rev.head()

# visualizing the % revenue growth
plot_data = [
    go.Scatter(
        x=df_rev.query("InvoiceYearMonth < '2011-12'")['InvoiceYearMonth'], # Not considering 2011 Dec as data is incomplete
        y=df_rev.query("InvoiceYearMonth < '2011-12'")['MonthlyGrowth'],
    )
]

plot_layout = go.Layout(
    xaxis = {"type": "category"},
    title = 'Monthly Growth Rate'
)

fig = go.Figure(data = plot_data, layout = plot_layout)
pyoff.iplot(fig)


# We can see 36.5% of growth in revenue from October 2011 to November 2011. But we need to dive deep to analyze what may have happened in April 2011.

# #### Monthly Active Customers

# We need to know the details of the Active Customers, but we will be focussing on UK based data as it has more records.

# In[9]:


# Creating a new dataframe with UK customers only
df_uk = df.query("Country == 'United Kingdom'").reset_index(drop=True)

# creating monthly active customers dataframe by counting unique Customer IDs
df_monthly_active = df_uk.groupby('InvoiceYearMonth')['CustomerID'].nunique().reset_index()

# print dataframe
print(df_monthly_active)

# visualizing the output
plot_data = [
    go.Bar(
        x=df_monthly_active['InvoiceYearMonth'],
        y=df_monthly_active['CustomerID'],
    )
]

plot_layout = go.Layout(
    xaxis={"type": "category"},
    title='Monthly Active Customers'
)

fig = go.Figure(data = plot_data, layout = plot_layout)
pyoff.iplot(fig)


# What we can see is that in April 2011, Number of active customers dropped down by 11.5% as compared to March 2011 (from 923 to 817)

# #### Monthly Order Count

# In[10]:


# creating monthly order count dataframe by using Quantity field
df_monthly_sales = df_uk.groupby('InvoiceYearMonth')['Quantity'].sum().reset_index()

# print dataframe
print(df_monthly_sales)

# visualizing the output
plot_data = [
    go.Bar(
        x=df_monthly_sales['InvoiceYearMonth'],
        y=df_monthly_sales['Quantity'],
    )
]

plot_layout = go.Layout(
    xaxis={"type": "category"},
    title='Monthly Order Count'
)

fig = go.Figure(data = plot_data, layout = plot_layout)
pyoff.iplot(fig)


# As expected, the Order Count has also declined in April 2011 by 8% (from 279k to 257k). We can say that # of Active Customers is directly affecting the # of Orders, which makes us to look into Average Revenue per Order.

# In[11]:


# create a new dataframe for average revenue by taking the mean of it
df_monthly_order_avg = df_uk.groupby('InvoiceYearMonth')['Revenue'].mean().reset_index()

#print the dataframe
print(df_monthly_order_avg)

#plot the bar chart
plot_data = [
    go.Bar(
        x=df_monthly_order_avg['InvoiceYearMonth'],
        y=df_monthly_order_avg['Revenue'],
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='Monthly Order Average'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# Also, the Monthly Average Revenue declined in April 2011 from $16.7 to $15.8. Now, we saw a lot of downs affecting our Key Metric - Revenue 

# #### It is the time to investigate some other metrics such as New Customer Ratio and Retention Rate

# #### New Customer Ratio
# It indicates if we are losing our customers or if we are unable to get hold of new ones

# In[12]:


# create a dataframe conatining customer ID and first Purchase date
df_min_purchase = df_uk.groupby('CustomerID')['InvoiceDate'].min().reset_index()
df_min_purchase.columns = ['CustomerID', 'MinPurchaseDate']
df_min_purchase['MinPurchaseYearMonth'] = pd.to_datetime(df_min_purchase['MinPurchaseDate']).dt.strftime('%Y-%m')
#pd.to_datetime(df_min_purchase['MinPurchaseDate']).dt.strftime('%Y-%m')

# merging df_min_purchase with our main data frame (df_uk)

df_uk = pd.merge(df_uk, df_min_purchase, on='CustomerID')

print(df_uk.head())


# In[23]:


# Creating a new column User Type and labeling them as assigned if InvoiceYearMonth is after MinPurchaseDate
df_uk['UserType'] = 'New'
df_uk.loc[df_uk['InvoiceYearMonth'] > df_uk['MinPurchaseYearMonth'], 'UserType'] = 'Existing'

# Calculating Revenue per month for each user type
df_user_type_revenue = df_uk.groupby(['InvoiceYearMonth', 'UserType'])['Revenue'].sum().reset_index()

# Visualizing the results
df_user_type_revenue = df_user_type_revenue.query("InvoiceYearMonth != '2010-12' and InvoiceYearMonth != '2011-12'")

plot_data = [
    go.Scatter(
        x=df_user_type_revenue.query("UserType == 'Existing'")['InvoiceYearMonth'],
        y=df_user_type_revenue.query("UserType == 'Existing'")['Revenue'],
        name= 'Existing Customers'
    ),
    go.Scatter(
        x=df_user_type_revenue.query("UserType == 'New'")['InvoiceYearMonth'],
        y=df_user_type_revenue.query("UserType == 'New'")['Revenue'],
        name = 'New Customers'
    )
]

plot_layout = go.Layout(
        xaxis = {"type": "category"},
        title = 'New Customers vs Existing Customers'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# We can see that the Existing Customers has a increasing trend which means that customer base is growing but new customers shows a slight negative trend

# In[22]:


df_uk.head()


# #### Revenue per Month for New and Existing Customers

# In[24]:


df_user_type_revenue.query("InvoiceYearMonth != 2010-12 and InvoiceYearMonth != 2011-12")


# #### Let us Visualize New Customer Ratio

# In[25]:


#create a dataframe that shows new user ratio - we also need to drop NA values (first month new user ratio is 0)
df_user_ratio = df_uk.query("UserType == 'New'").groupby(['InvoiceYearMonth'])['CustomerID'].nunique()/df_uk.query("UserType == 'Existing'").groupby(['InvoiceYearMonth'])['CustomerID'].nunique() 
df_user_ratio = df_user_ratio.reset_index()
df_user_ratio.rename(columns={'CustomerID': 'NewCustomerRatio'}, inplace=True)
df_user_ratio = df_user_ratio.dropna()

#print the dafaframe
print(df_user_ratio)

#plot the result

plot_data = [
    go.Bar(
        x=df_user_ratio.query("InvoiceYearMonth>'2011-01' and InvoiceYearMonth<'2011-12'")['InvoiceYearMonth'],
        y=df_user_ratio.query("InvoiceYearMonth>'2011-01' and InvoiceYearMonth<'2011-12'")['NewCustomerRatio'],
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='New Customer Ratio'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# It is very clear that New Customer Ratio has declined over time

# #### Monthly Retention Rate

# To see how well our products fit the market and how sticky is our service, we need observe the Retention Rate. We can think of it as Retained Customers from Previous Month / Total Active Customers

# In[50]:


#identify which users are active by looking at their revenue per month
df_user_purchase = df_uk.groupby(['CustomerID','InvoiceYearMonth'])['Revenue'].sum().reset_index()

#create retention matrix with crosstab
df_retention = pd.crosstab(df_user_purchase['CustomerID'], df_user_purchase['InvoiceYearMonth']).reset_index()

#create an array of dictionary which keeps Retained & Total User count for each month
months = df_retention.columns[2:]
retention_array = []
for i in range(len(months)-1):
    retention_data = {}
    selected_month = months[i+1]
    prev_month = months[i]
    retention_data['InvoiceYearMonth'] = selected_month
    retention_data['TotalUserCount'] = df_retention[selected_month].sum()
    retention_data['RetainedUserCount'] = df_retention[(df_retention[selected_month]>0) & (df_retention[prev_month]>0)][selected_month].sum()
    retention_array.append(retention_data)
    
#convert the array to dataframe and calculate Retention Rate
df_retention = pd.DataFrame(retention_array)
df_retention['RetentionRate'] = df_retention['RetainedUserCount']/df_retention['TotalUserCount']

#plot the retention rate graph
plot_data = [
    go.Scatter(
        x=df_retention.query("InvoiceYearMonth<'2011-12'")['InvoiceYearMonth'],
        y=df_retention.query("InvoiceYearMonth<'2011-12'")['RetentionRate'],
        name="organic"
    )
    
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='Monthly Retention Rate'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# We can see that how Retention Rate has jumped significantly from May 2011 to August 2011 & again went down same as previous levels.
