from flask import Flask, render_template, g, request
from datetime import datetime as dt
import sqlite3
import os

# Flask object
app = Flask(__name__)

database_path = os.getenv("DATABASE_PATH")

# connects the web app to the database
def connect_db():
    sql = sqlite3.connect(database_path)
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# close database connection
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

    cur = db.execute('select log_date.entry_date, sum(food.protein) as protein, sum(food.carbohydrates) as carbs, sum(food.fat) as fat, sum(food.calories) as calories from log_date left join food_date on food_date.log_date_id = log_date.id left join food on food.id = food_date.food_id group by log_date.id order by log_date.entry_date desc')
    results = cur.fetchall()

    date_results = []
    for result in results:
        single_date = {}

        single_date['entry_date'] = result['entry_date']
        single_date['protein'] = result['protein']
        single_date['carbohydrates'] = result['carbs']
        single_date['fat'] = result['fat']
        single_date['calories'] = result['calories']

        d = dt.strptime(str(result['entry_date']), '%Y%m%d')
        single_date['pretty_date'] = dt.strftime(d, '%B %d, %Y')

        date_results.append(single_date)

    return render_template("home.html", results=date_results)


@app.route("/view/<date>", methods=["GET", "POST"])
def view(date):
    db = get_db()

    cur = db.execute('select id, entry_date from log_date where entry_date = ?', [date])
    date_result = cur.fetchone()

    if request.method == "POST":
        db.execute('insert into food_date (food_id, log_date_id) values (?, ?)', [request.form['food-select'], date_result['id']])
        db.commit()


    d = dt.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = dt.strftime(d, '%B %d, %Y')

    # food items to select as an option
    food_cur = db.execute('select id, name from food')
    food_results = food_cur.fetchall()

    log_cur = db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id where log_date.entry_date = ?', [date])
    log_results = log_cur.fetchall()

    totals = {'protein': 0, 'carbohydrates': 0, 'fat': 0, 'calories': 0}

    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']

    return render_template("day.html", entry_date=date_result['entry_date'], pretty_date=pretty_date, food_results=food_results, log_results=log_results, totals=totals)
    

@app.route("/food", methods=["GET", "POST"])
def food():
    db = get_db()  # get the database

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