from flask import Flask, request
from flask_cors import CORS
import math
import heapq
import mysql.connector
import credentials

app = Flask(__name__)
CORS(app)

# ----------------------------------------------------------------------------
# Helper Function Definitions.

# This function opens the housing data file and returns an object containing
# all of the data.
def getHousingData():
    housingData = []
    cnx = mysql.connector.connect(user=credentials.mysqlUsername,
        password=credentials.mysqlPassword,
        host=credentials.mysqlEndpoint,database="cmpe272")
    cursor = cnx.cursor()
    query = ("SELECT address, city, state, zip_code, latitude, longitude, "
    "num_rooms, square_feet, price, transportation_distance, grocery_distance,"
    " parks_distance FROM cmpe272.housing")
    cursor.execute(query)
    for address, city, state, zip_code, latitude, longitude, num_rooms, square_feet,\
    price, transportation_distance, grocery_distance, parks_distance in cursor:
        house = {}
        house["address"] = address
        house["city"] = city
        house["state"] = state
        house["zipCode"] = zip_code
        house["latitude"] = latitude
        house["longitude"] = longitude
        house["numberOfRooms"] = num_rooms
        house["squareFeet"] = square_feet
        house["price"] = price
        house["distanceFromPublicTransportation"] = transportation_distance
        house["distanceFromWholeFoods"] = grocery_distance
        house["distanceFromParks"] = parks_distance
        housingData.append(house)
    cursor.close()
    cnx.close()
    return housingData

# This function returns the euclidian distance between two vectors.
def getEuclidianDistance(v1, v2):
    total = 0
    for i in range(len(v1)):
        total += (v1[i] - v2[i]) ** 2
    return math.sqrt(total)

def sortHouses(houses, checkStores, checkTransit, checkParks):
    h = []
    for i in range(len(houses)):
        currentVec = []
        idealVec = []
        if checkStores == "true":
            currentVec.append(houses[i]["distanceFromWholeFoods"])
            idealVec.append(0.01)
        if checkTransit == "true":
            currentVec.append(houses[i]["distanceFromPublicTransportation"])
            idealVec.append(0.01)
        if checkParks == "true":
            currentVec.append(houses[i]["distanceFromParks"])
            idealVec.append(0.01)
        # Calculate the similarity.
        similarity = getEuclidianDistance(currentVec, idealVec)
        # Put the house into a heap. This will make it easier to sort them
        # once they've all been given similarity scores. The way heapq works
        # with tuples is it will compare the first item in the tuple, then
        # the second and so on. We pass in 'i' to guarantee that it won't try
        # to compare the houses because that would result in a type error.
        heapq.heappush(h, (similarity, i, houses[i]))
    sortedHouses = []
    # Pop items from the heap until it is empty and append them to the list.
    while len(h) > 0:
        sortedHouses.append(heapq.heappop(h)[2])
    return sortedHouses

# ----------------------------------------------------------------------------
# Endpoint Definitions.

# This endpoint is just here to let people know that it's running.
@app.route("/")
def hello():
    return "Hello World!"

# This endpoint will return all of the housing data.
@app.route("/houses")
def houses():
    housingData = getHousingData()
    # Pull out the query parameters.
    checkStores = request.args.get("checkStores")
    checkTransit = request.args.get("checkTransit")
    checkParks = request.args.get("checkParks")
    # Sort the data based on our query parameters.
    sortedData = sortHouses(housingData, checkStores, checkTransit, checkParks)
    # Return a new object containing the sorted data.
    retVal = {}
    retVal["housingData"] = sortedData
    return retVal

# This starts the server and listens for requests.
# If you are running this locally you can open your browser to "localhost:5000/"
if __name__ == '__main__':
    app.run(debug=True)