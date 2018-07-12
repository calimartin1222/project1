import os
from flask import Flask, session, render_template, request, jsonify
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
currLocationID = None
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    userLoggedIn = ""
    currLocationID=""
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
    currLocationID=""

@app.route("/search/results", methods=["POST"])
def results():
    global userLoggedIn
    location = request.form.get("location").upper()
    matches=[]
    matches = db.execute("SELECT city, state, zip FROM locations WHERE zip LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
    if len(matches) == 0:
        matches = db.execute("SELECT city, state, zip FROM locations WHERE zip LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
    if len(matches) == 0:
        matches = db.execute("SELECT city, state, zip FROM locations WHERE city LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
    if len(matches) == 0:
        matches = db.execute("SELECT city, state, zip FROM locations WHERE city = :loc OR zip = :loc;", {"loc": location}).fetchone()
    if len(matches) == 0:
        return render_template("error.html", message="Not a valid city or zipcode")

    matchesSend = []
    for match in matches:
        currIndex = matches.index(match)
        strMatch = str(match)
        matchesSend.append(strMatch[2:(len(strMatch))-2])

    return render_template("results.html", matches=matchesSend, userLoggedIn=userLoggedIn)

@app.route("/search/weather/<string:location>", methods=["GET"])
def weather(location):
    global userLoggedIn
    global currLocationID
    location = location.split("'")[0]
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
    currLocationID =str(db.execute("SELECT id FROM locations WHERE lat = :lat AND long = :longi",
    {"lat": lat, "longi": longi}).fetchone())
    currLocationID = currLocationID[1:len(currLocationID)-2]
    weather = requests.get(url).json()
    res = requests.get(url)
    data = res.json()
    summary = ("The Summary is : " + str(data['currently']['summary']))
    currTemp = ("The Temperature is : " + str(data['currently']['temperature']))
    dp = ("The Dew Point is : " + str(data['currently']['dewPoint']))
    hum = ("Humidity is : " + str(100*(data['currently']['humidity'])))
    return render_template("weather.html", location=location, summary=summary,
    hum = hum, currTemp = currTemp, dp = dp, userLoggedIn=userLoggedIn)

@app.route("/search/weather/check-in/", methods=["POST"])
def checkIn():
    global userLoggedIn
    global currLocationID
    comment = request.form.get("comment")
    check=[]
    check = db.execute("SELECT id FROM checkins WHERE location = :location AND username = :username;", {"location": currLocationID, "username": userLoggedIn}).fetchone()
    if check is None:
        db.execute("INSERT INTO checkins (location, username, comment) VALUES (:x, :y, :z)", {"x": currLocationID, "y": userLoggedIn, "z": comment})
        db.commit()
        return render_template("alert.html", message="Your comment " + comment + " was added!")
    else:
        return render_template("error.html", message="You've already made a comment about this location")
@app.route("/api/<string:zip>")
def zip_api(zip):
    zipId = str(db.execute("SELECT id FROM locations WHERE zip = :zip;", {"zip": zip}).fetchone())
    if zipId is None:
        return jsonify({"error": "Invalid zipcode"}), 422
    zipId = zipId[1:(len(zipId)-2)]
    placeName = str(db.execute("SELECT city FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    stateName = str(db.execute("SELECT state FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    lat = str(db.execute("SELECT lat FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    longi = str(db.execute("SELECT long FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    zipCode = str(db.execute("SELECT zip FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    pop = str(db.execute("SELECT pop FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    checkIns = str(db.execute("SELECT COUNT(*) FROM checkins WHERE location = :id;", {"id": zipId}))

    placeName = placeName[2:(len(placeName)-3)]
    stateName = stateName[2:(len(stateName)-3)]
    lat = lat[2:(len(lat)-3)]
    longi = longi[2:(len(longi)-3)]
    zipCode = zipCode[2:(len(zipCode)-3)]
    pop = pop[2:(len(pop)-3)]
    checkIns = checkIns[2:(len(checkIns)-3)]

    return jsonify({
            "place_name": placeName,
            "state": stateName,
            "latitude": lat,
            "longitude": longi,
            "zip": zipCode,
            "population": pop,
            "check_ins": checkIns
        })