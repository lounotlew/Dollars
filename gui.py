##############################################################################################
# Main GUI class for Dollars.            # Code Line Contents:                               #
# Written by Lewis Kim.                  # - init, user creation, and management: 55 - 270   #
#                                        # - Spending data management page: 272 - 534        #
# Comment Keys:                          # - Spending data visualization page: 536 - 932     #
# - FIX: Needs bugfix or improvement.    # - Spending data prediction page: 934 - 1120       #
# - NYI: Not Yet Implemented.            # - Budget management page: 1122 - 1334             #
# - NR: Needs Removal.                   # - Spending profile page: 1336 - 1648              #
##############################################################################################

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from tkinter.messagebox import showinfo

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook

import pandas as pd
import pickle
from pandastable import Table, TableModel

import numpy as np
import math
import os
import shutil
import webbrowser
from datetime import datetime
from geopy.geocoders import GoogleV3
from gmplot import gmplot

from statsmodels.tsa.stattools import acf, pacf
import statsmodels.tsa.stattools as ts
from statsmodels.tsa.arima_model import ARIMA
from pyramid.arima import auto_arima

import utils

# Add API Key to GoogleV3, i.e. geolocator1 = GoogleV3(api_key = "YOUR API KEY")
geolocator1 = GoogleV3()

