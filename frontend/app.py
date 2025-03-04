import os
import sys
from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#this gets the models information
from models.db_models import db  
from models.populate_db import populate_db 


# this initializes the flask app that runs the server
app = Flask(__name__)
app.secret_key = "hello"

# this is for configuring sql alchemy
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///scheduling.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# this initializes the database
db.init_app(app)
 

#links to homepage
@app.route("/")
def home():
    return render_template("home_page.html")

# example sample create for how routing works in flask
@app.route("/login")
def user_login():
    return redirect(url_for("home"))

if __name__ == "__main__":
    #runs if the database is empty
    with app.app_context():
        db.create_all()
        print("Database initialized!")
    app.run(debug=True)