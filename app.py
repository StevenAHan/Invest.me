# %%
from re import I
from flask import Flask, render_template, request, url_for, flash, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
import pandas as pd
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

# %%
pymysql.install_as_MySQLdb()

# %%
df = pd.DataFrame({1:[1,2,3]})

# %%
app = Flask(__name__)

# %%
def get_chart(symbol):
    end = datetime.date.today() - datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=650)
    data = yf.download(symbol, start, end)['Adj Close'].to_frame()
    data['SMA50'] = data['Adj Close'].rolling(50).mean()
    data['SMA200'] = data['Adj Close'].rolling(200).mean()
    data.dropna(inplace=True)
    data.reset_index(inplace=True)
    dates = pd.date_range(start=start, end=end, freq='MS')
    fig = px.line(data, x="Date", y=['Adj Close', 'SMA50', 'SMA200'],
                  title=symbol + ' Stock Price Versus 50 & 200 Moving Averages')
    fig.update_layout(yaxis_title='Price',
                      xaxis={'tickmode': 'array', 'tickvals': dates,
                             'ticktext': [d.strftime('%b %Y') for d in dates]},
                      legend_title='Indicator')
    return fig

# %%
def esg_pie(companies):
    df_pie = pd.DataFrame(companies)
    df = getDB()
    df_pie['totalEsg'] = df['totalEsg']
    fig = px.pie(df_pie, values='totalEsg', names='Symbol', title='Environmental, social, and governance (ESG) Score Percentages of Selected Companies',
                 hole=.2)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

# %%
def financials_chart(companies):
    df_chart = pd.DataFrame(companies)
    df = getDB()
    df_chart['Company'] = df['Symbol']
    df_chart['Profit Margin'] = df['ProfitMargin']
    df_chart['Operating Margin'] = df['OperatingMarginTTM']
    df_chart['Return on Assets'] = df['ReturnOnAssetsTTM']
    df_chart['Return on Equity'] = df['ReturnOnEquityTTM']
    df_chart['Revenue'] = df['RevenueTTM']
    fig = px.bar(df_chart, x='Company', y='Profit Margin', barmode='group')
    dropdown_options = [
        {'label': 'Profit Margin', 'value': 'Profit Margin'},
        {'label': 'Operating Margin', 'value': 'Operating Margin'},
        {'label': 'Return on Assets', 'value': 'Return on Assets'},
        {'label': 'Return on Equity', 'value': 'Return on Equity'},
        {'label': 'Revenue', 'value': 'Revenue'}
    ]
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list([
                    dict(
                        label=option['label'],
                        method='update',
                        args=[{'y': [df_chart[option['value']]]}],
                        args2=[{'yaxis.title.text': option['label']}]
                    )
                    for option in dropdown_options
                ]),
                active=0,
                showactive=True,
                direction='down',
                xanchor='left',
                yanchor='top',
                y=1.15,
                x=0.02,
                pad={'r':10,'t':10}
            )
        ],
        yaxis_title='Operating Metric'
    )
    return fig

# %%
def getDB():
    group_username = "quartic_computing"
    group_password = "lEm25xfjJe4="
    db_name = "quartic_computing"
    conn_string = 'mysql://{user}:{password}@{host}:{port}/{db}?charset={encoding}'.format(
        user=group_username,
        password=group_password,
        host='jsedocc7.scrc.nyu.edu',
        port=3306,
        encoding='utf8',
        db=db_name
    )
    engine = create_engine(conn_string)
    query = 'SELECT * FROM Quantic_data'
    return pd.read_sql_query(sql=text(query), con=engine.connect()).tail(-1)

# %%
def getFeedback():
    group_username = "quartic_computing"
    group_password = "lEm25xfjJe4="
    db_name = "quartic_computing"
    conn_string = 'mysql://{user}:{password}@{host}:{port}/{db}?charset={encoding}'.format(
        user=group_username,
        password=group_password,
        host='jsedocc7.scrc.nyu.edu',
        port=3306,
        encoding='utf8',
        db=db_name
    )
    engine = create_engine(conn_string)
    query = 'SELECT * FROM Survey_data'
    return pd.read_sql_query(sql=text(query), con=engine.connect())

