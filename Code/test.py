# -*- coding: utf-8 -*-

print("h")
import numpy as np
import pandas as pd
print("h0")
# importing the London energy dataset
data=pd.read_csv('C:\\Users\\23304161\\Desktop\\LCL-FullData\\CC_LCL-FullData.csv')

print("h1")
# Checking the unique rows count of every column
data.describe()
print("h2")
data['LCLid'].unique()
print("h3")
# Checking the datatype of all columns
data.info()
print("h4")