# GUI class for Dollars. All subsequent windows opened in Dollars will be defined as functions in this class.
class Dollars:

	def __init__(self, master):
		self.username = ""       # Current username. Initialized with empty string.
		self.logged_in = False   # Whether or not a user has been selected. Initially false.

		with open("data/main/users.txt", "rb") as fp:  # Read in the usernames into a list from 'data/main/users.txt'.
			self.users = pickle.load(fp)

		# Spending data (as a pandas data frame) for the current user. Initialized as an empty data frame with defined columns..
		self.spendingData = pd.DataFrame([], columns = ["Address", "Amount", "Category", "City", "Country", "Date", "Description", "Latitude", "Longitude",
														"Payment Type", "Planned", "State", "User Address"])

		# Budget data (as a pandas data frame) for the current user. Initialized as an empty data frame with defined columns.
		self.budgetData = pd.DataFrame([], columns = ["Month", "Year", "Amount"])
		self.currentBudget = ['0', '0', '0']		# List containing data for current month, year, and budget as strings (to write to .txt file). Initially empty.
		self.userFolder = ""     		   	# File path to the current user's folder in 'data/users'. Initialized as an empty string.
		self.userSpendingFilePath = ""     		# File path to the .gz file containing the current user's spending data. Intialized as an empty string.
		self.userBudgetFilePath = ""       		# File path to the .gz file containing the current user's budget data. Initialized as an empty string.

		# Frames for the homepage of Dollars.
		frame1 = Frame(master)
		frame2 = Frame(master)
		frame3 = Frame(master)
		frame4 = Frame(master)
		frame5 = Frame(master)
		frame1.pack()
		frame2.pack()
		frame3.pack()
		frame4.pack()
		frame5.pack()

		# Welcome label.
		self.welcomeLabel = Label(frame1, text = "Dollars: Your Personal Finance Manager", font = ("Helvetica", 16))
		self.welcomeLabel.grid(row = 0)

		# A username label. Initialized as 'Please create of select a user', and then updates to 'Welcome, USERNAME' once a user has been selected.
		self.userLabel = Label(frame2, text = "Please create or select a user.", font = ("Helvetica", 14))
		self.userLabel.grid(row = 1)

		# A Button that displays all current users.
		self.displayUserButton = Button(frame3, text = "Display Users", font = ("Helvetica", 13), command = self.displayUsers)
		self.displayUserButton.grid(row = 2, column = 0)

		# A Button for creating a new user.
		self.createUserButton = Button(frame3, text = "Create a User", font = ("Helvetica", 13), command = self.createUser)
		self.createUserButton.grid(row = 2, column = 1)

		# A Button for selecting an existing user.
		self.selectUserButton = Button(frame3, text = "Select a User", font = ("Helvetica", 13), command = self.selectUser)
		self.selectUserButton.grid(row = 2, column = 2)

		# An button that deletes a user.
		self.deleteUserButton = Button(frame3, text = "Delete a User", font = ("Helvetica", 13), command = self.deleteUser)
		self.deleteUserButton.grid(row = 2, column = 3)

		# A Button for displaying spending data collection/management window.
		self.spendingButton = Button(frame4, text = "Manage Your Spendings", font = ("Helvetica", 13), command = self.createManagePage)
		self.spendingButton.grid(row = 3, column = 0)

		# A Button for visualizing a user's spendings with various matplotlib graphs.
		self.visSpendingButton = Button(frame4, text = "Visualize Your Spendings", font = ("Helvetica", 13), command = self.createVisPage)
		self.visSpendingButton.grid(row = 3, column = 1)

		# A Button for predicting a user's spendings.
		self.predictSpendingButton = Button(frame4, text = "Predict Your Spendings", font = ("Helvetica", 13), command = self.createPredictionPage)
		self.predictSpendingButton.grid(row = 3, column = 2)

		# Button for managing and displaying a user's budget data (and its interactions with spending data).
		self.budgetPageButton = Button(frame5, text = "Manage Your Budget", font = ("Helvetica", 13), command = self.createBudgetPage)
		self.budgetPageButton.grid(row = 4, column = 0)

		# Button for building and displaying a user's spending profile based on self.spendingData.
		self.spendingProfileButton = Button(frame5, text = "Your Spending Profile", font = ("Helvetica", 13), command = self.createProfilePage)
		self.spendingProfileButton.grid(row = 4, column = 1)

	"""Create a new user. Username gets added to self.users, and consequently users.txt, which is a master-file of all the
	   existing users. If self.username already exists in self.users, throws an error. Else, a new folder with the given username
	   is created in the 'spending' folder (self.userFolder), containing a .gz file of the initially empty user
	   spending data (self.userSpendingFilePath)."""
	def createUser(self):
		askedName = simpledialog.askstring("Create a New User", "Username:")

		if askedName == None:
			return

		# Check if selected username already exists.
		if askedName in self.users:
			showinfo("Error", "That user already exists. Please create a new user, or select an existing user.")
			return

		# Set the necessary class variables associated with a user.
		self.username = askedName
		
		self.logged_in = True
		self.spendingData = pd.DataFrame([], columns = ["Address", "Amount", "Category", "City", "Country", "Date", "Description", "Latitude", "Longitude",
														"Payment Type", "Planned", "State", "User Address"])
		self.budgetData = pd.DataFrame([], columns = ["Month", "Year", "Amount"])

		self.monthly_budget = 0
		self.budget_month = 0
		self.budget_year = 0
		self.currentBudget = ['0', '0', '0']

		# Create necessary directories and folders for the new user.
		self.userFolder = "data/users/" + self.username
		self.userSpendingFilePath = "data/users/" + self.username + "/" + self.username + "-spending.gz"
		self.userBudgetFilePath = "data/users/" + self.username + "/" + self.username + "-budget.gz"

		# Try to make a directory with the username; throw an error otherwise (usually only when a folder with the username already exists).
		try:
			os.makedirs(self.userFolder)
			os.makedirs(self.userFolder + "/graphics")
		except:
			showinfo("Error", "Makedir Error")

		# Save the initially empty user data to .gz files.
		self.spendingData.to_pickle(self.userSpendingFilePath)
		self.budgetData.to_pickle(self.userBudgetFilePath)

		# Change the username label to display "Welcome, USERNAME".
		self.userLabel['text'] = "Welcome, " + self.username + "."

		# Add the username to the masterlist of all current users.
		self.users.append(self.username)

		# Create a .txt file to store the current budget information.
		f = open("data/users/" + self.username + "/" + self.username + "-currentbudget.txt", "w+")
		f.close()

		# Write the masterlist of all users to users.txt.
		with open("data/main/users.txt", "wb") as fp:
			pickle.dump(self.users, fp)

		# Add the current budget information to the formerly created .txt file.
		with open("data/users/" + self.username + "/" + self.username + "-currentbudget.txt", "wb") as fp:
			pickle.dump(self.currentBudget, fp)

	"""Select an existing user from self.users (read from users.txt). self."""
	def selectUser(self):
		askedName = simpledialog.askstring("Select a User", "Username:")

		if askedName == None:
			return

		# Check if the selected username exists.
		if not askedName in self.users:
			showinfo("Error", "That user does not exist. Please create a new user, or select an existing user.")
			return

		self.username = askedName

		# Change the status of self.logged_in, and update the necessary filepaths to the user's data.
		self.logged_in = True
		self.userSpendingFilePath = "data/users/" + self.username + "/" + self.username + "-spending.gz"
		self.userBudgetFilePath = "data/users/" + self.username + "/" + self.username + "-budget.gz"

		# Read in the user data from .gz files stored in the user's folder in data/users.
		self.spendingData = pd.read_pickle(self.userSpendingFilePath)
		self.budgetData = pd.read_pickle(self.userBudgetFilePath)

		# Read in the user's current budget information from the .txt file in data/users.
		with open("data/users/" + self.username + "/" + self.username + "-currentbudget.txt", "rb") as fp:
			self.currentBudget = pickle.load(fp)

		# Update the user label.
		self.userLabel['text'] = "Welcome, " + self.username + "."

	"""Display the existing users (elements of self.users, items of 'data/main/users.txt') in a text widget."""
	def displayUsers(self):
		window = Toplevel()
		window.title("Current Users")

		# Create a new text windoe, and add all the usernames to it.
		t = Text(window, font = ("Helvetica", 14))

		for i in range(0, len(self.users)):
			if self.users[i] == self.username:
				t.insert(END, str(i+1) + ". " + self.users[i] + " (Selected)" + '\n')
			else:	
				t.insert(END, str(i+1) + ". " + self.users[i] + '\n')

		t.pack()

	"""Delete the user selected from the simpledialog window."""
	def deleteUser(self):
		user = simpledialog.askstring("Delete User", "Which user would you like to delete?")

		if user == None:
			return

		# Check if the username is actually a created user.
		if not user in self.users:
			showinfo("Error", "That user does not exist.")
			return

		# Confirmation window.
		answer = messagebox.askyesno("Are You Sure?", "Are you sure you want to delete " + user + "'s profile and all its contents?")

		if answer == None or answer == False:
			return

		# If the answer is yes, delete the username from the username list (and the .txt file),
		# and the folder with the username as its name in data/users (along with all its contents).
		if answer == True:
			self.users.remove(user)

			with open("data/main/users.txt", "wb") as fp:
				pickle.dump(self.users, fp)

			shutil.rmtree('data/users/' + user)

			showinfo("Success", "Successfully Removed " + user + "'s Profile.")

			# Change the user label.
			self.userLabel['text'] = "Please create or select a user."

			return

	"""Create a new window (Toplevel()) that contains all necessary buttons and widgets for personal spending data
	   collection and management. All subsequent functions before self.createVisPage are related to this page."""
	def createManagePage(self):
		if self.logged_in == False:
			showinfo("Error", "Please create a new user or select an existing user first.")
			return

		window = Toplevel()
		window.title("Manage Your Spendings")

		# A label for spending description.
		self.spendingDescLabel = Label(window, text = "Spending Description:", font = ("Helvetica", 14))
		self.spendingDescLabel.grid(row = 1, column = 0)

		# Entry field for spending description.
		self.spendingDescEntry = Entry(window)
		self.spendingDescEntry.grid(row = 1, column = 1)

		# A label for the spending amount entry.
		self.spendingAmountLabel = Label(window, text = "Amount Spent ($):", font = ("Helvetica", 13))
		self.spendingAmountLabel.grid(row = 2, column = 0)

		# Entry field for the spending amount. Must be numeric.
		self.spendingAmountEntry = Entry(window)
		self.spendingAmountEntry.grid(row = 2, column = 1)

		# A label for the spending date entry.
		self.spendingDateLabel = Label(window, text = "Date of Spending (MM-DD-YYYY):", font = ("Helvetica", 13))
		self.spendingDateLabel.grid(row = 3, column = 0)

		# Entry field for the spending date. Must follow MM-DD-YYYY datetime format (e.g. 1-20-1990).
		self.spendingDateEntry = Entry(window)
		self.spendingDateEntry.grid(row = 3, column = 1)

		# A label for the spending address. Cannot be empty.
		self.spendingAddressLabel = Label(window, text = "Spending Address (Home Address if Online/Bills):", font = ("Helvetica", 13))
		self.spendingAddressLabel.grid(row = 4, column = 0)

		# Entry field for spending address. Home address if online purchases or bill/mortgage payments.
		self.spendingAddressEntry = Entry(window)
		self.spendingAddressEntry.grid(row = 4, column = 1)

		# A lanel for spending category.
		self.spendingCategoryLabel = Label(window, text = "Spending Category:", font = ("Helvetica", 13))
		self.spendingCategoryLabel.grid(row = 5, column = 0)

		# An option menu that contains various spending categories as strings.
		self.variable = StringVar(window)
		self.variable.set("Consumer Debt")
		self.spendingCategory = OptionMenu(window, self.variable, "Consumer Debt", "Entertainment", "Food & Groceries", "Healthcare", 
													"Housing", "Luxury", "Misc. Expenses", "Personal Care", "Savings", "Utilities")
		self.spendingCategory.grid(row = 5, column = 1)

		# A label for payment type option menu.
		self.paymentTypeLabel = Label(window, text = "Payment Type:", font = ("Helvetica", 13))
		self.paymentTypeLabel.grid(row = 6, column = 0)

		# An option menu for payment type.
		self.paymentType = StringVar()
		self.paymentType.set("Cash")
		self.paymentTypeMenu = OptionMenu(window, self.paymentType, "Cash", "Check", "Credit", "Debit", "Other")
		self.paymentTypeMenu.grid(row = 6, column = 1)

		# A label for planned/unplanned purchases.
		self.planLabel = Label(window, text = "Planned or Unplanned Spending:", font = ("Helvetica", 13))
		self.planLabel.grid(row = 7, column = 0)

		# An option menu that says whether a purchase was planned or unplanned.
		self.pup = StringVar()
		self.pup.set("Planned")
		self.pupCategory = OptionMenu(window, self.pup, "Planned", "Unplanned")
		self.pupCategory.grid(row = 7, column = 1)

		# A button for adding the current entries in amount, date, and category to self.spendingData.
		# Throws an error if amount and/or date is empty, or invalid.
		self.addSpendingButton = Button(window, text = "Add Entries", font = ("Helvetica", 13), command = self.addToSpendingData)
		self.addSpendingButton.grid(row = 8, column = 0)

		# A button for removing the last entry (row) in self.spendingData.
		self.removeLastEntryButton = Button(window, text = "Remove Last Entry", font = ("Helvetica", 13), command = self.removeLastEntry)
		self.removeLastEntryButton.grid(row = 8, column = 1)

		# Label for current number of entries in self.spendingData.
		self.numOfEntries = Label(window, text = "Current Number of Entries: " + str(len(self.spendingData)), font = ("Helvetica", 13))
		self.numOfEntries.grid(row = 9, column = 0)

		# A button for displaying the current data in self.spendingData.
		self.displaySpendingData = Button(window, text = "Display Spending Data", font = ("Helvetica", 13), command = self.showSpendingData)
		self.displaySpendingData.grid(row = 9, column = 1)

	"""Return the string in the spending description entry field."""
	def getSpendingDescription(self):
		if self.spendingDescEntry.get() == "":
			showinfo("Error", "Spending Description cannot be empty.")
			return

		try:
			return self.spendingDescEntry.get()
		except:
			showinfo("Error", "Invalid Spending Description.")
			return

	"""Return the current float value in self.spendingAmountEntry."""
	def getSpendingAmount(self):
		try:
			return float(self.spendingAmountEntry.get())
		except:
			showinfo("Error", "Need a numeric entry.")

	"""Return the current datetime value in self.spendingDateEntry."""
	def getSpendingDate(self):
		try:
			return datetime.strptime(self.spendingDateEntry.get(), '%m-%d-%Y')
		except:
			showinfo("Error", "Please input a valid date.")
			return

	"""Return the address in self.spendingAddressEntry."""
	def getAddress(self):
		if self.spendingAddressEntry.get() == "":
			showinfo("Error", "Addresses cannot be empty.")
			return

		try:
			return self.spendingAddressEntry.get()
		except:
			showinfo("Error", "Address Error")
			return

	"""Returns a list of spending locational data in a dictionary, in the form of
	   {'latitude': float, 'longitude': float, 'address': string, 'city': string, 'state': string, 'country': string}."""
	def getSpendingLocationData(self):
		if self.getAddress() == None:
			return

		# Empty dictionary that will contain all necessary locational data.
		locational_data = {}

		# Check if the address is valid (i.e. whether or not GoogleV3 throws an error).
		try:
			coords_info = geolocator1.geocode(self.getAddress(), timeout = 10)
			latitude = coords_info.latitude
			longitude = coords_info.longitude

			coords  = (latitude, longitude)

			location = geolocator1.reverse(coords)

		except:
			showinfo("Error", "GoogleV3 Location Error")
			return

		# Check if the country is the US.
		try:
			loc = location[0]
			address = loc.address
			city_state_country = address.split(",")[-3:]

			# Remove spaces around words.
			city_state_country = [x.split(" ")[1] for x in city_state_country]

		except:
			showinfo("Error", "Dollars currently only supports addresses in the United States.")
			return

		# Split the returned strings into the necessary counterparts to retrieve the city/state names.
		city = city_state_country[0]
		state = city_state_country[1]
		country = city_state_country[2]

		# # Add the locational data to locational_data with the correct keys.
		locational_data['latitude'] = latitude
		locational_data['longitude'] = longitude
		locational_data['address'] = address
		locational_data['city'] = city
		locational_data['state'] = state
		locational_data['country'] = country

		return locational_data

	"""Get the spending category in self.spendingCategory."""
	def getSpendingCategory(self):
		try:
			return self.variable.get()
		except:
			showinfo("Error", "Spending Category Error")
			return

	"""Get the payment type in self.paymentTypeMenu."""
	def getPaymentType(self):
		try:
			return self.paymentType.get()
		except:
			showinfo("Error", "Payment Type Error")
			return

	"""Get Planned or Unplanned Spending in self.pupCategory. Returns True if Planned, False otherwise."""
	def getPUP(self):
		if self.pup.get() == "Planned":
			return True
		else:
			return False

	"""Update the number of entries label to the correct number of entries."""
	def updateNumOfEntries(self):
		text = "Current Number of Entries: " + str(len(self.spendingData))
		self.numOfEntries['text'] = text

	"""Add the spending amount, spending date, and spending category to self.spendingData,
	   and write it to a .gz file in self.userSpendingFilePath."""
	def addToSpendingData(self):
		location_data = self.getSpendingLocationData()

		if self.getSpendingDescription() == None or self.getSpendingAmount() == None or self.getSpendingDate() == None or location_data == None:
			return

		else:
			try:
				pup = self.getPUP()
				category = self.getSpendingCategory()

				# Create a temporary dataframe that contains data from all entry fields from the data management page, and append it to self.spendingData.
				tempDF = pd.DataFrame({'Address': [location_data['address']], 'Amount': [self.getSpendingAmount()], 'Category': [category],
											'City': [location_data['city']], 'Country': [location_data['country']], 'Date': [self.getSpendingDate()], 'Description': [self.getSpendingDescription()],
											'Latitude': [location_data['latitude']], 'Longitude': [location_data['longitude']], 'Payment Type': [self.getPaymentType()],
											'Planned': [self.getPUP()], 'State': [location_data['state']], 'User Address': [self.getAddress()]})
				self.spendingData = self.spendingData.append(tempDF).reset_index(drop = True)

				# Update the number of entries label in the data management page.
				self.updateNumOfEntries()

				# Export self.spendingData to its .gz file.
				self.spendingData.to_pickle(self.userSpendingFilePath)

			except:
				showinfo("Error", "Adding to Spending Data Error")
				return

	"""Remove the last entry (row) from self.spendingData, and then write it to a .gz file
	   in self.userSpendingFilePath."""
	def removeLastEntry(self):
		if len(self.spendingData) == 0:
			showinfo("Error", "Your dataset is empty!")

		else:
			self.spendingData = self.spendingData[:-1]
			self.spendingData.reset_index(drop = True, inplace = True)

			self.updateNumOfEntries()

			self.spendingData.to_pickle(self.userSpendingFilePath)

			showinfo("Success", "Successfully removed last entry.")

	"""Display self.spendingData in a new window using pandastable."""
	def showSpendingData(self):
		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")

		else:
			top1 = Toplevel()
			top1.title("Your Spending Data")

			self.table = pt = Table(top1, dataframe = self.spendingData)
			pt.show()
			return

	"""Create a new window (Toplevel()) that contains all necessary buttons and widgets for personal spending data
	   visualizations. All subsequent functions before self.createPredictionPage are related to this page."""
	def createVisPage(self):
		if self.logged_in == False:
			showinfo("Error", "Please create a new user or select an existing user first.")
			return

		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")
			return

		window1 = Toplevel()
		window1.title("Visualize Your Spendings")

		# Getting all unique spending months (Month/Year) and spending cities to avoid unnecessary multiple calls.
		self.uniqueMonths = self.getUniqueMonths()
		self.uniqueCities = self.getUniqueCities()

		# A button to display an overall daily average spending trend graph for the selected month.
		self.monthlyTrendButton = Button(window1, text = "View a Spending Trend Graph", font = ("Helvetica", 13), command = self.showGeneralTrend)
		self.monthlyTrendButton.grid(row = 0, column = 0)

		# A label that states "Select a Month:". Filter for self.monthlyTrendButton.
		self.monthlyTrendLabel = Label(window1, text = "Select a Month:", font = ("Helvetica", 13))
		self.monthlyTrendLabel.grid(row = 0, column = 1)

		# An option menu that selects a month for self.monthlyTrendButton.
		self.trendMonth = StringVar()
		self.trendMonth.set("All Months")
		self.trendMonthOptions = OptionMenu(window1, self.trendMonth, "All Months", *self.uniqueMonths)
		self.trendMonthOptions.grid(row = 0, column = 2)

		# A button to display an overall daily average spending trend graph by spending category for this month.
		self.categoryTrendButton = Button(window1, text = "View a Spending Trend Graph by Category", font = ("Helvetica", 13), command = self.showCategoryTrend)
		self.categoryTrendButton.grid(row = 1, column = 0)

		# A label that reads "Category:". Filter for self.categoryTrendButton.
		self.categoryTrendLabel = Label(window1, text = "Category:", font = ("Helvetica", 13))
		self.categoryTrendLabel.grid(row = 1, column = 1)

		# An option menu for selecting the spending category for self.categoryTrendButton.
		self.trendCategory = StringVar()
		self.trendCategory.set("Consumer Debt")
		self.trendOptions = OptionMenu(window1, self.trendCategory, "Consumer Debt", "Entertainment", "Food & Groceries", "Healthcare", "Housing", "Luxury", "Misc. Expenses", "Personal Care", "Savings", "Utilities")
		self.trendOptions.grid(row = 1, column = 2)

		# A Button to display a pie chart (PC) for spending category by # of purchases (count), filtered by month/year.
		self.countCategoryPCButton = Button(window1, text = "View a Count Pie Chart for Spending by Category ", font = ("Helvetica", 13), command = self.showCountCategoryPieChart)
		self.countCategoryPCButton.grid(row = 2, column = 0)

		# A label that reads "Select a Month:". Filter for self.countCategoryPCButton.
		self.countPCMonthLabel = Label(window1, text = "Select Month:", font = ("Helvetica", 13))
		self.countPCMonthLabel.grid(row = 2, column = 1)

		# An option menu that selects the month/year for self.countCategoryPCButton.
		self.countPCMonth = StringVar()
		self.countPCMonth.set("All Months")
		self.countPCMonthOptions = OptionMenu(window1, self.countPCMonth, "All Months", *self.uniqueMonths)
		self.countPCMonthOptions.grid(row = 2, column = 2)

		# A Button to display a pie chart (PC) for spending category by amount of money spent (sum), filtered by month/year.
		self.sumCategoryPCButton = Button(window1, text = "View a Sum Pie Chart for Spending by Category", font = ("Helvetica", 13), command = self.showSumCategoryPieChart)
		self.sumCategoryPCButton.grid(row = 3, column = 0)

		# A label that reads "Select a Month:". Filter for self.sumCategoryPCButton.
		self.sumPCMonthLabel = Label(window1, text = "Select Month:", font = ("Helvetica", 13))
		self.sumPCMonthLabel.grid(row = 3, column = 1)

		# An option menu that selects the month/year for self.sumCategoryPCButton.
		self.sumPCMonth = StringVar()
		self.sumPCMonth.set("All Months")
		self.sumPCMonthOptions = OptionMenu(window1, self.sumPCMonth, "All Months", *self.uniqueMonths)
		self.sumPCMonthOptions.grid(row = 3, column = 2)

		# A button to create a pie chart that displays planned vs. unplanned purchases by count.
		self.pupPCButton = Button(window1, text = "View a Pie Chart for Planned vs. Unplanned Purchases", font = ("Helvetica", 13), command = self.ShowPUPPieChart)
		self.pupPCButton.grid(row = 4, column = 0)

		# A label that reads "Select a Month:". Filter for self.pupPCButton.
		self.pupPCLabel = Label(window1, text = "Select Month:", font = ("Helvetica", 13))
		self.pupPCLabel.grid(row = 4, column = 1)

		# An option menu that selects the month/year for self.pupPCButton.
		self.pupMonth = StringVar()
		self.pupMonth.set("All Months")
		self.pupMonthOptions = OptionMenu(window1, self.pupMonth, "All Months", *self.uniqueMonths)
		self.pupMonthOptions.grid(row = 4, column = 2)

		# A button that creates a frequency bar plot for payment types by count for this month.
		self.ptBarGraphButton = Button(window1, text = "View a Frequency Bar Plot for Payment Types", font = ("Helvetica", 13), command = self.showPtFreqBarPlot)
		self.ptBarGraphButton.grid(row = 5, column = 0)

		# A label that reads "Select a Month:". Filter for self.ptBarGraphButton.
		self.ptBarGraphLabel = Label(window1, text = "Select a Month:", font = ("Helvetica", 13))
		self.ptBarGraphLabel.grid(row = 5, column = 1)

		# An option menu that selects the month/year for self.ptBarGraphButton.
		self.ptMonth = StringVar()
		self.ptMonth.set("All Months")
		self.ptMonthOptions = OptionMenu(window1, self.ptMonth, "All Months", *self.uniqueMonths)
		self.ptMonthOptions.grid(row = 5, column = 2)

		# A Button that creates a heat map of spending 'concentrations' in a selected city.
		self.heatMapButton = Button(window1, text = "View a Heat Map of Spending by City", font = ("Helvetica", 13), command = self.showHeatMap)
		self.heatMapButton.grid(row = 6, column = 0)

		# A label that reads "Select a City:". Used for the heat map.
		self.filterByCityLabel = Label(window1, text = "Select a City:", font = ("Helvetica", 13))
		self.filterByCityLabel.grid(row = 6, column = 1)

		# An option menu for the cities in self.spendingData to base the heat map on (hm = heatmap).
		self.hmCity = StringVar()
		self.hmCity.set("Select a City:")
		self.hmCityOptions = OptionMenu(window1, self.hmCity, *self.uniqueCities)
		self.hmCityOptions.grid(row = 6, column = 2)

	"""Return a list of strings in the format 'City, State' of unique cities/states purchases were made on.
	   The city and state names come from the city/state a purchase was made in (i.e. per row)."""
	def getUniqueCities(self):
		if len(self.spendingData) == 0:
			return ["No City/State Found"]

		try:
			# Filter self.spendingData to remove city entries that equal 'No City Returned.'
			df = self.spendingData[self.spendingData['City'] != "No City Returned"]

			# Drop duplicates of cities (so it returns only unique cities.)
			df = df.drop_duplicates(subset = ['City'])

			cities = df['City'].tolist()
			states = df['State'].tolist()

			city_state = []

			# Combine the ith element of cities and states into the format 'city, state'.
			# Improved by using list comprehension.
			for i in range(0, len(cities)):
				city_state.append(cities[i] + ", " + states[i])

			return city_state

		except:
			showinfo("Error", "Heatmap City Options Error")
			return ["No City/State Found"]

	"""Return a list of unique month/years in self.spendingData (e.g. 3/17, 4/18, 5/18)."""
	def getUniqueMonths(self):
		return self.spendingData['Date'].dt.strftime("%m/%Y").drop_duplicates().tolist()

	"""Display a matplotlib graph of an overall spending trend graph, filtered by the selected month/year.
	   If there are multiple spendings in 1 day, those are grouped as an average (and used as the value for that day."""
	def showGeneralTrend(self):
		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")
			return

		if self.trendMonth.get() == "All Months":
			numEntries = str(len(self.spendingData))

			# Group self.spendingData by the average money spent per day.
			df = self.spendingData.groupby(['Date'], as_index = False).sum()

			title = "Total Monthly Spending Trend Graph for " + self.username + ": " + self.trendMonth.get()

		else:
			# Get the month and year as integers from the user's selected Month/Year string.
			selectedMonthYear = self.trendMonth.get().split("/")
			month = int(selectedMonthYear[0])
			year = int(selectedMonthYear[1])

			# Filter self.spendingData by the selected month and year.
			df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)

			numEntries = str(len(df))

			# Group by average money spent per day.
			df = df.groupby(['Date'], as_index = False).sum()

			title = "Total Daily Spending Trend Graph for " + self.username + ": " + self.trendMonth.get()

		# Display a matplotlib graph of the average monthly spending trend graph.
		fig, ax = plt.subplots()
		ax.plot(df['Date'], df['Amount'], marker = 'o', ls = '-')

		ax.set_title(title)
		ax.set_xlabel('Date')
		ax.set_ylabel('Spending Amount')

		plt.show()

	"""Display a matplotlib graph of an overall spending trend graph, filtered by category..
	   If there are multiple spendings in 1 day, those are grouped as an average (and used as the value for that day."""
	def showCategoryTrend(self):
		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")
			return

		# Filter self.spendingData by the selected category, then group by the average money spent per day.
		df = self.spendingData[self.spendingData['Category'] == self.trendCategory.get()].reset_index(drop = True)
		df = df.groupby(['Date'], as_index = False).sum()

		if len(df) == 0:
			showinfo("Error", "You have no spendings under " + self.trendCategory.get() + ".")
			return

		if len(df) == 1:
			showinfo("Error", "There is only 1 day of purchases under " + self.trendCategory.get() + "; there is no trend to display.")
			return

		min_day = df['Date'].min()
		max_day = df['Date'].max()

		months = mdates.MonthLocator()
		days = mdates.DayLocator()
		daysFmt = mdates.DateFormatter('%D')

		# Display a matplotlib graph of the average monthly spending trend graph, filtered by user-selected category.
		fig, ax = plt.subplots()
		ax.plot(df['Date'], df['Amount'], marker = 'o', ls = '-')

		# Adjust the x-axis (date axis) of this graph to follow a specific date format.
		ax.xaxis.set_major_locator(days)
		ax.xaxis.set_major_formatter(daysFmt)
		ax.xaxis.set_minor_locator(months)

		date_min = str(min_day.month) + "-" + str(min_day.day) + "-" + str(min_day.year)
		date_max = str(max_day.month) + "-" + str(max_day.day) + "-" + str(max_day.year)

		title = self.trendCategory.get() + ' Categorical Total Spending Trend Graph for ' + self.username + ": " + date_min + " to " + date_max

		ax.set_title(title)
		ax.set_xlabel('Date')
		ax.set_ylabel('Spending Amount')

		plt.show()

	"""Display a matplotlib graph of a spending count pie chart, organized by spending category."""
	def showCountCategoryPieChart(self):
		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")
			return

		if self.countPCMonth.get() == "All Months":
			df = self.spendingData.groupby(['Category'], as_index = False).count()

		else:
			selectedMonthYear = self.countPCMonth.get().split("/")
			month = int(selectedMonthYear[0])
			year = int(selectedMonthYear[1])

			df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)

			df = df.groupby(['Category'], as_index = False).count()

		labels = df['Category'].tolist()
		values = df['Amount'].tolist()

		fig, ax = plt.subplots()
		ax.pie(values, labels = labels, autopct='%1.1f%%', shadow=True, startangle=90)
		ax.axis('equal')

		title = "Spending Pie Chart for Number of Purchases in Categories for " + self.username + ": " + self.countPCMonth.get()

		ax.set_title(title)
		plt.legend(loc = 'best')

		plt.show()

	"""Display a matplotlib graph of a spending sum pie chart, organized by spending category."""
	def showSumCategoryPieChart(self):
		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")
			return

		if self.sumPCMonth.get() == "All Months":
			df = self.spendingData.groupby(['Category'], as_index = False).sum()

		else:
			selectedMonthYear = self.sumPCMonth.get().split("/")
			month = int(selectedMonthYear[0])
			year = int(selectedMonthYear[1])

			df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)

			df = df.groupby(['Category'], as_index = False).sum()

		labels = df['Category'].tolist()
		values = df['Amount'].tolist()

		fig, ax = plt.subplots()
		ax.pie(values, labels = labels, autopct='%1.1f%%', shadow=True, startangle=90)
		ax.axis('equal')

		title = "Spending Pie Chart for Amount in Purchases in Categories for " + self.username + ": " + self.sumPCMonth.get()

		ax.set_title(title)
		plt.legend(loc = 'best')

		plt.show()

	"""Display a matplotlib graph of a count pie chart, organized by number of planned vs. unplanned purchases."""
	def ShowPUPPieChart(self):
		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")
			return

		if self.pupMonth.get() == "All Months":
			df = self.spendingData.groupby(['Planned'], as_index = False).count()

		else:
			selectedMonthYear = self.pupMonth.get().split("/")
			month = int(selectedMonthYear[0])
			year = int(selectedMonthYear[1])

			df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)

			df = df.groupby(['Planned'], as_index = False).count()

		labels = df['Planned'].tolist()
		values = df['Amount'].tolist()
		labels[:] = ["Planned" if x == True else "Unplanned" for x in labels]

		fig, ax = plt.subplots()
		ax.pie(values, labels = labels, autopct='%1.1f%%', shadow=True, startangle=90)
		ax.axis('equal')

		title = "Pie Chart for Number of Planned vs. Unplanned Purchases for " + self.username + ": " + self.pupMonth.get()

		ax.set_title(title)
		plt.legend(loc = 'best')

		plt.show()

	"""Display a frequency plot for payment types."""
	def showPtFreqBarPlot(self):
		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")
			return

		if self.ptMonth.get() == "All Months":
			df = self.spendingData.groupby(['Payment Type'], as_index = False).count().reset_index(drop = True)

		else:
		 	selectedMonthYear = self.ptMonth.get().split("/")
		 	month = int(selectedMonthYear[0])
		 	year = int(selectedMonthYear[1])

		 	df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)

		 	df = df.groupby(['Payment Type'], as_index = False).count().reset_index(drop = True)

		labels = tuple(df['Payment Type'].tolist())
		values = df['Amount'].tolist()
		x = np.arange(len(values))

		title = "Frequency Plot for Different Payment Methods for " + self.username + ": " + self.ptMonth.get()

		fig, ax = plt.subplots()

		# Set the labels for the frequency bar plot.
		plt.bar(x, values)
		plt.xticks(x, labels)
		plt.yticks(range(min(values), math.ceil(max(values)) + 1))

		ax.set_title(title)
		ax.set_xlabel('Payment Type')
		ax.set_ylabel('Count')		

		plt.show()

	"""Create a heat map (in.html) using gmplot, based on the city that was selected in self.hmCityOptions.
	   The heat map is then displayed in a new tab of the default web browser."""
	def showHeatMap(self):
		if self.hmCity.get() == None or self.hmCity.get() == "Select a City:":
			showinfo("Error", "Please select a city.")
			return

		elif self.hmCity.get() == "No City/State Found":
			showinfo("Error", "There are no cities to display.")
			return

		# Split the selected city/state (in the form of City, State).
		city_state = self.hmCity.get().split(', ')

		# Filter self.spendingData by the user's selected city.
		df = self.spendingData[(self.spendingData['City'] == city_state[0]) & (self.spendingData['State'] == city_state[1])]

		latitudes = df['Latitude'].tolist()
		longitudes = df['Longitude'].tolist()

		gmap = gmplot.GoogleMapPlotter.from_geocode(self.hmCity.get())
		gmap.heatmap(latitudes, longitudes)

		# Filepath/name to save the heat map as. Saved inside data/users/USERNAME/graphics.
		filename = "data/users/" + self.username + "/graphics/" + city_state[0] + "-heatmap.html"

		# Generate the heat map, then open up the default browser to display it.
		# Currently, there is no way to display non-simple html files in a native tkinter window.
		gmap.draw(filename)
		webbrowser.open("file://" + os.path.realpath(filename))

	"""Create a new window (Toplevel()) that contains all necessary buttons and widgets for a spending prediction page.
	   All subsequent functions before createBudgetPage are related to this page."""
	def createPredictionPage(self):
		if self.logged_in == False:
			showinfo("Error", "Please create a new user or select an existing user first.")
			return

		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")
			return

		# Get today's month and year as strings, and calculate the number of days left in this month.
		today = datetime.today()
		thisMonth = utils.num_to_month[str(today.month)]
		thisYear = str(today.year)
		days_left = utils.days_in_month[str(today.month)] - today.day + 1

		spending_categories = ["Consumer Debt", "Entertainment", "Food & Groceries", "Healthcare", "Housing",
							"Luxury", "Misc. Expenses", "Personal Care", "Savings", "Utilities"]

		window = Toplevel()
		window.title("Spending Predictions")

		# A label that displays the username, this month, and this year.
		self.predPageLabel = Label(window, text = "Spending Predictions for " + self.username + ": " + thisMonth + " of " + thisYear, font = ("Helvetica", 16))
		self.predPageLabel.grid(row = 0, column = 0)

		# Check if there's only 1 day left in this month (trivial grammatical peeves).
		if days_left <= 1:
			self.numDaysLeftLabel = Label(window, text = "There is " + str(days_left) + " day left in " + thisMonth + ".", font = ("Helvetica", 14))
			self.numDaysLeftLabel.grid(row = 1, column = 0)

		else:
			self.numDaysLeftLabel = Label(window, text = "There are " + str(days_left) + " days left in " + thisMonth + ".", font = ("Helvetica", 14))
			self.numDaysLeftLabel.grid(row = 1, column = 0)

		# A button that displays spending predictions for the rest of the month.
		# Feature still being tested/improved on.
		self.mainPredictionButton = Button(window, text = "Predict My Overall Daily Spendings for the Rest of " + thisMonth, font = ("Helvetica", 13), command = self.dailyOverallPrediction)
		self.mainPredictionButton.grid(row = 2, column = 0)

		# A button that displays spending predictions for the rest of the month, filtered by spending category.
		# Feature still being tested/improved on.
		self.categoryPredButton = Button(window, text = "Predict My Spendings for " + thisMonth + " by Spending Category", font = ("Helvetica", 13), command = self.categoryPrediction)
		self.categoryPredButton.grid(row = 3, column = 0)

		# A button that predicts whether or not the current user will be overbudget by the end of the month, based on their current rate of spending.
		# Feature still being tested/improved on.
		# Since spending rates are so unpredictable, this feature is more of a fun "gimmick" than an accurate representation.
		self.predictSpendingBudgetButton = Button(window, text = "Will I be over-budget by the end of " + utils.num_to_month[str(today.month)] + "?",
													font = ("Helvetica", 13), command = self.predictOverBudget)
		self.predictSpendingBudgetButton.grid(row = 4, column = 0)

		# More to be added.

	"""Display a new tkinter text window that displays daily spending predictions for the rest of the month."""
	def dailyOverallPrediction(self):

		# Check if self.spendingData has enough entries.
		if len(self.spendingData) < 6:
			showinfo("Error", "You do not have enough spending entries for " + utils.num_to_month[str(month)] + " to use this feature (minimum # of entries required: N).")
			return

		# Get today's day/month/year, and the number of days left in the current month.
		today = datetime.today()
		thisDay = today.day
		month = today.month
		year = today.year
		thisMonth = utils.num_to_month[str(month)]
		days_left = utils.days_in_month[str(month)] - today.day + 1

		# Sort self.spendingData by today's month, and get the 'Amount' column as a matrix.
		df = self.spendingData[self.spendingData['Date'].dt.month == month].set_index('Date', drop = True)
		amount = df['Amount'].as_matrix()

		spentSoFar = sum(amount)

		# Use Pyramid's auto_arima() function to find the optimal p, d, q values for the time series model.
		stepwise_fit = auto_arima(amount, start_p=1, start_q=1, max_p=3, max_q=3, m=12,
                         start_P=0, seasonal=True, d=1, D=1, trace=True,
                         error_action='ignore',  # don't want to know if an order does not work
                         suppress_warnings=True,  # don't want convergence warnings
                         stepwise=True)  # set to stepwise

		# Use Pyramid's predict() function to forecast spending values for the number of days left this month.
		predictions = stepwise_fit.predict(n_periods = days_left)

		window = Toplevel()
		window.title("Daily Overall Predictions")

		t = Text(window, font = ("Helvetica", 14))

		t.insert(END, "Spending Predictions for the Remainder of " + thisMonth + " :" + '\n' + '\n')

		for i in range(0, len(predictions)):
			n = thisDay + i
			t.insert(END, thisMonth + " " + str(n) + ": $" + str(abs(round(predictions[i], 2))) + '\n')

		t.insert(END, '\n' + "Total Spent in May: $" + str(round(spentSoFar + (sum(predictions)), 2)) + '\n')

		t.pack()

	"""Not Yet Implemented."""
	def categoryPrediction(self):
		showinfo("Error", "Not Yet Implemented.")
		return

	"""Open a new tkinter window that displays predictions for whether or not the current user will be overbudget by the end of the month.
	   See self.predictSpendingBudgetButton's comments for additional details.
	   This function follows the exact same structure as the other prediction functions used in self.createPredictionPage."""
	def predictOverBudget(self):
		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")
			return

		today = datetime.today()
		thisDay = today.day
		month = today.month
		year = today.year
		budget = int(self.currentBudget[2])
		thisMonth = utils.num_to_month[str(month)]
		days_left = utils.days_in_month[str(month)] - today.day + 1

		df = self.spendingData[self.spendingData['Date'].dt.month == month].reset_index(drop = True)

		if len(df) < 6:
			showinfo("Error", "You do not have enough spending entries for " + utils.num_to_month[str(month)] + " to use this feature (minimum # of entries required: 6).")
			return

		amount = df['Amount'].as_matrix()

		spentSoFar = sum(amount)

		stepwise_fit = auto_arima(amount, start_p=1, start_q=1, max_p=3, max_q=3, m=12,
                         start_P=0, seasonal=True, d=1, D=1, trace=True,
                         error_action='ignore',  # don't want to know if an order does not work
                         suppress_warnings=True,  # don't want convergence warnings
                         stepwise=True)  # set to stepwise

		predictions = stepwise_fit.predict(n_periods = days_left)

		total_spent = sum(predictions)
		theoretical_spending = spentSoFar + total_spent

		# A way to get predictions using ARIMA(p, d, q) in statsmodels.

		# amount = df['Amount']

		# spentSoFar = sum(amount.tolist())

		# differenced = utils.difference(amount, 1)

		# model = ARIMA(differenced, order = (1, 0, 1))
		# model_fit = model.fit()

		# forecast = model_fit.forecast(steps = days_left)[0]
		# history = [x for x in amount]

		# day = 1
		# forecast_list = []

		# for yhat in forecast:
		# 	inverted = utils.inverse_difference(history, yhat, 1)
		# 	forecast_list.append(inverted)
		# 	history.append(inverted)
		# 	day += 1

		# forecast_list = [abs(x) for x in forecast_list]

		# prediction_total = sum(forecast_list)
		# total_theo_spending = spentSoFar + prediction_total    # Total theoretical spending amount.

		showinfo("Warning", "The accuracy of this feature depends on the number of entries you have for this month.")

		predWindow = Toplevel()
		predWindow.title("Budget Predictions")

		# A label that tells the user whether or not they will be over/underbudget by X dollars. Initially empty.
		predictionLabel = Label(predWindow, text = "", font = ("Helvetica", 14))
		predictionLabel.pack()

		# Calculate if the user will be over/underbudget by X dollars, then display the corresponding text.
		if theoretical_spending <= budget:
			predictionLabel['text'] = "At your current rate of spending, You will be $" + str(round(budget - theoretical_spending, 2)) + " under budget by the end of " + thisMonth + "."

		elif theoretical_spending > budget:
			predictionLabel['text'] = "At your current rate of spending, You will be $" + str(round(theoretical_spending - budget, 2)) + " over budget by the end of " + thisMonth + "."

	"""Create a new window (Toplevel()) that contains all necessary buttons and widgets for budget management.
	   All subsequent functions before self.createProfilePage are related to this page."""
	def createBudgetPage(self):
		today = datetime.today()
		thisYearMonth = str(today.year) + "-" + str(today.month)

		# Get the current month, year, and budget amount from self.currentBudget.
		savedMonth = int(self.currentBudget[0])
		savedYear = int(self.currentBudget[1])
		savedAmount = int(self.currentBudget[2])

		if self.logged_in == False:
			showinfo("Error", "Please create a new user or select an existing user first.")
			return

		# Check if the user ever set a budget (i.e. if a user is new).
		elif len(self.budgetData) == 0:
			question = "You have not set a budget yet. What is your budget for " + utils.num_to_month[str(today.month)] + " of " + str(today.year) + "?"

			amount = simpledialog.askinteger("Set a Budget", question, minvalue = 0)

			if amount == None:
				return

			# Update self.currentBudget with today's month/year, and the budget amount chosen by the user.
			# Then, update the necessary files in data/users/USERNAME.
			self.currentBudget = [str(today.month), str(today.year), str(amount)]
			self.updateCurrentBudget()
			self.addToBudgetData()

		# Check if a new month has started. If true, then ask the user for a new budget amount for the new month,
		# and update the necessary files.
		elif savedMonth + savedYear != today.month + today.year:
			question = "Please create a new budget for " + utils.num_to_month[str(today.month)] + " of " + str(today.year) + "."

			amount = simpledialog.askinteger("Set a Budget", question, minvalue = 0)

			if amount == None:
				return

			self.currentBudget = [str(today.month), str(today.year), str(amount)]
			self.updateCurrentBudget()
			self.addToBudgetData()

		window3 = Toplevel()
		window3.title("Manage Your Budget")

		# A label that displays the user's current budget for this month.
		self.currentBudgetAmountLabel = Label(window3, text = "Your budget for " + utils.num_to_month[str(today.month)] + " of " + str(today.year) + " is $" + str(self.currentBudget[2]) + ".",
												font = ("Helvetica", 14))
		self.currentBudgetAmountLabel.grid(row = 0, column = 0)

		# A label that displays the total amount of money the user spent this month.
		self.amountSpentLabel = Label(window3, text = "You have spent $" + str(self.amountSpentThisMonth()) + " so far in " + utils.num_to_month[str(today.month)] + ".", font = ("Helvetica", 14))
		self.amountSpentLabel.grid(row = 1, column = 0)

		# A label that displays the user's remaining budget for this month.
		self.remainingBudgetLabel = Label(window3, text = "You have $" + str(int(self.currentBudget[2]) - self.amountSpentThisMonth()) + " remaining in your budget.",
												font = ("Helvetica", 14))
		self.remainingBudgetLabel.grid(row = 2, column = 0)

		# Check if there is 1 day left in the month. Trivial grammatical peeve.
		if utils.days_in_month[str(today.month)] - today.day > 1:
			self.remainingDaysLabel = Label(window3, text = "There are " + str(utils.days_in_month[str(today.month)] - today.day + 1) + " days left in " + utils.num_to_month[str(today.month)] + ".",
												font = ("Helvetica", 14))
			self.remainingDaysLabel.grid(row = 3, column = 0)

		else:
			self.remainingDaysLabel = Label(window3, text = "There is " + str(utils.days_in_month[str(today.month)] - today.day + 1) + " day left in " + utils.num_to_month[str(today.month)] + ".",
												font = ("Helvetica", 14))
			self.remainingDaysLabel.grid(row = 3, column = 0)			

		# A button for changing the user's budget for this month.
		self.changeBudgetButton = Button(window3, text = "Change My Budget for " + utils.num_to_month[str(today.month)], font = ("Helvetica", 13), command = self.changeBudget)
		self.changeBudgetButton.grid(row = 4, column = 0)

		# A button that displays a trend graph for cumulative daily spendings for this month alongside a horizontal line for this month's budget amount.
		self.compareSpendingBudgetButton = Button(window3, text = "Show My Spending vs. My Budget for " + utils.num_to_month[str(today.month)],
													font = ("Helvetica", 13), command = self.compareSpendingBudget)
		self.compareSpendingBudgetButton.grid(row = 5, column = 0)

		# Show budget trend graph for all the user's budgets from previous months.
		self.showBudgetTrendButton = Button(window3, text = "Display a Trend Graph for All My Budgets", font = ("Helvetica", 13), command = self.showBudgetTrend)
		self.showBudgetTrendButton.grid(row = 7, column = 0)

	"""Update the budget information displayed in all the labels on the budget page.
	   This function is what makes the labels dynamic."""
	def updateBudgetPageInfo(self):
		today = datetime.today()
		self.currentBudgetAmountLabel['text'] = "Your budget for " + utils.num_to_month[str(today.month)] + " of " + str(today.year) + " is $" + str(self.currentBudget[2]) + "."
		self.remainingBudgetLabel['text'] = "You have $" + str(int(self.currentBudget[2]) - self.amountSpentThisMonth()) + " remaining for this month."

	"""Update the user's current budget in the .txt file containing the user's budget information."""
	def updateCurrentBudget(self):
		with open("data/users/" + self.username + "/" + self.username + "-currentbudget.txt", "wb") as fp:
			pickle.dump(self.currentBudget, fp)

	"""Return the amount of money spent by the user this month."""
	def amountSpentThisMonth(self):
		if len(self.spendingData) == 0:
			return 0

		today = datetime.today()
		thisYearMonth = str(today.year) + "-" + str(today.month)

		df = self.spendingData.set_index('Date').groupby(pd.Grouper(freq='M')).sum()

		return df[thisYearMonth].iloc[0]['Amount']

	"""Add this month's budget information to self.budgetData."""
	def addToBudgetData(self):
		tempDF = pd.DataFrame({'Month': [str(self.currentBudget[0])], 'Year': [str(self.currentBudget[1])], 'Amount': [int(self.currentBudget[2])]})
		self.budgetData = self.budgetData.append(tempDF).reset_index(drop = True)

		self.budgetData.to_pickle(self.userBudgetFilePath)

	"""Change the user's budget for this month, and update the necessary files that contain the user's budget information."""
	def changeBudget(self):
		today = datetime.today()

		try:
			question = "What is your new budget for " + utils.num_to_month[str(today.month)] + " of " + str(today.year) + "?"
			newAmount = simpledialog.askinteger("Change Your Budget", question, minvalue = 0)

			if newAmount == None:
				return

			# Update self.currentBudget and self.budgetData with the new budget, and update the necessary files.
			self.currentBudget[2] = str(newAmount)
			self.budgetData.at[len(self.budgetData) - 1, 'Amount'] = newAmount

			self.updateCurrentBudget()
			self.budgetData.to_pickle(self.userBudgetFilePath)

			self.updateBudgetPageInfo()

			showinfo("Change Successful", "You have changed your " + utils.num_to_month[str(today.month)] + " budget to $" + str(newAmount) + ".")

		except:
			showinfo("Error", "Change Budget Error")
			return

	"""Display a matplotlib graph that displays the user's cumulative daily spending vs. this month's budget as a horizontal line.
	   This function follows a very similar structure to all the other graph-displaying functions used in self.createVisPage."""
	def compareSpendingBudget(self):
		month = datetime.today().month
		stringMonth = utils.num_to_month[str(month)]
		year = datetime.today().year
		amount = int(self.currentBudget[2])

		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")
			return

		# Filter self.spendingData by today's month and year, and group elements by Date.
		df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)
		df = df.groupby('Date', as_index = False).sum()

		if len(df) == 0:
			showinfo("Error", "Your spending dataset is empty for " + utils.num_to_month[str(month)] + ".")
			return

		elif len(df) == 1:
			showinfo("Error", "You only have 1 spending in " + stringMonth + ". There is no trend to display.")
			return

		spendingLine = df[['Amount']].cumsum()['Amount'].tolist()

		min_day = df['Date'].min()
		max_day = df['Date'].max()

		months = mdates.MonthLocator()
		days = mdates.DayLocator()
		daysFmt = mdates.DateFormatter('%D')

		date_min = str(min_day.month) + "-" + str(min_day.day) + "-" + str(min_day.year)
		date_max = str(max_day.month) + "-" + str(max_day.day) + "-" + str(max_day.year)

		fig, ax = plt.subplots()
		ax.plot(df['Date'], spendingLine, label = "Total Spending for " + stringMonth, marker = 'o', ls = '-')

		title = "Total Spending vs. Budget Graph for " + self.username + ": " + date_min + " to " + date_max

		ax.set_title(title)
		ax.set_xlabel('Date')
		ax.set_ylabel('Total Spending')

		plt.axhline(y = amount, color = 'r', ls = 'solid', label = 'Budget for ' + stringMonth)
		plt.legend()
		plt.show() 

	"""Show a trend graph of all the budgets of previous months.
	   Does not display anything is the user has only 1 entry (i.e. if the user has been active for only 1 month)."""
	def showBudgetTrend(self):
		amounts = self.budgetData['Amount'].tolist()
		months = self.budgetData[['Month', 'Year']].apply(lambda x: '-'.join(x), axis = 1).tolist()
		months_as_dt = [datetime.strptime(x, '%m-%Y') for x in months]

		if len(self.budgetData) == 1:
			showinfo("Error", "You only have 1 budget entry for $" + str(amounts[0]) + " in " + months[0] + ".")
			return

		fig, ax = plt.subplots()

		ax.plot(months_as_dt, amounts, marker = 'o', ls = '-')

		title = "All Budget Amounts for " + self.username + ": " + months[0] + " to " + months[len(months) - 1]

		ax.set_title(title)
		ax.set_xlabel('Date')
		ax.set_ylabel('Budget Amount')

		plt.show()

	"""Create a new window (Toplevel()) that contains all necessary buttons and widgets for a personal spending profile."""
	def createProfilePage(self):
		if self.logged_in == False:
			showinfo("Error", "Please create a new user or select an existing user first.")
			return

		if len(self.spendingData) == 0:
			showinfo("Error", "Your spending dataset is empty.")
			return

		window2 = Toplevel()
		window2.title("Your Spending Profile")

		# Get all the unique months (Month/Year) the user has spending data on.
		self.uniqueMonths = self.getUniqueMonths()

		# An option menu for the user to select one of the months from uniqueMonths.
		self.selectedMonth = StringVar()
		self.selectedMonth.set("All Months")
		self.selectedMonthOptions = OptionMenu(window2, self.selectedMonth, "All Months", *self.uniqueMonths)
		self.selectedMonthOptions.pack()

		# A refresh button that re-displays the spending profile information based on the month selected in self.selectedMonthOptions.
		self.refreshButton = Button(window2, text = "Refresh", font = ("Helvetica", 13), command = self.updateSpendingProfile)
		self.refreshButton.pack()

		# A label that displays the user's average amount of money spent per day during the selected month/year.
		self.avgDaySpendingLabel = Label(window2, text = "Average Amount of Money Spent Per Day: $" + self.getAvgDailySpending(), font = ("Helvetica", 14))
		self.avgDaySpendingLabel.pack()

		# Get the most/least expensive purchases, categories with the most/least number of purchases and amount spent,
		# most/least used payment types, and number of planned and unplanned purchases (during the selected month/year).
		most_least_purchase = self.getMostLeastExpPurchase()
		most_least_category_count = self.getMostLeastCategoryCount()
		most_least_category_amount = self.getMostLeastCategoryAmount()
		most_least_payment_type = self.getMostLeastPaymentType()
		most_least_city = self.getMostLeastCity()
		num_pup = self.getNumPup()

		# A label that displays the user's most expensive purchase during the selected month/year.
		self.mostExpPurchase = Label(window2, text = "My Most Expensive Purchase: " + most_least_purchase[0], font = ("Helvetica", 14))
		self.mostExpPurchase.pack()

		# A label that displays the user's least expensive purchase during the selected month/year.
		self.leastExpensivePurchase = Label(window2, text = "My Least Expensive Purchase: " + most_least_purchase[1], font = ("Helvetica", 14))
		self.leastExpensivePurchase.pack()

		# A label that displays the user's spending category with the most number of purchases during the selected month/year.
		self.mostSpentCategoryCount = Label(window2, text = "Spending Category with Most Number of Spendings: " + most_least_category_count[0], font = ("Helvetica", 14))
		self.mostSpentCategoryCount.pack()

		# A label that displays the user's spending category with the least number of purchases during the selected month/year.
		self.leastSpentCategoryCount = Label(window2, text = "Spending Category with Least Number of Spendings: " + most_least_category_count[1], font = ("Helvetica", 14))
		self.leastSpentCategoryCount.pack()

		# A label that displays the user's spending category with the most amount of money spent during the selected month/year.
		self.mostSpentCategoryAmount = Label(window2, text = "Spending Category with Most Amount of Money Spent: " + most_least_category_amount[0], font = ("Helvetica", 14))
		self.mostSpentCategoryAmount.pack()

		# A label that displays the user's spending category with the least amount of money spent during the selected month/year.
		self.leastSpentCategoryAmount = Label(window2, text = "Spending Category with Least Amount of Money Spent: " + most_least_category_amount[1], font = ("Helvetica", 14))
		self.leastSpentCategoryAmount.pack()

		# A label that displays the user's most frequently used payment type during the selected month/year.
		self.mostUsedPaymentType = Label(window2, text = "My Most Used Payment Type: " + most_least_payment_type[0], font = ("Helvetica", 14))
		self.mostUsedPaymentType.pack()

		# A label that displays the user's least frequently used payment type during the selected month/year.
		self.leastUsedPaymentType = Label(window2, text = "My Least Used Payment Type: " + most_least_payment_type[1], font = ("Helvetica", 14))
		self.leastUsedPaymentType.pack()

		# A label that displays the city/state the user spent the most money on during the selected month/year.
		self.mostSpentCity = Label(window2, text = "City Where I Spent the Most: " + most_least_city[0], font = ("Helvetica", 14))
		self.mostSpentCity.pack()

		# A label that displays the city/state the user spent the least money on during the selected month/year.
		self.leastSpentCity = Label(window2, text = "City Where I Spent the Least: " + most_least_city[1], font = ("Helvetica", 14))
		self.leastSpentCity.pack()

		# A label that displays the user's number of planned purchases during the selected month/year.
		self.numPlannedPurchases = Label(window2, text = "Number of Planned Purchases: " + num_pup[0], font = ("Helvetica", 14))
		self.numPlannedPurchases.pack()

		# A label that displays the user's number of unplanned purchases during the selected month/year.
		self.numUnplannedPurchases = Label(window2, text = "Number of Unplanned Purchases: " + num_pup[1], font = ("Helvetica", 14))
		self.numUnplannedPurchases.pack()

	"""Update the information in the labels in the spending profile page (reactive to the refresh button)."""
	def updateSpendingProfile(self):

		# Get the most/least expensive purchases, categories with the most/least number of purchases and amount spent,
		# most/least used payment types, and number of planned and unplanned purchases (during the selected month/year).
		most_least_purchase = self.getMostLeastExpPurchase()
		most_least_category_count = self.getMostLeastCategoryCount()
		most_least_category_amount = self.getMostLeastCategoryAmount()
		most_least_payment_type = self.getMostLeastPaymentType()
		most_least_city = self.getMostLeastCity()
		num_pup = self.getNumPup()

		# Update the labels in self.createProfilePage upon the user clicking the refresh button.
		self.avgDaySpendingLabel['text'] = "Average Amount of Money Spent Per Day: $" + self.getAvgDailySpending()
		self.mostExpPurchase['text'] = "My Most Expensive Purchase: " + most_least_purchase[0]
		self.leastExpensivePurchase['text'] = "My Least Expensive Purchase: " + most_least_purchase[1]
		self.mostSpentCategoryCount['text'] = "Spending Category with Most Number of Spendings: " + most_least_category_count[0]
		self.leastSpentCategoryCount['text'] = "Spending Category with Least Number of Spendings: " + most_least_category_count[1]
		self.mostSpentCategoryAmount['text'] = "Spending Category with Most Amount of Money Spent: " + most_least_category_amount[0]
		self.leastSpentCategoryAmount['text'] = "Spending Category with Least Amount of Money Spent: " + most_least_category_amount[1]
		self.mostUsedPaymentType['text'] = "My Least Used Payment Type: " + most_least_payment_type[0]
		self.leastUsedPaymentType['text'] = "My Least Used Payment Type: " + most_least_payment_type[1]
		self.mostSpentCity['text'] = "City Where I Spent the Most: " + most_least_city[0]
		self.leastSpentCity['text'] = "City Where I Spent the Least: " + most_least_city[1]
		self.numPlannedPurchases['text'] = "Number of Planned Purchases: " + num_pup[0]
		self.numUnplannedPurchases['text'] = "Number of Unplanned Purchases: " + num_pup[1]

	"""Return the average amount of money spent per day during the selected month/year in self.selectedMonthOptions."""
	def getAvgDailySpending(self):
		if self.selectedMonth.get() == "All Months":

			return str(round(self.spendingData['Amount'].mean(), 2))

		selectedMonthYear = self.selectedMonth.get().split("/")
		month = int(selectedMonthYear[0])
		year = int(selectedMonthYear[1])

		df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)

		return str(round(df['Amount'].mean(), 2))

	"""Return the most and least expensive purchases as strings (in that order) during the selected month/year in a list."""
	def getMostLeastExpPurchase(self):
		if self.selectedMonth.get() == "All Months":

			# Sort self.spendingData by spending amounts, in descending order.
			df = self.spendingData.sort_values('Amount', ascending = False).reset_index(drop = True)

			# Get the purchase date, city, and state for most expensive purchase.
			most_exp_date = df.at[0, 'Date'].strftime('%m/%d/%Y')
			most_exp_city = df.at[0, 'City']
			most_exp_state = df.at[0, 'State']

			# Get the purchase date, city, and state for least expensive purchase.
			least_exp_date = df.at[len(df) - 1, 'Date'].strftime('%m/%d/%Y')
			least_exp_city = df.at[len(df) - 1, 'City']
			least_exp_state = df.at[len(df) - 1, 'State']

			most = df.at[0, 'Description'] + " for $" + str(df.at[0, 'Amount']) + " on " + most_exp_date + " at " + most_exp_city + ", " + most_exp_state + "."
			least = df.at[len(df) - 1, 'Description'] + " for $" + str(df.at[len(df) - 1, 'Amount']) + " on " + least_exp_date + " at " + least_exp_city + ", " + least_exp_state + "."

			return [most, least]

		# Get the selected month/year in self.selectedMonthOptions.
		selectedMonthYear = self.selectedMonth.get().split("/")
		month = int(selectedMonthYear[0])
		year = int(selectedMonthYear[1])

		df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)
		df = df.sort_values('Amount', ascending = False).reset_index(drop = True)

		most_exp_date = df.at[0, 'Date'].strftime('%m/%d/%Y')
		most_exp_city = df.at[0, 'City']
		most_exp_state = df.at[0, 'State']

		least_exp_date = df.at[len(df) - 1, 'Date'].strftime('%m/%d/%Y')
		least_exp_city = df.at[len(df) - 1, 'City']
		least_exp_state = df.at[len(df) - 1, 'State']

		most = df.at[0, 'Description'] + " for $" + str(df.at[0, 'Amount']) + " on " + most_exp_date + " at " + most_exp_city + ", " + most_exp_state + "."
		least = df.at[len(df) - 1, 'Description'] + " for $" + str(df.at[len(df) - 1, 'Amount']) + " on " + least_exp_date + " at " + least_exp_city + ", " + least_exp_state + "."

		return [most, least]

	"""Return the categories with most and least number of purchases made (in that order) as strings during the selected month/year, in a list."""
	def getMostLeastCategoryCount(self):
		if self.selectedMonth.get() == "All Months":

			df = self.spendingData.groupby(['Category'], as_index = False).count().sort_values('Amount', ascending = False).reset_index(drop = True)


			most = df.at[0, 'Category'] + " with " + str(df.at[0, 'Amount']) + " spending(s)."
			least = df.at[len(df) - 1, 'Category'] + " with " + str(df.at[len(df) - 1, 'Amount']) + " spending(s)."

			return [most, least]

		selectedMonthYear = self.selectedMonth.get().split("/")
		month = int(selectedMonthYear[0])
		year = int(selectedMonthYear[1])

		df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)
		df = df.groupby(['Category'], as_index = False).count().sort_values('Amount', ascending = False).reset_index(drop = True)

		most = df.at[0, 'Category'] + " with " + str(df.at[0, 'Amount']) + " spendings(s)."
		least = df.at[len(df) - 1, 'Category'] + " with " + str(df.at[len(df) - 1, 'Amount']) + " spending(s)."

		return [most, least]

	"""Return the categories with most and least amount of money spent on (in that order) as strings during the selected month/year, in a list."""
	def getMostLeastCategoryAmount(self):
		if self.selectedMonth.get() == "All Months":

			df = self.spendingData.groupby(['Category'], as_index = False).sum().sort_values('Amount', ascending = False).reset_index(drop = True)

			most = df.at[0, 'Category'] + " with $" + str(df.at[0, 'Amount']) + " spent."
			least = df.at[len(df) - 1, 'Category'] + " with $" + str(df.at[len(df) - 1, 'Amount']) + " spent."

			return [most, least]

		selectedMonthYear = self.selectedMonth.get().split("/")
		month = int(selectedMonthYear[0])
		year = int(selectedMonthYear[1])

		df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)
		df = df.groupby(['Category'], as_index = False).sum().sort_values('Amount', ascending = False).reset_index(drop = True)

		most = df.at[0, 'Category'] + " with $" + str(df.at[0, 'Amount']) + " spent."
		least = df.at[len(df) - 1, 'Category'] + " with $" + str(df.at[len(df) - 1, 'Amount']) + " spent."

		return [most, least]

	"""Return the most and least used payment types (in that order) as strings during the selected month/year, in a list."""
	def getMostLeastPaymentType(self):
		if self.selectedMonth.get() == "All Months":

			df = self.spendingData.groupby(['Payment Type'], as_index = False).count().sort_values('Amount', ascending = False).reset_index(drop = True)

			most = df.at[0, 'Payment Type'] + " with " + str(df.at[0, 'Amount']) + " purchase(s)."
			least = df.at[len(df) - 1, 'Payment Type'] + " with " + str(df.at[len(df) - 1, 'Amount']) + " purchase(s)."

			return [most, least]

		selectedMonthYear = self.selectedMonth.get().split("/")
		month = int(selectedMonthYear[0])
		year = int(selectedMonthYear[1])

		df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)
		df = df.groupby(['Payment Type'], as_index = False).count().sort_values('Amount', ascending = False).reset_index(drop = True)

		most = df.at[0, 'Payment Type'] + " with " + str(df.at[0, 'Amount']) + " purchase(s)."
		least = df.at[len(df) - 1, 'Payment Type'] + " with " + str(df.at[len(df) - 1, 'Amount']) + " purchase(s)."

		return [most, least]

	"""Return the cities with most and least amount of money spent in (in that order) as strings during the selected month/year, in a list."""
	def getMostLeastCity(self):
		if self.selectedMonth.get() == "All Months":

			# Add a new column 'City, State' to df where the values are the rows' city and state combined (e.g. 'Berkeley' and 'CA' become 'Berkeley, CA'.)
			df = self.spendingData.reset_index(drop = True)
			df['City, State'] = df[['City', 'State']].apply(lambda x: ", ".join(x), axis = 1)
			df = df.groupby(['City, State'], as_index = False).sum().sort_values('Amount', ascending = False).reset_index(drop = True)

			most = df.at[0, 'City, State'] + " with $" + str(round(df.at[0, 'Amount'], 2)) + " spent."
			least = df.at[len(df) - 1, 'City, State'] + " with $" + str(round(df.at[len(df) - 1, 'Amount'], 2)) + " spent."

			return [most, least]

		selectedMonthYear = self.selectedMonth.get().split("/")
		month = int(selectedMonthYear[0])
		year = int(selectedMonthYear[1])

		df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)
		df['City, State'] = df[['City', 'State']].apply(lambda x: ", ".join(x), axis = 1)
		df = df.groupby(['City, State'], as_index = False).sum().sort_values('Amount', ascending = False).reset_index(drop = True)

		most = df.at[0, 'City, State'] + " with $" + str(round(df.at[0, 'Amount'], 2)) + " spent."
		least = df.at[len(df) - 1, 'City, State'] + " with $" + str(round(df.at[len(df) - 1, 'Amount'], 2)) + " spent."

		return [most, least]

	"""Get the number of planned and unplannd purchases (in that order) as strings during the selected month/year, in a list."""
	def getNumPup(self):
		if self.selectedMonth.get() == "All Months":

			# Sort self.spendingData by Planned (boolean True) counts.
			df = self.spendingData.groupby(['Planned'], as_index = False).count().reset_index(drop = True)

			# Check if there's only either planned or unplanned purchases.
			# Then, check if it is unplanned.
			if len(df) == 1:
				if df.at[0, 'Planned'] == False:
					unplanned = str(df.at[0, 'Amount'])
					planned = str(0)

				planned = str(df.at[0, 'Amount'])
				unplanned = str(0)

				return [planned, unplanned]

			unplanned = str(df.at[0, 'Amount'])
			planned = str(df.at[1, 'Amount'])

			return [planned, unplanned]

		selectedMonthYear = self.selectedMonth.get().split("/")
		month = int(selectedMonthYear[0])
		year = int(selectedMonthYear[1])

		df = self.spendingData[(self.spendingData['Date'].dt.month == month) & (self.spendingData['Date'].dt.year == year)].reset_index(drop = True)
		df = df.groupby(['Planned'], as_index = False).count().reset_index(drop = True)

		if len(df) == 1:
			if df.at[0, 'Planned'] == False:
				unplanned = str(df.at[0, 'Amount'])
				planned = str(0)

			planned = str(df.at[0, 'Amount'])
			unplanned = str(0)

			return [planned, unplanned]

		unplanned = str(df.at[0, 'Amount'])
		planned = str(df.at[1, 'Amount'])

		return [planned, unplanned]


# Run the application.
root = Tk()
root.title("Dollars: Your Personal Finance Manager")
app = Dollars(root)

while True:
	try:
		root.mainloop()
		break
	except UnicodeDecodeError: # Added to avoid the program crashing when scrolling.
		pass