# %%
def uploadFeedback(acc, spread, questions):
    group_username = "quartic_computing"
    group_password = "lEm25xfjJe4="
    db_name = "quartic_computing"
    conn_string = 'mysql://{user}:{password}@{host}:{port}/{db}?charset={encoding}'.format(
        user=group_username,
        password=group_password,
        host='jsedocc7.scrc.nyu.edu',
        port=3306,
        encoding='utf8',
        db=db_name
    )
    engine = create_engine(conn_string)
    df = pd.read_sql_query(sql=text("SELECT * FROM Survey_data"), con=engine.connect()).tail(-1)
    new_row = {'Accuracy': acc, 'Spreadability': spread, 'Questions': questions}
    df = df.append(new_row, ignore_index=True)
    # This is for speeding up the insertion into the database schema
    df.to_sql(name= "Survey_data",
          con=engine,
          if_exists='replace',
          index=False,
          chunksize=1000,
          method='multi'
    )

# %%
def convertStringToh3(strList):
    for i in range(len(strList)):
        strList[i] = "<h3>" + strList[i] + "</h3>"
    return strList.join(" ")

# %%
def convertCompanyDFToButtons(df):
    company_names = df['Name'].tolist()
    company_symbols = df["Symbol"].tolist()
    df["ProportionalUndervalued"] = df["ProportionalUndervalued"] * 100
    df["ProportionalUndervalued"] = round(df["ProportionalUndervalued"], 1)
    company_price = df["ProportionalUndervalued"].tolist()
    companiesHTML = ""
    for i in range(len(company_names)):
        companiesHTML += f"<a class='companyList' href='/company/{company_symbols[i]}'> {company_names[i]} ({company_price[i]}%)</a>"
    return companiesHTML

# %%
def getSentiment(input):
    endpoint = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/3d4468af-8ad0-4453-9535-72f90c9eb5c4/v1/analyze"

    # You can register and get your own credentials
    # The ones below have a quota of 1000 calls per day
    # and can run out quickly if multiple people use these
    username = "apikey"
    password = "-OwF1ab-S1ekafX-ps_dSnaFE_Q0eYBf9wtTdcVV2x0B"
    parameters = {
        'features': 'emotion,sentiment',
        'version': '2022-04-07',
        'text': input,
        'language': 'en',
        # url = url_to_analyze, this is an alternative to sending the text
    }
    resp = requests.get(endpoint, params=parameters, auth=(username, password))
    return resp.json()['sentiment']['document']['score']

# %% [markdown]
# Default route

# %%
@app.route("/")
def home():
    return render_template("home.html")

# %%
@app.route("/data")
def data():
    df = getDB()
    return render_template("data.html", tables=[df.to_html(classes='data')], titles=df.columns.values)

# %%
@app.route("/getfeedback")
def fbdata():
    df = getFeedback()
    return render_template("feedbackdata.html", tables=[df.to_html(classes='fb')], titles=df.columns.values)

# %%
def filtered_df(risk_input, sent_input, env_input, pol_input, df):
    print("into the function")
    print("mean:", df['Beta'].mean())
    print("standev:", df['Beta'].std())
    risk_input_cutoff = df['Beta'].mean() - df['Beta'].std() * risk_input  # below this value
    sent_input_cutoff = df['Sentiment Score'].mean() + df['Sentiment Score'].std() * sent_input  # above this value
    env_input_cutoff = df['percentile'].mean() + df['percentile'].std() * env_input  # above this value
    pol_input_cutoff = df['politican_count'].mean() + df['politican_count'].std() * pol_input  # above this value
    print("got the means and stds")
    rslt_df = df[df['Beta'] < risk_input_cutoff]
    print("first cutoff")
    rslt_df = rslt_df[rslt_df['Sentiment Score'] > sent_input_cutoff]
    rslt_df = rslt_df[rslt_df['percentile'] > env_input_cutoff]
    rslt_df = rslt_df[rslt_df['politican_count'] > pol_input_cutoff]
    print("return")
    return rslt_df

