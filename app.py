from flask import Flask, render_template, g, request
import sqlite3
import os

app = Flask(__name__)

database_path = os.getenv("DATABASE_PATH")

def connect_db():
    sql = sqlite3.connect(database_path)
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route("/")
def index():
    return render_template("home.html")

@app.route("/view")
def view():
    return render_template("day.html")
    

@app.route("/food", methods=["GET", "POST"])
def food():
    if request.method == "POST":
        return f"<h1>Food: {request.form['food-name']} Fat: {request.form['fat']} Carbohydrates: {request.form['carbohydrates']}\
            Protein: {request.form['protein']}</>"
    return render_template("add_food.html")