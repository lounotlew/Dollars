# Dollars - Personal Finance Management, Visualization, and Prediction
> Written by Lewis Kim

### Description

Dollars is a personal finance manager, visualizer, and predictor, using ``tkinter`` as its GUI framework. Dollars allows any user to log and manage their personal spending data in a very organized way (e.g. spending amount, location, date, category, etc.), and uses the data to track and analyze the user's monthly budget. Dollars also allows users to visualize and examine their spendings for the current month through spending trend graphs, pie charts, frequency barplots, and heat maps. Users can also choose to forecast their spendings (overall or by spending category) for the rest of the month using a time series ARIMA model, which can also predict whether or not a user will be over or underbudget by the end of the month.

For a GUI sample and applet walkthrough, click this [link](gui_sample/README.md).

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

To run this application (after installing all required packages), type the following command in terminal/bash in the directory inside the Dollars folder:

```
python3 gui.py
```

### References

References to the libraries and packages used in Dollars:

1) ``tkinter``: https://wiki.python.org/moin/TkInter
2) ``matplotlib``: https://matplotlib.org/gallery/index.html
3) ``pandas``: https://pandas.pydata.org/pandas-docs/stable/
4) ``pandastable``: https://github.com/dmnfarrell/pandastable
5) ``scipy``/``numpy``: https://www.scipy.org/
6) ``geopy``: https://geopy.readthedocs.io/en/stable/
7) ``gmplot``: https://github.com/vgm64/gmplot
8) ``statsmodels`` (specifically time series ARIMA): http://www.statsmodels.org/dev/generated/statsmodels.tsa.arima_model.ARIMA.html
9) ``pyramid-arima``: https://github.com/tgsmith61591/pyramid
