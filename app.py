from re import I
from flask import Flask, render_template, request, url_for, flash, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import yfinance as yf
import numpy as np
import plotly.express as px
import datetime
import plotly
from dateutil.relativedelta import relativedelta
import json
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)

def get_chart(symbol):
  end = datetime.date.today() - datetime.timedelta(days=1)
  start = end - datetime.timedelta(days=650)
  data = yf.download(symbol, start, end)['Adj Close'].to_frame()

  data['SMA50'] = data['Adj Close'].rolling(50).mean()
  data['SMA200'] = data['Adj Close'].rolling(200).mean()
  data.dropna(inplace=True)
  data.reset_index(inplace=True)

  dates = pd.date_range(start=start, end=end, freq='MS')
  fig = px.line(data,x="Date", y=['Adj Close','SMA50', 'SMA200'], title=symbol+' Stock Price Versus 50 & 200 Moving Averages')
  fig.update_layout(yaxis_title='Price',
                    xaxis={'tickmode': 'array', 'tickvals': dates, 
                    'ticktext': [d.strftime('%b %Y') for d in dates]},
                    legend_title = 'Values')
  return fig

def esg_pie(companies):
  df_pie = pd.DataFrame(companies)
  df_pie['totalEsg'] = df['totalEsg']


  fig = px.pie(df_pie, values = 'totalEsg', names = 'Symbol', title='ESG Score Percentages of Selected Companies',
               hole = .2)
  fig.update_traces(textposition='inside', textinfo='percent+label')
  return fig

def getDB():
    group_username = "quartic_computing"
    group_password = "lEm25xfjJe4="
    db_name = "quartic_computing"

    conn_string = 'mysql://{user}:{password}@{host}:{port}/{db}?charset={encoding}'.format(
        user=group_username, 
        password=group_password, 
        host = 'jsedocc7.scrc.nyu.edu', 
        port = 3306, 
        encoding = 'utf8',
        db = db_name
    )
    engine = create_engine(conn_string)
    query = 'SELECT * FROM Quantic_data'

    return pd.read_sql_query(sql=text(query), con=engine.connect())

def convertStringToh3(strList):
    for i in range(len(strList)):
        strList[i] = "<h3>" + strList[i] + "</h3>"
    return strList.join(" ")

def convertCompanyDFToButtons(df):
    company_names = df['Name'].tolist()
    company_symbols = df["Symbol"].tolist()
    companiesHTML = ""
    for i in range(len(company_names)):
        companiesHTML += f"<a class='companyList' href='/company/{company_symbols[i]}'> {company_names[i]} </a> <br>"
    return companiesHTML

#TODO
def getSentiment(input):
    return .7


# Default route
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/data")
def data():
    df = getDB()
    return render_template("data.html", tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route("/prompt", methods=["GET", "POST"])
def prompt():
    # if the form is submitted
    if (request.method == "POST"):
        risk_input = request.form['risk-input']
        sent_input = request.form["sent-input"]
        env_input = request.form["env-input"]
        pol_input = request.form["pol-input"]
        risk_ss = getSentiment(risk_input)
        sent_ss = getSentiment(sent_input)
        env_ss = getSentiment(env_input)
        pol_ss = getSentiment(pol_input)
        df = getDB()
        df = df.head(5)
        companies = convertCompanyDFToButtons(df)
        listHTML = ""
        listHTML += "<p>You like to take risks</p>" if risk_ss > .5 else "<p>You are adverse to risk</p>"
        listHTML += "<p>You care about public sentiment</p>" if sent_ss > .5 else "<p>You don't care too much about public sentiment</p>"
        listHTML += "<p>You care a lot about the environment</p>" if env_ss > .5 else "<p>You aren't focused on environmentality</p>"
        listHTML += "<p>You care about insider trading</p>" if pol_ss > .5 else "<p>You don't care that much about insider trading</p>"

        return render_template("result.html", companies=companies, listHTML=listHTML)
    
    return render_template("prompt.html")
    
# @app.route("/result")
# def result():
#     return render_template("result.html")

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

@app.route("/feedback-submitted", methods=["GET", "POST"])
def fbsb():
    if(request.method == "POST"):
        print("S")
    return render_template("feedbacksub.html")

@app.route("/company/<string:company_symbol>")
def company(company_symbol):
    df = getDB()
    company = df.loc[df['Symbol'] == company_symbol.upper()].iloc[0].to_dict()
    fig = get_chart(company_symbol)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("companyInfo.html", company=company, graphJSON=graphJSON)

@app.route("/companies")
def companies():
    df = getDB()
    companiesHTML = convertCompanyDFToButtons(df)
    return render_template("companies.html", companies=companiesHTML)

if __name__ == "__main__":
    app.run(debug=True)
