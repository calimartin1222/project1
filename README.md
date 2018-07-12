# Project 1

Web Programming with Python and JavaScript

Short Description:
This website is a search-based weather information provider that allows users to register
an account and log in and leave comments("check ins") and gives information based on
zipcode when a user makes a GET request and goes to root/api/ZIPCODE

File Descriptions:
index.html - home page that includes a login form
reg.html - register page that includes a form for the user to register for an account
dash.html - a "dashboard" that the user sees when they first login in, includes search for locations
results.html - displays all possible matches to a user's search input for the weather of a location
weather.html - displays the weather information for the user's chosen location, and the ability to check in
alert.html - displays when the user should be notified about something (i.e. they successfully made an account)
error.html - displays when the user should be notified about something that went wrong (i.e. location doesn't exist)
template.html - the template all the html files extend, includes header and links to stylesheets

application.py - all the functions for when a user submits information through a
form or goes to a certain url of the website, contains SQL and Flask
import.py - imported the information in zips.csv into the locations database
zips.csv - list of thousands of locations with information about them
requirements.txt - list of python packages that need to be installed in order to be able to run the website

To install packages in requirements.txt:
$pip3 install -r requirements.txt