import os

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    
    try:
        # create user table : id, username, password, emailid 
        db.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, username VARCHAR UNIQUE NOT NULL, password VARCHAR NOT NULL, emailid VARCHAR)")

        # books table : isbn, title, author, year
        db.execute("CREATE TABLE books(isbn VARCHAR PRIMARY KEY, title VARCHAR NOT NULL, author VARCHAR not null, year INT NOT NULL)")

        # reviews table : id, book_isbn, stars, textreview, user_id, timestamp
        db.execute("CREATE TABLE reviews(id SERIAL PRIMARY KEY, book_isbn VARCHAR NOT NULL, stars INT NOT NULL CHECK (stars >= 1 AND stars <= 5), textreview VARCHAR, user_id INT NOT NULL, timestamp TIMESTAMP NOT NULL, UNIQUE (book_isbn, user_id))")

        # foregin key constrains
        db.execute("ALTER TABLE reviews ADD CONSTRAINT fk_book_isbn FOREIGN KEY (book_isbn) REFERENCES books (isbn)")

        db.execute("ALTER TABLE reviews ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users (id)")
    
    except exc.SQLAlchemyError as e:
        print(f"SQLAlchemy error while creating tables:\n\n{e}")
        return

    # commit changes
    db.commit()
    print("Created tables successfully.")
    
if __name__ == "__main__":
    main()