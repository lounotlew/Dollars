# Code for creating a new users.txt file with test-user (i.e. a "fresh" version of PH).
# Used for debugging and testing purposes.

import pandas as pd
import pickle

users = ["Sam"]

with open("users.txt", "wb") as fp:
	pickle.dump(users, fp)

df = pd.DataFrame([], columns = ['Month', 'Year', 'Amount'])

tempDF1 = pd.DataFrame({'Month': [str('1')], 'Year': [str('2018')], 'Amount': [4000]})
tempDF2 = pd.DataFrame({'Month': [str('2')], 'Year': [str('2018')], 'Amount': [5000]})
tempDF3 = pd.DataFrame({'Month': [str('3')], 'Year': [str('2018')], 'Amount': [4500]})
tempDF4 = pd.DataFrame({'Month': [str('4')], 'Year': [str('2018')], 'Amount': [4000]})

df = df.append(tempDF1).reset_index(drop = True)
df = df.append(tempDF2).reset_index(drop = True)
df = df.append(tempDF3).reset_index(drop = True)
df = df.append(tempDF4).reset_index(drop = True)

df.to_pickle('Sam-budget.gz')


cb = ['4', '2018', '4000']

with open("Sam-currentbudget.txt", "wb") as fp:
	pickle.dump(cb, fp)