import speech_recognition as sr


#brew install flac
# brew install portaudio
# pip install pyaudio

def record():
    #return "hello"
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source, phrase_time_limit = 5)
    #try:
    s = r.recognize_google(audio, language="en-US")
    print("Text: " + s)
    # except Exception as e:
    #     print("Exception: " + str(e))
    return s

@app.route("/prompt5", methods=["GET", "POST"])
def prompt5():
    if request.method == 'POST':
        # write your Python code here
        result_text = record()
    return render_template('prompt.html', result3=result_text)

# %%
@app.route("/prompt", methods=["GET", "POST"])
def prompt():
    # if the form is submitted
    if (request.method == "POST"):
        risk_input = request.form['risk-input']  # strings
        print("risk:", risk_input)
        sent_input = request.form["sent-input"]
        print("sent:", sent_input)
        env_input = request.form["env-input"]
        print("env:", env_input)
        pol_input = request.form["pol-input"]
        print("pol:", pol_input)
        risk_ss = getSentiment(risk_input)
        sent_ss = getSentiment(sent_input)
        env_ss = getSentiment(env_input)
        pol_ss = getSentiment(pol_input)  # add this, so you get # from -1 to 1
        print("answers:", risk_ss, sent_ss, env_ss, pol_ss)
        df = getDB()
        df["percentile"] = pd.to_numeric(df["percentile"], errors="coerce")
        df["Beta"] = pd.to_numeric(df["Beta"], errors="coerce")
        mean_value = df["percentile"].mean()
        mean_value2 = df["Beta"].mean()
        df["percentile"].fillna(mean_value)
        df["Beta"].fillna(mean_value2)
        # filter the db
        # df will be filtered db
        df = filtered_df(risk_ss, sent_ss, env_ss, pol_ss, df)
        df = df.head(5)
        print(df)
        companies = convertCompanyDFToButtons(df)
        listHTML = ""
        listHTML += "<li>You like to take risks</li>" if risk_ss > 0 else "<li>You are adverse to risk</li>"
        listHTML += "<li>You care about public sentiment</li>" if sent_ss > 0 else "<li>You don't care too much about public sentiment</li>"
        listHTML += "<li>You care a lot about the environment</li>" if env_ss > 0 else "<li>You aren't focused on environmentality</li>"
        listHTML += "<li>You care about insider trading</li>" if pol_ss > 0 else "<li>You don't care that much about insider trading</li>"
        compList = df['Symbol'].head(5)
        fig = esg_pie(compList)
        graphJSON1 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        fig2 = financials_chart(compList)
        graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template("result.html", companies=companies, listHTML=listHTML, graphJSON1=graphJSON1, graphJSON2=graphJSON2)
    return render_template("prompt.html")

# %% [markdown]
# @app.route("/result")<br>
# def result():<br>
#     return render_template("result.html")

# %%
@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

# %%
@app.route("/feedback-submitted", methods=["GET", "POST"])
def fbsb():
    if (request.method == "POST"):
        uploadFeedback(request.form["Accuracy"], request.form["Spreadability"], request.form["Questions"])
    return render_template("feedbacksub.html")

# %%
@app.route("/company/<string:company_symbol>")
def company(company_symbol):
    df = getDB()
    company = df.loc[df['Symbol'] == company_symbol.upper()].iloc[0].to_dict()
    fig = get_chart(company_symbol)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    company["PredictedPrice"] = round(company["PredictedPrice"], 2)
    return render_template("companyInfo.html", company=company, graphJSON=graphJSON)

# %%
@app.route("/companies")
def companies():
    df = getDB()
    companiesHTML = convertCompanyDFToButtons(df)
    return render_template("companies.html", companies=companiesHTML)

# %%
if __name__ == "__main__":
    app.run(debug=False)