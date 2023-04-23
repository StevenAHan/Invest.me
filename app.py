from re import I
from flask import Flask, render_template, request, url_for, flash, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text

app = Flask(__name__)

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
        company = "hi"
        return render_template("result.html", company=company)
    
    return render_template("prompt.html")
    
@app.route("/result")
def result():
    return render_template("result.html")

if __name__ == "__main__":
    app.run(debug=True)
