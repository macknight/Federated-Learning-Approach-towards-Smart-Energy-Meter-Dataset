# -*- coding: utf-8 -*-
"""datacl_kmeans_final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/macknight/Federated-Learning-Approach-towards-Smart-Energy-Meter-Dataset/blob/Draft/Code/datacl_kmeans_final.ipynb

**PART 1 : DATA CLEANING**
"""

import numpy as np
import pandas as pd

print("h1")
# importing the London energy dataset
data=pd.read_csv('C:\\Users\\23304161\\Desktop\\LCL-FullData\\CC_LCL-FullData.csv')

print("h2")
# Checking the unique rows count of every column
# data.describe()

# data['LCLid'].unique()

# Checking the datatype of all columns
# data.info()

num_unique_customers = len(data['LCLid'].unique())
print("Number of unique customers: ", num_unique_customers)

# Re-naming the column to make it small
data.columns = ['LCLid', 'stdorToU', 'DateTime', 'KWH/hh']
print(data.columns)

# data

# # Checking the NAN values for each column
# data.isna().sum()

# # Checking the Null values for each column
# data.isnull().sum()

# making KWH/hh float type
data2 = data.copy()
data2['KWH/hh'] = data2['KWH/hh'].replace('Null', np.nan).astype('float32')
# data2.info()

# data2

# checking kwh avg per LCLid
avg_kwh = data2.groupby('LCLid')['KWH/hh'].mean()
print(avg_kwh)

# identify rows with NaN KWH/hh values and dropping
# nan_rows = data2['KWH/hh'].isna()
# dropping nan values
data2.dropna(subset=["KWH/hh"], inplace=True)

# checking kwh avg per LCLid again after dropping values
avg_kwh = data2.groupby('LCLid')['KWH/hh'].mean()
print(avg_kwh)

# checking min,max,mean value of avg
min_avgkwh = avg_kwh.min()
max_avgkwh = avg_kwh.max()
avg_avgkwh = avg_kwh.mean()
# checking min,max,mean value of avg
print(min_avgkwh, max_avgkwh, avg_avgkwh)

# checking min,max,mean value of avg (setting boundaries)
KWH_less_than_009 = (avg_kwh < 0.09).sum()
KWH_more_than_135 = (avg_kwh > 1.35).sum()

# print the results
print(KWH_less_than_009, KWH_more_than_135)

#transferring for data cleaning
data3 = data2.copy()
# data.info()

# data3.info()

# droping rows as per limits set
Yavg_kwh = data3.groupby('LCLid')['KWH/hh'].mean()

# drop rows where the average 'KWH/hh' is less than 0.09 or more than 1.35
to_drop = Yavg_kwh[(Yavg_kwh < 0.09) | (Yavg_kwh > 1.35)].index

# to_drop

data3 = data3[~data3['LCLid'].isin(to_drop)]

# reset the index of the dataframe
data3 = data3.reset_index(drop=True)
# data3

data4 = data.copy()
# data4

# data.info()
# data2.info()
# data3.info()
# data4.info()

data4['KWH/hh'] = data4['KWH/hh'].replace('Null', np.nan)
# data4

# dropping nan values
data4.dropna(subset=['KWH/hh'],inplace=True)
# data4.info()
# data4

data4 = data4[~data4['LCLid'].isin(to_drop)]

# reset the index of the dataframe
data4 = data4.reset_index(drop=True)
# data4

# counting readings
count_s = data3.groupby('LCLid')['KWH/hh'].count()
print(count_s)

# checking drop values existance
exists = "MAC000004" in data3['LCLid'].values
print(exists)

# checking grouped statistics
grouped_data3 = data3.groupby('LCLid')

"""**USING K-MEANS FOR CLUSTERING THE LCLId's into 18 Groups as per London Household ACORN INDEX**"""

