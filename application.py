import os
from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests, json

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


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("reg.html")

@app.route("/register_createaccount", methods=["POST"])
def account():
    uname = request.form.get("uname")
    pword = request.form.get("pword")
    first = request.form.get("first")
    match = db.execute("SELECT * FROM userinfo WHERE uname = :uname AND pword = pword", {"uname": uname, "pword": pword}).fetchone()
    if match is not None:
        return render_template("error.html", message="Username already exists. Please choose another")
    db.execute("INSERT INTO userinfo (first, uname, pword) VALUES (:first, :uname, :pword)",
            {"first": first, "uname": uname, "pword": pword})

    db.commit()
    return render_template("alert.html", message="Congrats on making your account!")

@app.route("/dashboard", methods=["POST"])
def login():
    uname = request.form.get("uname")
    pword = request.form.get("pword")

    match = db.execute("SELECT * FROM userinfo WHERE uname = :uname AND pword = pword", {"uname": uname, "pword": pword}).fetchone()
    if match is None:
        return render_template("error.html", message="Wrong username or password")

    return render_template("dash.html", user=uname)

@app.route("/logout")
def logout():
    return render_template("logout.html")


@app.route("/weather", methods=["POST"])
def weather():
    location = request.form.get("location")
    match = db.execute("SELECT id FROM locations WHERE city = :loc OR zip = :loc", {"loc": location}).fetchall()
    if match is None:
        return render_template("error.html", message="Not a valid city or zipcode")
    lat = str(db.execute("SELECT lat FROM locations WHERE city = :loc OR zip = :loc", {"loc": location}).fetchone())
    longi = str(db.execute("SELECT long FROM locations WHERE city = :loc OR zip = :loc", {"loc": location}).fetchone())
    url = "https://api.darksky.net/forecast/ec674134bed7c60466462a9b3adbaa66/" + lat[2:6] + "," + longi[2:6]
    #weather = requests.get(url).json()
    weatherInfo = url#json.dumps(weather["currently"], indent = 2)
    #weather = requests.get("https://api.darksky.net/forecast/ec674134bed7c60466462a9b3adbaa66/42.37,-71.11").json()
    #weatherInfo = (json.dumps(weather["currently"], indent = 2))

    return render_template("weather.html", location=location, weatherInfo=weatherInfo)