import os
from datetime import datetime
import requests

from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt

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

goodreads_key = "RDV7j0TosEXJvMwN4XNVzw"

# index (home page)
@app.route("/")
def index():

    # if logged in 
    if "username" in session:
        return render_template("index.html", username=session["username"])
    
    # not logged in 
    else:
        return render_template("index.html")

# search
@app.route("/search")
def search():

    if "username" in session:
        return render_template("search.html", username=session["username"])
    else:
        flash("Logging in is required for this feature", category="error")
        return redirect(url_for('index'))

# login 
@app.route("/login", methods = ["POST", "GET"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username":username}).fetchone()
        if user is None:
            flash("Username does not exist.", category="error")
            return redirect(url_for('login'))
        if sha256_crypt.verify(password, user.password):
            flash("You were successfully logged in!", category="success")
            session["username"] = username
            return redirect(url_for("search"))
        else:
            flash("Incorrect Password", category="error")
            return redirect(url_for('login'))
            
# logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have successfully logged out!", category="success")
    return redirect(url_for("index"))

@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # create account after user fills form and clicks register button
    if request.method == "POST":
        username = request.form.get("username")
        password = sha256_crypt.hash(request.form.get("password"))
        email = request.form.get("email")
        # TODO: validate form entries
        
        try:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username":username, "password":password})

        except exc.IntegrityError:
            #TODO: add specific error handling
            flash("Username already exists.", category='error')
            return redirect(url_for('register'))
        db.commit()
        flash("Account created, you can login now.", category="success")
        return redirect(url_for('login'))

@app.route("/account")
def account():

    if "username" in session:
        
        reviews = db.execute("SELECT b.title, r.book_isbn, r.stars, r.textreview, r.timestamp FROM users u join reviews r on u.id=r.user_id join books b on r.book_isbn=b.isbn WHERE u.username=:username", {"username":session["username"]}).fetchall()

        return render_template("account.html", username=session["username"], reviews=reviews)
    else:
        flash("Logging in is required for this feature", category="error")
        return redirect(url_for('index'))

@app.route("/booklist")
def booklist():
    
    if "username" in session:
        # get list of books
        books = db.execute("SELECT * FROM books").fetchall()
        return render_template('booklist.html', username=session["username"], books=books)
    
    else:
        flash("Logging in is required for this feature", category="error")
        return redirect(url_for('index'))

@app.route("/results", methods = ["POST", "GET"])
def results():

    form_results = request.form
    isbn, title, author = form_results.get('isbn'), form_results.get('title'), form_results.get('author')
    
    if isbn=="" and title=="" and author=="":
        flash("Please enter atleast one of the three options!", category="error")
        return redirect(url_for('search'))

    books = db.execute("SELECT * FROM books WHERE lower(isbn) LIKE lower(:isbn) AND lower(title) LIKE lower(:title) AND lower(author) LIKE lower(:author)", {"isbn":f"%{isbn}%", "title":f"%{title}%", "author":f"%{author}%"}).fetchall()
    if not books:
        flash("No books matched your search!", category="error")
        return redirect(url_for('search'))
    return render_template('booklist.html', username=session["username"], books=books)

@app.route("/book/<string:isbn>", methods=["POST", "GET"])
def book(isbn):
    if request.method == "POST":
        stars = request.form.get("stars")
        review = request.form.get("review")
        # insert 
        user_id = db.execute("SELECT * FROM users WHERE username = :username", {"username":session["username"]}).fetchone().id
        try:
            db.execute("INSERT INTO reviews (book_isbn, stars, textreview, user_id, timestamp) VALUES (:isbn, :stars, :review, :user_id, now())", {"isbn":isbn, "stars":stars, "review":review, "user_id":user_id})
        except exc.SQLAlchemyError as e:
            print(f"SQLAlchemy error while inserting review:\n\n{e}")
            return

        db.commit()
        print("Inserted review")
        return redirect("#")

    if request.method == "GET":
        book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()

        # get users' textual reviewa
        reviews = db.execute("SELECT r.textreview, r.stars, u.username FROM reviews as r join users as u on r.user_id=u.id WHERE r.book_isbn=:isbn AND r.textreview IS NOT NULL", {"isbn":isbn}).fetchall()

        # get users' star rating
        stars = db.execute("SELECT AVG(stars) as avg_stars, COUNT(stars) as count_stars FROM reviews WHERE book_isbn=:isbn", {"isbn":isbn}).fetchone()
        avg_stars = stars.avg_stars
        count_stars = stars.count_stars
        if avg_stars is not None:
            avg_stars = round(avg_stars, 1)
        else:
            avg_stars = 0
        
        # get goodreads rating
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodreads_key, "isbns": isbn})
        goodreads_rating = [res.json().get('books')[0].get(x) for x in ['average_rating', "work_reviews_count"]]
        print(goodreads_rating) 

        # check if this user has already submitted a review
        review_submitted = db.execute("SELECT count(*) as count FROM reviews as r join users as u on r.user_id=u.id WHERE r.book_isbn=:isbn AND u.username=:username", {"isbn":isbn, "username":session["username"]}).fetchone().count

        return render_template("book.html", username=session["username"], book=book, avg_stars=avg_stars, count_stars=count_stars, reviews=reviews, review_submitted=review_submitted, goodreads_rating=goodreads_rating)

@app.route("/api/<string:isbn>")
def api(isbn):

    # make sure book exists
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
    if book is None:
        return jsonify({"error":"Invalid isbn"}), 404

    stars = db.execute("SELECT AVG(stars) as avg_stars, COUNT(stars) as count_stars FROM reviews WHERE book_isbn=:isbn", {"isbn":isbn}).fetchone()
    avg_stars = stars.avg_stars
    count_stars = stars.count_stars
    if avg_stars is not None:
        avg_stars = round(avg_stars, 1)
    else:
        avg_stars = 0

    return jsonify(
    title= book.title,
    author= book.author,
    year= book.year,
    isbn= book.isbn,
    review_count= count_stars,
    average_score= float(avg_stars)
    )

def main():
    app.run()

if __name__ == "__main__":
    main()
