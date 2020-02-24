import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv


engine = create_engine("postgres://swgfzukjvgmsew:c987efcfdb9af994e0c497ccb91101b119abe8a91c65d1a4ccc15bd21510c1c9@ec2-184-72-236-3.compute-1.amazonaws.com:5432/d6cbp8fk0b634n")
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
