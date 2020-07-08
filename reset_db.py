import os

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    choice = input("Are you sure you want to delete tables 'users', 'books' and 'reviews'?\nEnter 'Y' to delete or 'N' to exit. ")
    if choice=='Y':
        try:
            db.execute("DROP TABLE users, books, reviews cascade")
        except exc.SQLAlchemyError as e:
            print(f"SQLAlchemy error:\n{e}")
            return

        db.commit()
    elif choice=='N':
        return 
    else:
        print("Invalid choice. Exiting now.")
        return

if __name__ == "__main__":
    main()
