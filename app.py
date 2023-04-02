from re import I
from flask import Flask, render_template, request, url_for, flash, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class files(db.Model):
    id = db.Column("id", db.Integer, primary_key = True)
    file_name = db.Column(db.String(100))
    file_blob = db.Column(db.LargeBinary)
    def __init__(self, file_name, file_blob):
        self.file_name = file_name
        self.file_blob = file_blob

with app.app_context():
    db.create_all()

# To insert a file into the database
def insert_into_database(file):
    db.session.add(file)
    db.session.commit()

# To get a file from the database
def get_from_database(file_name):
    file = files.query.filter_by(file_name = file_name).first()
    return file.file_blob

# To remove a file from the database
def remove_from_database(file_name):
    file = files.query.filter_by(file_name = file_name).first()
    db.session.delete(file)
    db.session.commit()

# Default route
@app.route("/")
def index():
    the_files = files.query.all()
    return render_template("index.html", files=the_files)

    
if __name__ == "__main__":
    app.run(debug=True)