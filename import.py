# import book data from csv and insert into database

import os
import csv, tqdm

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    csv_file = "books.csv"
    f = open(csv_file)
    reader = csv.reader(f)
    header = next(reader, None)
    count = 0
    for book in tqdm.tqdm(reader):
        [isbn, title, author, year] = book
        try:
            db.execute("INSERT INTO books(isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn":isbn, "title":title, "author":author, "year":year})
        except exc.SQLAlchemyError as e:
            print(f"SQLAlchemy error {e}")
            break
        count += 1
        
    db.commit()
    print(f"Inserted {count} books in db.")
    f.close()

if __name__ == "__main__":
    main()