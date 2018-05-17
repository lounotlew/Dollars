###########################################################
# Misc. helper functions and data structures for Dollars. #
# Not all functions may be used.                          #
# Written by Lewis Kim.									  #
###########################################################

import pandas as pd
import numpy as np
import math

# A dictionary that maps a month's corresponding number (as a string) to its full name.
num_to_month ={'1': 'January', '2': 'February', '3': 'March', '4': 'April', '5': 'May', '6': 'June',
				'7': 'July', '8': 'August', '9': 'September', '10': 'October', '11': 'November', '12': 'December'}

# A dictionary that maps a month's corresponding number (as a string) to the number of days it has.
# Does not account for leap years.
days_in_month = {'1': 31, '2': 28, '3': 31, '4': 30, '5': 31, '6': 30, '7': 31, '8': 31, '9': 30,
					'10': 31, '11': 30, '12': 31}

# Model for constructing an ARIMA(1, 0, 1).
def difference(dataset, interval = 1):
	diff = list()
	for i in range(interval, len(dataset)):
		value = dataset[i] - dataset[i - interval]
		diff.append(value)

	return np.array(diff)

# Model for ARIMA forecasting.
def inverse_difference(history, yhat, interval = 1):
	return yhat + history[-interval]

# Hashing a string password.
# Source: https://www.pythoncentral.io/hashing-strings-with-python/
def hash_password(password):
    # uuid is used to generate a random number
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

# Unhashing a string password.
# Source: https://www.pythoncentral.io/hashing-strings-with-python/
def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
