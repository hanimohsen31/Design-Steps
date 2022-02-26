import imp
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from sqlalchemy import PrimaryKeyConstraint
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session, url_for
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///design.db")
# db = SQL("https://firebasestorage.googleapis.com/v0/b/design-steps.appspot.com/o/design.db?alt=media&token=15cce15a-58f6-4add-86cf-956edfb34a6e")
# postgres://ckhcrgnmjqgvta:465294900aa8ff756289f1b8cd427c188d707881ce88f9b00a4ad990b2d1029d@ec2-3-227-195-74.compute-1.amazonaws.com:5432/d3u9elt515ribt



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# ----------------------------------------------- DataBase ----------------------------------------------- #
'''
CREATE TABLE pics (id INTEGER,
                    cat TEXT NOT NULL,
                    image_file TEXT NOT NULL,
                    PRIMARY KEY(id)
                    );

CREATE TABLE pallets (id INTEGER,
                    image_file TEXT NOT NULL,
                    col1 TEXT NOT NULL,
                    col2 TEXT NOT NULL,
                    col3 TEXT NOT NULL,
                    col4 TEXT NOT NULL,
                    col5 TEXT NOT NULL,
                    col6 TEXT NOT NULL,
                    PRIMARY KEY(id)
                    );

CREATE TABLE users (
                id INTEGER,
                username TEXT NOT NULL,
                email TEXT ,
                hash TEXT NOT NULL,
                UNIQUE (username),
                UNIQUE (email),
                PRIMARY KEY(id)
            );

CREATE TABLE list1 (
                pic_id INTEGER,
				user_id INTEGER,
                FOREIGN KEY(pic_id) REFERENCES pics(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

CREATE TABLE list2 (
                pallet_id INTEGER,
				user_id INTEGER,
                FOREIGN KEY(pallet_id) REFERENCES pallets(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

'''
# ----------------------------------------------- globalQuery ----------------------------------------------- #
# globalQuery = db.execute("SELECT * FROM pics")
# ----------------------------------------------- home ----------------------------------------------- #
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        input = request.form.get("design")
        query = db.execute("Select * FROM pics Where cat like ?", input)
        return render_template("design.html", data=query )

    if request.method == "GET":
        globalQuery = db.execute("SELECT * FROM pics")
        return render_template("home.html", data=globalQuery )
# ----------------------------------------------- design ----------------------------------------------- #
@app.route("/design", methods=["GET", "POST"])
@login_required
def design():
    if request.method == "POST":
        currntUser = session["user_id"]
        print('currntUser: ',currntUser)
        input = request.form.get("design")
        print('input: ',input)
        query = db.execute("Select * FROM list1 Where pic_id = ?", input)
        print('design query: ',query)
        if not query:
            db.execute("INSERT INTO list1 (pic_id, user_id) VALUES(?, ?)", input, currntUser)
            # return redirect('/mylist')
            return ('', 204)
        else:
            # return redirect('/mylist')
            return ('', 204)
        

    if request.method == "GET":
        globalQuery = db.execute("SELECT * FROM pics")
        return render_template("design.html", data=globalQuery )
# ----------------------------------------------- pallet ----------------------------------------------- #
@app.route("/pallet", methods=["GET", "POST"])
@login_required
def pallet():
    if request.method == "POST":
        currntUser = session["user_id"]
        print('currntUser: ',currntUser)
        input = request.form.get("pallet")
        print('input: ',input)
        query = db.execute("Select * FROM list2 Where pallet_id = ?", input)
        print('design query: ',query)
        if not query:
            db.execute("INSERT INTO list2 (pallet_id, user_id) VALUES(?, ?)", input, currntUser)
            # return redirect('/mypallets')
            return ('', 204)

        else:
            # return redirect('/mypallets')
            return ('', 204)


    if request.method == "GET":
        query = db.execute("Select * FROM pallets")
        return render_template("pallet.html", data=query )
# ----------------------------------------------- mylist ----------------------------------------------- #
@app.route("/mylist", methods=["GET", "POST"])
@login_required
def mylist():
    if request.method == "POST":
        currntUser = session["user_id"]
        input = request.form.get("list1")
        query = db.execute("Delete from list1 where pic_id = ? and user_id = ?",input,currntUser)
        print('deleted')
        return redirect('/mylist')
        # return ('', 204)

    if request.method == "GET":
        currntUser = session["user_id"]
        print(currntUser)
        list=[]
        query = db.execute("Select * from list1 where user_id = ? ",currntUser)
        for i in query :
            list.append(i['pic_id'])
        print(list)
        data = db.execute("Select * from pics where id in (?) ",list)
        print(data)
        context = {
            'data':data,
        }
        return render_template("mylist.html", data=context )
