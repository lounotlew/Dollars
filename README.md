## Dollars - Personal Finance Management, Visualization, and Prediction
###### Written by Lewis Kim

### Description

Dollars is a personal finance manager, visualizer, and predictor, written in Python (3.6). Dollars allows any user to log and manage their personal spending data in a very organized way (e.g. spending amount, location, date, category, etc.), and uses the data to track and analyze the user's monthly budget. Dollars also allows users to visualize and examine their spendings for the current month through spending trend graphs, pie charts, frequency barplots, and heat maps. Users can also choose to forecast their spendings (overall or by spending category) for the rest of the month using a time series ARIMA model, which can also predict whether or not a user will be over or underbudget for the month.

### Installation

Dollars was written in Python 3.6, and may not work with Python 2.

Required packages:
- ``tkinter`` (included with Python 3)
- ``matplotlib`` (pip install: ``pip3 install matplotlib``)
- ``pandas`` (pip install: ``pip3 install pandas``)
- ``pandastable`` (pip install: ``pip3 install pandastable``)
- ``scipy``/``numpy`` (pip install: ``pip3 install scipy numpy``)
- ``geopy`` (pip install: ``pip3 install geopy``)
- ``gmplot`` (pip install: ``pip3 install gmplot``)
- ``statsmodels`` (pip install: ``pip3 install statsmodels``)
- ``pyramid-arima`` (pip install: ``pip3 install pyramid-arima``)

For a GUI sample and applet walkthrough, click this [link](gui_sample/README.md).

To run this application (after installing all required packages), type the following command in terminal/bash in the directory inside the Dollars folder:

```
python3 gui.py
```
