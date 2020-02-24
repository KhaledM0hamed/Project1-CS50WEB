import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv


engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

f = open("books.csv")
reader = csv.reader(f)

# for isbn,title,author,year in reader:  # loop gives each column a name
#     db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn,:title,:author,:year)",
#                {"isbn": isbn,
#                 "title": title,
#                 "author": author,
#                 "year": year})  # substitute values from CSV line int
# print(
#     f"Added book from {isbn} to {title} lasting {author} minutes.")
db.execute("INSERT INTO master (username, email, password) VALUES ('khaled', 'dsadsdas@ddd.com', '1611')")
db.commit()  # transactions are assumed, so close the transaction finished
