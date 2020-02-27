import os
import requests
from flask import Flask, session, render_template, url_for, request, redirect, jsonify
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
            return redirect("/search/"+bookname)
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
        result = db.execute("SELECT email, password, username FROM master WHERE email = :email", {"email": email}).fetchone()
        print(result)
        if email == result[0] and password == result[1]:
            print("good job")
            session["email"] = result[0]
            session["username"] = result[2]
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

# search result 
@app.route("/search/<book>")
def search_result(book):
    books_query = "SELECT * FROM books WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author"
    results = db.execute(books_query, {"isbn" : book+'%', "title": book+'%', "author": book+'%'}).fetchall()
    
    return render_template("result.html", results= results, book= book)



# book 
@app.route("/<book>", methods=["POST", "GET"])
def book(book):
    # book section 
    books_query = "SELECT * FROM books WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author"
    result = db.execute(books_query, {"isbn" : '%'+book+'%', "title": '%'+book+'%', "author": '%'+book+'%'}).fetchone()
    API_res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "d0YLsqe9THhgDCZEvYJVA", "isbns": result[1]})
    jsonAPI = API_res.json()
    # review section 
    reviews_query = "SELECT * FROM reviews WHERE book_id = ':book_id'"
    reviews = db.execute(reviews_query, {"book_id": result[0]}).fetchall()
    # comment 
    comment_check = db.execute("SELECT * FROM reviews WHERE user_name = :username AND book_id = :book_id",{"username": session.get("username"), "book_id":  str(result[0])}).fetchone()
    print(comment_check)
    print(session.get("username"))
    if request.method == "POST" and comment_check == None:
        comment_query = "INSERT INTO reviews (book_id, user_name, review, rate) VALUES (:book_id, :username, :review, :rate)" 
        comment = request.form.get('comment')
        book_id = result[0]
        rate = request.form.get('entered_rate')
        print(session.get("username"))
        db.execute(comment_query, {"book_id": book_id, "username": session.get("username"), "review": comment, "rate": rate })
        db.commit()
        return redirect("/"+ result[1])
    elif  request.method == "POST" and comment_check[2] == session.get("username"):
            return render_template("book.html", result= result, jsonAPI= jsonAPI, reviews= reviews, message= "you can review only once")
    else:
        return render_template("book.html", result= result, jsonAPI= jsonAPI, reviews= reviews)


# logout 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/api/<isbn>")
def api(isbn):
    try:
        query = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id",{"book_id": str(query[0]) }).fetchall()
        rate_sum = 0
        review_count = 0
        for review in reviews:
            review_count = review_count + 1
        for review in reviews:
            rate_sum = review[4] + rate_sum
        if isbn == query[1]:
            average_score = rate_sum / (review_count)
            return jsonify({"title":query[2], "author":query[3], "year":query[4], "isbn":isbn, "review_count": review_count , "average_score":average_score })
        
    except:
        return jsonify({"error": "Invalid isbn"}), 422
    # get_book_id = db.execute("SELECT * FROM books")
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id",{"book_id": str(query[0]) }).fetchall()
    rate_sum = 0
    review_count = 0
    for review in reviews:
        review_count = review_count + 1
    for review in reviews:
        rate_sum = review[4] + rate_sum
    if isbn == query[1]:
        average_score = rate_sum / (review_count)
        return jsonify({"title":query[2], "author":query[3], "year":query[4], "isbn":isbn, "review_count": review_count , "average_score":average_score })
    
    


# INSERT INTO reviews (book_id, user_name, review, rate) VALUES ('1', 'khaled', 'wow amazing', '3');

# CREATE TABLE reviews(
#     id SERIAL PRIMARY KEY,
#     book_id VARCHAR NOT NULL,
#     user_name VARCHAR NOT NULL,
#     review VARCHAR NOT NULL,
#     rate INTEGER NOT NULL
# );





