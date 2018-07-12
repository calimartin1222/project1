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

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#initialize two global variables that functions will use to store data about the user
userLoggedIn = None
currLocationID = None

@app.route("/")
def index():
    #reset global variables
    userLoggedIn = ""
    currLocationID= ""
    #render home page
    return render_template("index.html")

@app.route("/register")
def register():
    #render register page
    return render_template("reg.html")

@app.route("/register_createaccount", methods=["POST"])
def account():
    #get information from form on register page
    uname = request.form.get("uname")
    pword = request.form.get("pword")
    first = request.form.get("first")
    #set variable 'match' to all of the instances where the username and password the user
    # has just entered occurs in the database userinfo
    match = db.execute("SELECT * FROM userinfo WHERE uname = :uname AND pword = pword", {"uname": uname, "pword": pword}).fetchone()
    #checks if the username and password already exist in the database and returns an error if it does
    if match is not None:
        return render_template("error.html", message="Username already exists. Please choose another")
    #adds the info the user has provided into the database
    db.execute("INSERT INTO userinfo (first, uname, pword) VALUES (:first, :uname, :pword)",
            {"first": first, "uname": uname, "pword": pword})
    #actually runs the code above
    db.commit()
    #renders the alert page with a message telling the user they were successful in making their account
    return render_template("alert.html", message="Congrats on making your account!")

@app.route("/dashboard", methods=["POST"])
def login():
    global userLoggedIn
    #get information from form on home(login) page
    uname = request.form.get("uname")
    pword = request.form.get("pword")
    #set variable 'match' to all of the instances where the username and password the user
    # has just entered occurs in the database userinfo
    match = db.execute("SELECT * FROM userinfo WHERE uname = :uname AND pword = :pword", {"uname": uname, "pword": pword}).fetchone()
    #checks if the username and password already exist in the database and returns an error if it does not
    if match is None:
        return render_template("error.html", message="Wrong username or password")
    #sets global variable 'userLoggedIn' to the user's username so it can be referenced later
    userLoggedIn=uname
    #renders the dashboard page once the user has logged in, and sends the variable 'userLoggedIn'
    return render_template("dash.html", userLoggedIn=userLoggedIn)

@app.route("/logout")
def logout():
    global userLoggedIn
    #renders the alert page with a message telling the user they were successful in logging out of their account
    return render_template("alert.html", message = " Thank you for visiting, " + userLoggedIn + "!")
    #resets global variables
    userLoggedIn = ""
    currLocationID=""

