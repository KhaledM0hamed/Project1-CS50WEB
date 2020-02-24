import os

from flask import Flask, session, render_template, url_for, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# Good Read API 
# key: d0YLsqe9THhgDCZEvYJVA
# secret: HcHgJlAfeNZtC2Fqdb2UxyZKAM87RhaiGwKZpKPyDbs

# searching page 
@app.route("/", methods=["GET", "POST"])
def index():
    print(session.get("email"))
    if request.method == "POST":
        if session.get("email") is not None:
            bookname = request.form.get("bookname")
            return redirect("/"+bookname)
        else:
            return render_template("index.html", message=" please login first")
    else:
        return render_template("index.html")

# register page 
@app.route("/register")
def register():
    return render_template("register.html")

# login page 
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        result = db.execute("SELECT email, password FROM master WHERE email = :email", {"email": email}).fetchone()
        print(result)
        if email == result[0] and password == result[1]:
            print("good job")
            session["email"] = result[0]
            return redirect("/")
        else:
            print("something went wrong")
            return render_template("login.html", message="your email or password is wrong!")
    else:
        return render_template("login.html")

# hello page 
@app.route("/hello", methods=["POST"])
def hello():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    print(username)
    print(email)
    print(password)
    try:
        db.execute("INSERT INTO master (username, email, password) VALUES (:username, :email, :password)", {"username": username, "email": email, "password": password})
        db.commit()
        done = "true"
    except:
        done = "false" 

    return render_template("hello.html", done=done)

# book 
@app.route("/<book>")
def book(book):
    result = db.execute("SELECT * FROM books WHERE isbn = :isbn OR title = :title", {"isbn" : book, "title": book}).fetchone()
    return render_template("hello.html", message= result)


# logout 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")