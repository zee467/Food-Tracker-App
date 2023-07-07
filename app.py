from flask import Flask, render_template, g, request
from datetime import datetime as dt
import sqlite3
import os

# Flask object
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

    cur = db.execute('select entry_date from log_date order by entry_date desc')
    results = cur.fetchall()

    pretty_results = []
    for result in results:
        single_date = {}

        d = dt.strptime(str(result['entry_date']), '%Y%m%d')
        single_date['entry_date'] = dt.strftime(d, '%B %d, %Y')

        pretty_results.append(single_date)

    return render_template("home.html", results=pretty_results)


@app.route("/view/<date>")
def view(date):
    db = get_db()
    cur = db.execute('select entry_date from log_date where entry_date = ?', [date])
    result = cur.fetchone()

    d = dt.strptime(str(result['entry_date']), '%Y%m%d')
    pretty_date = dt.strftime(d, '%B %d, %Y')

    return render_template("day.html", pretty_date=pretty_date)
    

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