@app.route("/search/results", methods=["POST"])
def results():
    global userLoggedIn
    #get information from search form on dashboard page
    location = request.form.get("location").upper()
    matches=[]
    #set variable 'matches' to all of the instances where the location the user has just entered occurs in the
    #database 'locations', goes through possible inputs the user may have entered, including partial and exact matches
    matches = db.execute("SELECT city, state, zip FROM locations WHERE zip LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
    if len(matches) == 0:
        matches = db.execute("SELECT city, state, zip FROM locations WHERE zip LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
    if len(matches) == 0:
        matches = db.execute("SELECT city, state, zip FROM locations WHERE city LIKE ('%' || :loc || '%');", {'loc': location}).fetchall()
    if len(matches) == 0:
        matches = db.execute("SELECT city, state, zip FROM locations WHERE city = :loc OR zip = :loc;", {"loc": location}).fetchone()
    # if, after going through all possible inputs, there are no matches in the database,
    #renders the error page telling the user that it was not a match with anything in the database
    if len(matches) == 0:
        return render_template("error.html", message="Not a valid city or zipcode")
    #creates a list with readable matches by trimming the results
    #of the psql command ('matches') and inserting those values in a new list
    matchesSend = []
    for match in matches:
        currIndex = matches.index(match)
        strMatch = str(match)
        matchesSend.append(strMatch[2:(len(strMatch))-2])
    #renders the results page, and sends the variables 'userLoggedIn' and 'matches'
    return render_template("results.html", matches=matchesSend, userLoggedIn=userLoggedIn)

@app.route("/search/weather/<string:location>", methods=["GET"])
def weather(location):
    global userLoggedIn
    global currLocationID
    #gets the city from the variable 'location'
    location = location.split("'")[0]
    #sets the variable 'currLocationID' to the id of the city the user wanted
    currLocationID =str(db.execute("SELECT id FROM locations WHERE city = :city;",{"city": location}).fetchone())

    #sets the variables 'lat' and 'longi' of location to readable strings
    #that can be put into the DarkSky API URL to get weather info
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

    #inserts the variables 'lat' and 'longi' into the variable 'url' that will be the request url for DarkSky
    url = "https://api.darksky.net/forecast/ec674134bed7c60466462a9b3adbaa66/" + lat + "," + longi

    #trimming the results of the psql command from earlier and setting that to the variable 'currLocationID'
    currLocationID = currLocationID[1:len(currLocationID)-2]
    #requests Dark Sky API weather info
    weather = requests.get(url).json()
    res = requests.get(url)
    data = res.json()
    #sets variables to be sent to weather.html as readale data from the DarkSky API
    summary = ("The Current Summary is : " + str(data['currently']['summary']))
    currTemp = ("The Current Temperature is : " + str(data['currently']['temperature']))
    dp = ("The Current Dew Point is : " + str(data['currently']['dewPoint']))
    hum = ("The Current Humidity is : " + str(100*(data['currently']['humidity']))+"%")
    #returns weather.html and sends the above variables
    return render_template("weather.html", location=location, summary=summary,
    hum = hum, currTemp = currTemp, dp = dp, userLoggedIn=userLoggedIn)

@app.route("/search/weather/check-in/", methods=["POST"])
def checkIn():
    global userLoggedIn
    global currLocationID
    #get information from form on weather page
    comment = request.form.get("comment")
    check=[]
    #set variable 'check' to all of the instances where the location the user is at
    # and their username occurs in the database 'checkins'
    check = db.execute("SELECT id FROM checkins WHERE location = :location AND username = :username;", {"location": currLocationID, "username": userLoggedIn}).fetchone()
    #checks if the username and location already exist in the database and adds them to the database if it does not
    if check is None:
        db.execute("INSERT INTO checkins (location, username, comment) VALUES (:x, :y, :z)", {"x": currLocationID, "y": userLoggedIn, "z": comment})
        db.commit()
        #renders the alert page with a message telling the user they were successful in making their comment
        return render_template("alert.html", message="Your comment " + comment + " was added!")
    else:
        #renders the error page with a message telling the user they already made a comment about that location
        return render_template("error.html", message="You've already made a comment about this location")

@app.route("/api/<string:zip>")
def zip_api(zip):
    #sets the variable 'zipId' to the id of the location with the same zip code in the locations database as the url
    zipId = str(db.execute("SELECT id FROM locations WHERE zip = :zip;", {"zip": zip}).fetchone())
    #checks if the zipcode has a corresponding id in the database, and returns an error if it does not
    if zipId is None:
        return jsonify({"error": "Invalid zipcode"}), 422
    #trims the variable 'zipId' to use to select later
    zipId = zipId[1:(len(zipId)-2)]

    #sets the variables needed for the json information to the corresponding values based on the
    #id of the location in the locations datatable stored in the variable 'zipId'
    placeName = str(db.execute("SELECT city FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    stateName = str(db.execute("SELECT state FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    lat = str(db.execute("SELECT lat FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    longi = str(db.execute("SELECT long FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    zipCode = str(db.execute("SELECT zip FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    pop = str(db.execute("SELECT pop FROM locations WHERE id = :id;", {"id": zipId}).fetchone())
    #sets the variable 'checkIns' for the json information to the number of check ins of the location
    # based on the id of the location in the checkins datatable stored in the variable 'zipId'
    checkIns = str(db.execute("SELECT COUNT(comment) FROM checkins WHERE location = :id;", {"id": zipId}).fetchall())

    #trims the variables that were just set to readable text
    placeName = placeName[2:(len(placeName)-3)]
    stateName = stateName[2:(len(stateName)-3)]
    lat = lat[2:(len(lat)-3)]
    longi = longi[2:(len(longi)-3)]
    zipCode = zipCode[2:(len(zipCode)-3)]
    pop = pop[2:(len(pop)-3)]
    checkIns = checkIns[2:(len(checkIns)-3)]
    #returns json information
    return jsonify({
            "place_name": placeName,
            "state": stateName,
            "latitude": lat,
            "longitude": longi,
            "zip": zipCode,
            "population": pop,
            "check_ins": checkIns
        })