# calculate the median, average, sum, highest, and lowest energy consumption for each 'LCLid'
median_consumption = grouped_data3['KWH/hh'].median()
average_consumption = grouped_data3['KWH/hh'].mean()
sum_consumption = grouped_data3['KWH/hh'].sum()
highest_consumption = grouped_data3['KWH/hh'].max()
lowest_consumption = grouped_data3['KWH/hh'].min()

# checking grouped statistics
# print the results
print('Energy consumption median:')
print(median_consumption)
print('Energy consumption average:')
print(average_consumption)

print('Energy consumption sum:')
print(sum_consumption)

print('Highest recorded energy consumption:')
print(highest_consumption)

print('Lowest recorded energy consumption:')
print(lowest_consumption)

unique_count = data3['LCLid'].nunique()
print("Number of unique LCLids:", unique_count)

#create a new dataframe with the required features
kmeans_data = pd.DataFrame({
    'LCLid': grouped_data3['KWH/hh'].median().index,
    'median_consumption': median_consumption,
    'average_consumption': average_consumption,
    'sum_consumption': sum_consumption,
    'highest_consumption': highest_consumption,
    'lowest_consumption': lowest_consumption
})

# kmeans_data

# standardize the data
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
kmeans_data_scaled = scaler.fit_transform(kmeans_data.iloc[:, 1:5])

# apply KMeans algorithm to divide the LCLIDs into 18 groups
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=18, random_state=42)
kmeans.fit(kmeans_data_scaled)

# add cluster labels to the dataframe
kmeans_data['cluster'] = kmeans.labels_
# print the number of LCLIDs in each cluster
print(kmeans_data['cluster'].value_counts())

#checking K-means data with cluster added
# reset the index of kmeans_data
kmeans_data = kmeans_data.reset_index(drop=True)
# kmeans_data

# merge the dataframes based on LCLid
merged_data = pd.merge(data4, kmeans_data[['LCLid', 'cluster']], on='LCLid')

import matplotlib.pyplot as plt
grouped_clusters = kmeans_data.groupby('cluster')
cluster_data = []
for cluster_label, cluster_df in grouped_clusters:
    cluster_data.append(cluster_df['lowest_consumption'].values)

plt.figure(figsize=(12, 6))
plt.boxplot(cluster_data)
plt.xlabel('Cluster')
plt.ylabel('Lowest Recorded Consumption')
plt.title('K-means Clustering - Lowest Recorded Consumption by Cluster')
plt.xticks(range(1, len(cluster_data) + 1), range(1, len(cluster_data) + 1))
plt.show()

# We proceed with all the data's in cluster 15, 14 and 8 and make seperate files for federated learning.
cluster_18_data = merged_data[merged_data['cluster'] == 17]
cluster_14_data = merged_data[merged_data['cluster'] == 13]
cluster_8_data = merged_data[merged_data['cluster'] == 7]
cluster_9_data = merged_data[merged_data['cluster'] == 8]
cluster_4_data = merged_data[merged_data['cluster'] == 3]
cluster_7_data = merged_data[merged_data['cluster'] == 6]
# cluster_18_data.info()

cluster_18_data.to_csv('C:\\Users\\23304161\\Desktop\\LCL-FullData\\Cluster15data.csv', index=False)
cluster_14_data.to_csv('C:\\Users\\23304161\\Desktop\\LCL-FullData\\Cluster14data.csv', index=False)
cluster_8_data.to_csv('C:\\Users\\23304161\\Desktop\\LCL-FullData\\Cluster8data.csv', index=False)
cluster_9_data.to_csv('C:\\Users\\23304161\\Desktop\\LCL-FullData\\Cluster9data.csv', index=False)
cluster_4_data.to_csv('C:\\Users\\23304161\\Desktop\\LCL-FullData\\Cluster4data.csv', index=False)
cluster_7_data.to_csv('C:\\Users\\23304161\\Desktop\\LCL-FullData\\Cluster7data.csv', index=False)

# cluster_18_data.to_csv('C:\\Users\\23304161\\Desktop\\LCL-FullData\\Cluster15data.csv', index=False)