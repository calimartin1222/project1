import os
from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests, json

app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

userLoggedIn = None

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
    global userLoggedIn
    uname = request.form.get("uname")
    pword = request.form.get("pword")

    match = db.execute("SELECT * FROM userinfo WHERE uname = :uname AND pword = :pword", {"uname": uname, "pword": pword}).fetchone()
    if match is None:
        return render_template("error.html", message="Wrong username or password")
    userLoggedIn=uname
    return render_template("dash.html", userLoggedIn=userLoggedIn)

@app.route("/logout")
def logout():
    global userLoggedIn
    return render_template("alert.html", message = " Thank you for visiting, " + userLoggedIn + "!")
    userLoggedIn = ""

@app.route("/search/results", methods=["POST"])
def results():
    global userLoggedIn
    location = request.form.get("location").upper()
    matches=[]
    matches = db.execute("SELECT city FROM locations WHERE zip LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
    if len(matches) != 0:
        matches = db.execute("SELECT state FROM locations WHERE zip LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
        matchesZip = db.execute("SELECT zip FROM locations WHERE zip LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
    if len(matches) == 0:
        matches = db.execute("SELECT city FROM locations WHERE city LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
        if len(matches) != 0:
            stateMatches=db.execute("SELECT state FROM locations WHERE city LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
            matchesZip = db.execute("SELECT zip FROM locations WHERE city LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
    if len(matches) == 0:
        matches = db.execute("SELECT city FROM locations WHERE city = :loc OR zip = :loc;", {"loc": location}).fetchone()
        if len(matches) != 0:
            stateMatches=db.execute("SELECT state FROM locations WHERE city = :loc OR zip = :loc;", {"loc": location}).fetchone()
            matchesZip=db.execute("SELECT zip FROM locations WHERE city = :loc OR zip = :loc;", {"loc": location}).fetchone()
    if len(matches) == 0:
        return render_template("error.html", message="Not a valid city or zipcode")

    matchesZipSend = []
    for match in matchesZip:
        strMatch = str(match)
        matchesZipSend.append(strMatch[2:(len(strMatch))-3])

    matchesStateSend = []
    for match in stateMatches:
        strMatch = str(match)
        matchesStateSend.append(strMatch[2:(len(strMatch))-3])

    matchesSend = []
    for match in matches:
        currIndex = matches.index(match)
        strMatch = str(match)
        matchesSend.append(strMatch[2:(len(strMatch))-3] + ", " + matchesStateSend[currIndex] + ", " + matchesZipSend[currIndex])




    return render_template("results.html", matches=matchesSend, userLoggedIn=userLoggedIn)

@app.route("/search/weather/<string:location>", methods=["GET"])
def weather(location):
    location = location.split(",")[0]
    lat = str(db.execute("SELECT lat FROM locations WHERE city = :loc OR zip = :loc", {"loc": location}).fetchone())
    longi = str(db.execute("SELECT long FROM locations WHERE city = :loc OR zip = :loc", {"loc": location}).fetchone())
    if lat[2] == "-":
        lat = lat[2:8]
    else:
        lat = lat[2:7]
    if longi[2] == "-":
        longi = longi[2:8]
    else:
        longi = longi[2:7]
    url = "https://api.darksky.net/forecast/ec674134bed7c60466462a9b3adbaa66/" + lat + "," + longi
    weather = requests.get(url).json()
    weatherInfo = json.dumps(weather["currently"], indent = 2)
    return render_template("weather.html", location=location, weatherInfo=weatherInfo)