# Project 1

Web Programming with Python and JavaScript

## Tables

1. User - id, username, password, email id
2. Books - isbn, title, author, year, review_id
3. Reviews - id, book_isbn, stars, textreview, user_id, timestamp


## Features

1. User Account 
    1. User creates account with username, password and email id
    2. User logs in with username and password --> goes to search page
    3. User logs out

2. Search books
    1. Enter ISBN, title or author of book. Display matching results/message if no results. Partial entries in query field should be matched too to give possible results.
    2. Clicking on the book --> book page with book details including reviews (left on my website).

3. Reviews
    1. On book page, user can add a rating (1-5 scale) and a text review. 
    2. User can submit a review only once for a book.
    3. If available, book page also diplays Goodreads Review of the book.

4. API access
    1. `/api/<isbn>` should return JSON response with book details. (format given in instructions)
    2. 404 error if isbn does not exist

## Files 

1. createtables.py
2. import.py - take books from `books.csv` and import them into the database

