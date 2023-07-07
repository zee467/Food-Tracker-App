from flask import Flask, render_template, g, request
from datetime import datetime as dt
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


@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()

    if request.method == "POST":
        database_date = dt.strptime(request.form["date"], "%Y-%m-%d")
        final_db_date = dt.strftime(database_date, "%Y%m%d")
        
        db.execute('insert into log_date (entry_date) values (?)', [final_db_date])
        db.commit()
    return render_template("home.html")

@app.route("/view")
def view():
    return render_template("day.html")
    

@app.route("/food", methods=["GET", "POST"])
def food():
    db = get_db()

    if request.method == "POST":
        food = request.form['food-name']
        fat = int(request.form['fat'])
        carbohydrates = int(request.form['carbohydrates'])
        protein = int(request.form['protein'])

        calories = carbohydrates * 4 + protein * 4 + fat * 9
        
        db.execute('insert into food (name, protein, carbohydrates, fat, calories) values (?, ?, ?, ?, ?)', [food, protein, carbohydrates, fat, calories])
        db.commit()

    cur = db.execute("select name, protein, carbohydrates, fat, calories from food")
    results = cur.fetchall()
    return render_template("add_food.html", results=results)