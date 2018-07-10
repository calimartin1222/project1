import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
def main():
    f = open("zips.csv")
    reader = csv.reader(f)
    for row in reader:
        db.execute("INSERT INTO locations (zip, city, state, lat, long, pop) VALUES (:x, :y, :z, :a, :b, :c)",
                    {"x": row[0], "y": row[1], "z": row[2], "a": row[3], "b": row[4], "c": row[5]})
        print(f"Added {row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}.")
    db.commit()
if __name__ == "__main__":
    main()