# ----------------------------------------------- mypallets ----------------------------------------------- #
@app.route("/mypallets", methods=["GET", "POST"])
@login_required
def mypallets():
    if request.method == "POST":
        currntUser = session["user_id"]
        input = request.form.get("list2")
        query = db.execute("Delete from list2 where pallet_id = ? and user_id = ?",input,currntUser)
        return redirect('/mypallets')
        # return ('', 204)

    if request.method == "GET":
        currntUser = session["user_id"]
        print(currntUser)
        list=[]
        query = db.execute("Select * from list2 where user_id = ? ",currntUser)
        for i in query :
            list.append(i['pallet_id'])
        data = db.execute("Select * from pallets where id in (?) ",list)
        context = {
            'data':data,
        }
        return render_template("mypallets.html", data=context )
# ----------------------------------------------- report ----------------------------------------------- #
# @app.route("/report", methods=["GET", "POST"])
# @login_required
# def report():
#     if request.method == "POST":
#         pass
#     if request.method == "GET":
#         # -----------------------------------------------
#         currntUser = session["user_id"]
#         list=[]
#         query = db.execute("Select * from list1 where user_id = ? ",currntUser)
#         for i in query :
#             list.append(i['pic_id'])
#         data1 = db.execute("Select * from pics where id in (?) ",list)
#         # context = {'data':data,}
#         # -----------------------------------------------
#         # list2=[]
#         query = db.execute("Select * from list2 where user_id = ? ",currntUser)
#         for i in query :
#             list.append(i['pallet_id'])
#         data2 = db.execute("Select * from pallets where id in (?) ",list)
#         data3 = data1 + data2
#         context = {'data':data3}
#         # -----------------------------------------------
#         return render_template("mypallets.html", data=context )
# ----------------------------------------------- steps ----------------------------------------------- #
@app.route("/steps", methods=["GET", "POST"])
@login_required
def steps():
    if request.method == "POST":
        pass

    if request.method == "GET":
        return render_template("steps.html")
# ----------------------------------------------- about ----------------------------------------------- #
@app.route("/about", methods=["GET", "POST"])
@login_required
def about():
    if request.method == "POST":
        pass

    if request.method == "GET":
        return render_template("about.html")
# ----------------------------------------------- login ----------------------------------------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("prove"):
            return apology("must prove that you are Hani Mohsen", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # print('rows: ', rows)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("log in error", 403)

        if request.form.get("prove") != 'hanimohsenprove':
            return apology("Who the fuck are you !!", 403)

        # Remember which user has logged in
        try:
            session["user_id"] = rows[0]["id"]
        except:
            print('no session was created motherfucker')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# ----------------------------------------------- register ----------------------------------------------- #
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        """Register user"""
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirm =request.form.get("confirmation")
        email =request.form.get("email")

        if password != password_confirm :
            return apology("wrong confirmation", 400)

        password = generate_password_hash(request.form.get("password"))
        # print(password)
        session.clear()


        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password was submitted
        elif not request.form.get("email"):
            return apology("must provide email", 400)

        elif not request.form.get("prove"):
            return apology("must prove that you are Hani Mohsen", 403)


        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        rows_email = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        if len(rows) >= 1 :
            print('error line 151 checkpass')
            return apology("invalid username and/or password", 400)

        if len(rows_email) >= 1 :
            print('error line 151 checkpass')
            return apology("invalid email and/or password", 400)

        if request.form.get("prove") != 'hanimohsenprove':
            return apology("Who the fuck are you !!", 403)

        db.execute("INSERT INTO users (username,email, hash) VALUES(?, ?, ?)", username,email, password)
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Remember which user has logged in
        try:
            session["user_id"] = rows[0]["id"]
        except:
            print('no session was created motherfucker')

        return redirect ('/')

    if request.method == "GET":
        return render_template("register.html")

# ----------------------------------------------- logout ----------------------------------------------- #
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# ---------------------------------------------------------------------------------------------- #